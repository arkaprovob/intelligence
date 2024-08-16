import asyncio
from typing import List,AsyncGenerator
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.postprocessor import (
    SentenceTransformerRerank,
    MetadataReplacementPostProcessor,
    SimilarityPostprocessor,
    LongContextReorder,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.llms import LLM
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from ingestion import LowercaseNodePostprocessor
from llm import LLMPool
from prompt import PromptProvider
from qna import get_synthesizer_instance


import time
import json
import logging

from util.utility import get_config_value

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)


async def _stream_response(response):
    try:
        for text in response.response_gen:
            yield text
            await asyncio.sleep(0)  # Allow other coroutines to run
    except Exception as e:
        logging.error(f"Error streaming response: {str(e)}")
        yield f"Error streaming response: {str(e)}"


class QueryEngineSetup:
    def __init__(self, llm_pool: LLMPool, index: VectorStoreIndex = None, include_lowercase_postprocessor: bool = True):
        self.llm_pool = llm_pool
        self.index = index
        self.config = self._load_configuration()
        self.node_postprocessors = self._setup_node_postprocessors(include_lowercase_postprocessor)
        if self.index is None:
            self.query_engine = None
        else:
            self.query_engine: BaseQueryEngine = self._configure_query_engine()

    @classmethod
    def _load_configuration(cls) -> dict:
        return {
            "ENABLE_QUERY_PIPELINE": get_config_value("ENABLE_QUERY_PIPELINE"),
            "USE_NODE_PARSER": get_config_value("USE_NODE_PARSER"),
            "ASYNC_INDEXING": get_config_value("ASYNC_INDEXING"),
            "SIMILARITY_TOP_K": get_config_value("SIMILARITY_TOP_K"),
            "RERANKING_MODEL": get_config_value("RERANKING_MODEL"),
            "RERANKING_TOP_N": get_config_value("RERANKING_TOP_N"),
            "SIMILARITY_CUTOFF": get_config_value("SIMILARITY_CUTOFF"),
        }

    def _setup_node_postprocessors(self, lowercase_postprocessor) -> List:
        metadata_replacement = MetadataReplacementPostProcessor(target_metadata_key="window")
        rerank = SentenceTransformerRerank(
            model=self.config["RERANKING_MODEL"],
            top_n=self.config["RERANKING_TOP_N"]
        )
        similarity = SimilarityPostprocessor(similarity_cutoff=self.config["SIMILARITY_CUTOFF"])
        long_context_reorder = LongContextReorder()

        # If both 'ENABLE_QUERY_PIPELINE' and 'USE_NODE_PARSER' are True,
        # add SimilarityPostprocessor, metadata_replacement, and rerank to the list
        if self.config["ENABLE_QUERY_PIPELINE"] and self.config["USE_NODE_PARSER"]:
            node_postprocessors = [similarity, metadata_replacement, rerank, long_context_reorder]

        # If 'ENABLE_QUERY_PIPELINE' is True but 'USE_NODE_PARSER' is False,
        # add only SimilarityPostprocessor and rerank to the list
        elif self.config["ENABLE_QUERY_PIPELINE"] and not self.config["USE_NODE_PARSER"]:
            node_postprocessors = [similarity, rerank, long_context_reorder]

        # If both 'ENABLE_QUERY_PIPELINE' and 'USE_NODE_PARSER' are False,
        # add only rerank to the list
        else:
            node_postprocessors = [rerank, long_context_reorder]

        if lowercase_postprocessor:
            print("Adding LowercaseNodePostprocessor")
            node_postprocessors.append(LowercaseNodePostprocessor())

        print(f"the length of the node_postprocessors is {len(node_postprocessors)}")
        return node_postprocessors

    def _configure_query_engine(self, vsi: VectorStoreIndex = None, llm: LLM = None) -> BaseQueryEngine:

        if not (self.index or vsi):
            raise ValueError("Index is not provided")
        if llm is None:
            raise ValueError("LLM is not provided")

        lm = llm if llm else None

        _index = vsi if vsi else self.index

        if self.config["ENABLE_QUERY_PIPELINE"]:
            print("Using query pipeline")
            retriever = VectorIndexRetriever(
                index=_index,
                similarity_top_k=self.config["SIMILARITY_TOP_K"],
                verbose=True,
                sparse_top_k=12,
                vector_store_query_mode=VectorStoreQueryMode.HYBRID
            )
            return RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=get_synthesizer_instance(llm=lm),
                node_postprocessors=self.node_postprocessors
            )
        else:
            print("Using index directly")
            return _index.as_query_engine(
                similarity_top_k=self.config["SIMILARITY_TOP_K"],
                streaming=True,
                node_postprocessors=self.node_postprocessors,
                llm=lm,
                sparse_top_k=12,
                vector_store_query_mode="hybrid",
                use_async=self.config["ASYNC_INDEXING"],  # todo handle async indexing
            )

    # todo handle async indexing
    async def generate_answer(self, query: str, vsi: VectorStoreIndex = None) -> AsyncGenerator[str, None]:
        if vsi is not None:
            _index = vsi
        elif self.index is not None:
            _index = self.index
        else:
            raise ValueError("No valid index provided")

        llm_instance = None
        try:
            llm_instance, was_queued = await self.llm_pool.get_instance()

            if was_queued:
                yield f"data: {json.dumps({'queued': True})}\n\n"

            _query_engine = self._configure_query_engine(_index, llm_instance.llm.get_llm())
            _query_engine.update_prompts({
                "response_synthesizer:text_qa_template": PromptProvider().get_prompt()
                .partial_format(tone_name="senior support engineer")})

            # print(_query_engine.get_prompts())
            now = time.time()
            response = _query_engine.query(query)
            async for text in _stream_response(response):
                # todo try stopping logic here if text contains any token from stopping sequence break the flow
                yield f"data: {json.dumps({'text': text})}\n\n"
            yield f"data: {json.dumps({'time_taken': round(time.time() - now, 2), 'done': True, 'source': 'llm'})}\n\n"
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            logging.error("Full stack trace:", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': False})}\n\n"
        finally:
            if llm_instance:
                await self.llm_pool.release_instance(llm_instance)
