from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor, SummaryExtractor
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.schema import MetadataMode
from llama_index.vector_stores.qdrant import QdrantVectorStore

from llama_index.core import Settings

import logging

from utility import get_config_value

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class IndexProvider:
    def __init__(self, documents, client, collection_name, embed_model, llm, transform=False,
                 use_node_parser=False):
        Settings.llm = llm
        Settings.chunk_size = get_config_value("CHUNK_SIZE")
        Settings.chunk_overlap = get_config_value("CHUNK_OVERLAP")
        try:
            self.vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

            # todo explore TokenTextSplitter
            node_parser = SentenceWindowNodeParser(
                window_size=3,
                window_metadata_key="window",
                original_text_metadata_key="original_text"
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
                orig_nodes = node_parser.get_nodes_from_documents(documents)
                self.index = VectorStoreIndex(
                    orig_nodes,
                    storage_context=self.storage_context,
                    embed_model=embed_model,
                    transformations=extractors,
                    show_progress=True
                )
            else:
                logger.info("Using documents")
                print("Using documents")
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    storage_context=self.storage_context,
                    embed_model=embed_model,
                    transformations=extractors,
                    show_progress=True)

        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)

    def get_index(self):
        return self.index
