import os
from typing import List

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.readers.base import BaseReader
import re
import hashlib

from util.utility import get_config_value


class DocsBotExtensionFileReader(BaseReader):
    def load_data(self, file, extra_info=None) -> List[Document]:
        documents: List[Document] = []
        with open(file, "rb") as f:  # Open in binary mode
            content = f.read()
            file_hash = hashlib.md5(content).hexdigest()
            text = content.decode('utf-8')  # Decode bytes to string

        texts, meta = self._split_chunks_and_extract_metadata(text)
        # load_data returns a list of Document objects

        meta['file_name'] = os.path.basename(file)
        meta['from_file'] = os.path.basename(file)
        meta['parent_file_hash'] = file_hash

        for record in texts:
            content_hash = hashlib.md5(record.encode('utf-8')).hexdigest()
            chunk_meta = meta.copy()
            chunk_meta['content_hash'] = content_hash
            _document = Document(text=record, extra_info=chunk_meta)

            for key in ['excluded_llm_metadata_keys', 'excluded_embed_metadata_keys']:
                setattr(_document, key, getattr(_document, key) + ["content_hash", "source"])

            documents.append(_document)

        return documents

    @classmethod
    def _split_chunks_and_extract_metadata(cls, text: str) -> tuple[List[str], dict]:
        metadata_match = re.search(r'<meta-data>(.*?)</meta-data>', text, re.DOTALL)
        metadata = {}
        if metadata_match:
            metadata_str = metadata_match.group(1)
            metadata = eval(metadata_str)  # Convert string to dictionary

        # Remove metadata from text
        text = re.sub(r'<meta-data>.*?</meta-data>', '', text, flags=re.DOTALL)

        # Split text into chunks
        chunks = re.findall(r'<chunk>(.*?)</chunk>', text, re.DOTALL)
        chunks = [chunk.strip().lower() for chunk in chunks]

        return chunks, metadata


def read_docs_bot_file(file_loc: str = None) -> List[Document]:
    if file_loc is None:
        input_dir = get_config_value("SDR_DIR")
        file_extractor = {".docsbot": DocsBotExtensionFileReader()}
        reader = SimpleDirectoryReader(input_dir=input_dir, file_extractor=file_extractor)
        return reader.load_data()
    reader = SimpleDirectoryReader(
        input_files=[file_loc], file_extractor={".docsbot": DocsBotExtensionFileReader()}
    )
    return reader.load_data()
