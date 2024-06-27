from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor, SummaryExtractor
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter
from llama_index.core.schema import MetadataMode
from llama_index.vector_stores.qdrant import QdrantVectorStore
import nest_asyncio

from llama_index.core import Settings

import logging

import qdrant_client
from qdrant_client import QdrantClient

from utility import get_config_value

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Ingestion:
    def __init__(self, documents, collection_name, embed_model, llm, transform=False,
                 use_node_parser=False):
        Settings.llm = llm
        Settings.chunk_size = get_config_value("CHUNK_SIZE")
        Settings.chunk_overlap = get_config_value("CHUNK_OVERLAP")
        async_indexing = get_config_value("ASYNC_INDEXING")
        try:
            self.use_async = False

            if async_indexing:
                nest_asyncio.apply()
                client = qdrant_client.AsyncQdrantClient(host=get_config_value("QDRANT_HOST"),
                                                         port=get_config_value("QDRANT_PORT"))
                self.vector_store = QdrantVectorStore(client=client,
                                                      collection_name=collection_name,
                                                      prefer_grpc=True, )
                self.use_async = True
            else:
                client = QdrantClient(host=get_config_value("QDRANT_HOST"),
                                      port=get_config_value("QDRANT_PORT"))
                self.vector_store = QdrantVectorStore(client=client,
                                                      collection_name=collection_name)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

            # todo explore TokenTextSplitter
            node_parser = SentenceWindowNodeParser(
                window_size=3,
                window_metadata_key="window",
                original_text_metadata_key="original_text"
            )

            text_splitter = SentenceSplitter(
                chunk_size=get_config_value("CHUNK_SIZE"),
                chunk_overlap=get_config_value("CHUNK_OVERLAP")
            )

            # plays an important role in the extraction of the metadata from the nodes
            # todo use a separate llm for these extractors with proper context
            if transform:
                extractors = [
                    TitleExtractor(nodes=5, llm=llm),
                    SummaryExtractor(summaries=["prev", "self", "next"], llm=llm),
                    QuestionsAnsweredExtractor(questions=3, llm=llm,
                                               metadata_mode=MetadataMode.EMBED),
                ]
            else:
                extractors = []

            if use_node_parser:
                logger.info("Using node parser")
                print("Using node parser")
                nodes = node_parser.get_nodes_from_documents(documents)
            else:
                logger.info("Using documents")
                print("Using documents")
                Settings.text_splitter = text_splitter
                nodes = text_splitter.get_nodes_from_documents(documents)

            # todo Trigger this when there is a new data and trigger the next when the index already exists and
            #  searchable; make it a part of pipeline
            # self.index = VectorStoreIndex(
            #     nodes=nodes,
            #     storage_context=self.storage_context,
            #     embed_model=embed_model,
            #     transformations=extractors,
            #     use_async=self.use_async,
            #     show_progress=True)

            self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)

    def get_index(self):
        return self.index
