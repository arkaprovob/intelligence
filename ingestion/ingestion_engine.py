import logging
from typing import Sequence

from llama_index.core import VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor, SummaryExtractor
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter
from llama_index.core.schema import MetadataMode, Document
from llama_index.embeddings.fastembed import FastEmbedEmbedding

from llm import LLMPool
from util import get_config_value
from vector_store import DataStore

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Ingestion:
    def __init__(self, llm_pool: LLMPool = None, embedding: BaseEmbedding = None):

        self.config = self._load_configuration()
        self.embedding = self._get_embedding(embedding)
        self.llm_pool = llm_pool

        #  1. todo add more parser and make them configurable, preferably through api

        # 2. todo explore TokenTextSplitter
        self.node_parser = SentenceWindowNodeParser(
            window_size=5,
            window_metadata_key="window",
            original_text_metadata_key="original_text"
        )
        # 3. todo add support for visual chunk size and overlap interface
        self.text_splitter = SentenceSplitter(
            chunk_size=self.config["CHUNK_SIZE"],
            chunk_overlap=self.config["CHUNK_OVERLAP"]
        )

    @classmethod
    def _load_configuration(cls) -> dict:
        return {
            "CHUNK_SIZE": get_config_value("CHUNK_SIZE"),
            "CHUNK_OVERLAP": get_config_value("CHUNK_OVERLAP"),
            "ASYNC_INDEXING": get_config_value("ASYNC_INDEXING"),
            "EMBEDDING_MODEL": get_config_value("EMBEDDING_MODEL"),
            "CACHE_DIR": get_config_value("CACHE_DIR")
        }

    def _get_embedding(self, embedding):
        if embedding is None:
            return self._default_embedding()
        return embedding

    def _default_embedding(self):
        return FastEmbedEmbedding(model_name=self.config["EMBEDDING_MODEL"],
                                  cache_dir=self.config["CACHE_DIR"])

    async def _load_extractors(self, transform: bool):
        # plays an important role in the extraction of the metadata from the nodes
        # 4. todo use a separate llm for these extractors with proper context
        extractors = []
        llm_instance = None
        if not transform or self.llm_pool is None:
            return extractors
        else:

            try:
                llm_instance, was_queued = await self.llm_pool.get_instance()
                if was_queued:
                    print("No llm instance available, request queued")
                extractors = [
                    TitleExtractor(nodes=5, llm=llm_instance.llm.get_llm()),
                    SummaryExtractor(summaries=["prev", "self", "next"], llm=llm_instance.llm.get_llm()),
                    QuestionsAnsweredExtractor(questions=3, llm=llm_instance.llm.get_llm(),
                                               metadata_mode=MetadataMode.EMBED),
                ]

            except Exception as e:
                logging.error(f"Error processing query: {str(e)}")
                logger.error(f"Error loading extractors: {str(e)}")
            finally:
                if llm_instance:
                    await self.llm_pool.release_instance(llm_instance)
                return extractors

    async def ingest_documents(self, bucket: DataStore, documents:Sequence[Document], use_node_parser: bool = True,
                               async_support: bool = False, show_progress: bool = True, transform: bool = False):
        if use_node_parser:
            logger.info("Using node parser")
            print("Using node parser")
            nodes = self.node_parser.get_nodes_from_documents(documents)
        else:
            logger.info("Using documents")
            print("Using documents")
            # Settings.text_splitter = self.text_splitter
            nodes = self.text_splitter.get_nodes_from_documents(documents)

        # Await the extractors
        extractors = await self._load_extractors(transform=transform)

        return VectorStoreIndex(  # This returns an index after ingesting the documents
            nodes=nodes,
            storage_context=bucket.get_storage_context(),
            embed_model=self.embedding,
            transformations=extractors,
            use_async=async_support,  # 5. todo fix the async_support during ingestion
            show_progress=show_progress)
