import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor, SummaryExtractor
from llama_index.core.llms import LLM
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter
from llama_index.core.schema import MetadataMode

from data_store_engine import DataStore
from utility import get_config_value
from llama_index.embeddings.fastembed import FastEmbedEmbedding

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Ingestion:
    def __init__(self, llm: LLM = None, embedding: BaseEmbedding = None, transform: bool = False):

        self.config = self._load_configuration()
        self.embedding = self._get_embedding(embedding)
        self.llm = llm

        #  1. todo add more parser and make them configurable, preferably through api

        # 2. todo explore TokenTextSplitter
        self.node_parser = SentenceWindowNodeParser(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text"
        )
        # 3. todo add support for visual chunk size and overlap interface
        self.text_splitter = SentenceSplitter(
            chunk_size=self.config["CHUNK_SIZE"],
            chunk_overlap=self.config["CHUNK_OVERLAP"]
        )

        self.extractors = self._load_extractors(transform)

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

    def _load_extractors(self, transform: bool):
        # plays an important role in the extraction of the metadata from the nodes
        # 4. todo use a separate llm for these extractors with proper context
        if not transform or self.llm is None:
            return []
        else:
            return [
                TitleExtractor(nodes=5, llm=self.llm),
                SummaryExtractor(summaries=["prev", "self", "next"], llm=self.llm),
                QuestionsAnsweredExtractor(questions=3, llm=self.llm,
                                           metadata_mode=MetadataMode.EMBED),
            ]

    def ingest_documents(self, bucket: DataStore, documents, use_node_parser: bool = True,
                         async_support: bool = False, show_progress: bool = True):
        if use_node_parser:
            logger.info("Using node parser")
            print("Using node parser")
            nodes = self.node_parser.get_nodes_from_documents(documents)
        else:
            logger.info("Using documents")
            print("Using documents")
            # Settings.text_splitter = self.text_splitter
            nodes = self.text_splitter.get_nodes_from_documents(documents)
        return VectorStoreIndex(  # This returns an index after ingesting the documents
            nodes=nodes,
            storage_context=bucket.get_storage_context(),
            embed_model=self.embedding,
            transformations=self.extractors,
            use_async=async_support,  # 5. todo fix the async_support during ingestion
            show_progress=show_progress)


