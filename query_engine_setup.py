from typing import List, Generator
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.postprocessor import (
    SentenceTransformerRerank,
    MetadataReplacementPostProcessor,
    SimilarityPostprocessor,
    LongContextReorder,
)
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.llms import LLM
from llama_index.core.indices import VectorStoreIndex

from utility import get_config_value

import time
import json
import logging

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)


class QueryEngineSetup:
    def __init__(self, llm: LLM, index: VectorStoreIndex = None):
        self.llm = llm
        self.index = index
        self.config = self._load_configuration()
        self.node_postprocessors = self._setup_node_postprocessors()
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

    def _setup_node_postprocessors(self) -> List:
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

        print(f"the length of the node_postprocessors is {len(node_postprocessors)}")
        return node_postprocessors

    def _configure_query_engine(self, vsi: VectorStoreIndex = None) -> BaseQueryEngine:

        if not (self.index or vsi):
            raise ValueError("Index is not provided")

        _index = vsi if vsi else self.index

        if self.config["ENABLE_QUERY_PIPELINE"]:
            print("Using query pipeline")
            retriever = VectorIndexRetriever(
                index=_index,
                similarity_top_k=self.config["SIMILARITY_TOP_K"],
                verbose=True
            )
            response_synthesizer = get_response_synthesizer(
                streaming=True,
                llm=self.llm,
                use_async=self.config["ASYNC_INDEXING"],
                verbose=True
            )
            return RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=response_synthesizer,
                node_postprocessors=self.node_postprocessors,
            )
        else:
            print("Using index directly")
            return _index.as_query_engine(
                similarity_top_k=self.config["SIMILARITY_TOP_K"],
                streaming=True,
                node_postprocessors=self.node_postprocessors,
                llm=self.llm,
                use_async=self.config["ASYNC_INDEXING"], # todo handle async indexing
            )

    # todo handle async indexing
    def generate_answer(self, query: str, vsi: VectorStoreIndex = None) -> Generator[str, None, None]:
        if vsi is not None:
            _query_engine = self._configure_query_engine(vsi)
        else:
            _query_engine = self.query_engine

        if _query_engine is None:
            raise ValueError("Query engine is not initialized, please provide a valid index")

        try:
            now = time.time()
            response = _query_engine.query(query)
            for text in response.response_gen:
                yield f"data: {json.dumps({'text': text})}\n\n"
            yield f"data: {json.dumps({'time_taken': round(time.time() - now, 2), 'done': True})}\n\n"
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': False})}\n\n"
