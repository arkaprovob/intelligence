"""
Ingestion: includes a custom node parser .
"""
from .custom_chunkizer import ChunkNodeParser
from .docsbot_docu_builder import DocsBotExtensionFileReader,read_docs_bot_file

__version__ = "0.1.0"
__all__ = ['ChunkNodeParser','DocsBotExtensionFileReader','read_docs_bot_file']