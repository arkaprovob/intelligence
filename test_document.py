# Extra contents not for shipping

from typing import Optional, List, Dict, Any
from llama_index.core import Settings, Document
from llama_index.core.node_parser import SentenceWindowNodeParser
from pydantic import BaseModel


class TextIngestionRequest(BaseModel):
    text: str
    metadata: Dict[str, Any] = None


def ingest_text(docs: List[TextIngestionRequest]):
    # Validate the request: make sure text and metadata fields are not None
    for doc in docs:
        if doc.text is None:
            raise ValueError("Text field cannot be None")
        if doc.metadata is None:
            doc.metadata = {}

    # Create a list of Document objects
    documents = [Document(text=entry.text, metadata=entry.metadata) for entry in docs]

    # Iterate over the list and print each document
    for document in documents:
        print(f"Document Text: {document.text}")
        print(f"Document Metadata: {document.metadata}")
        print(f"Excluded LLM Metadata Keys: {document.excluded_llm_metadata_keys}")
        print("---")

    return documents


text_ingestion_request_mock = TextIngestionRequest(text="Hello this is a text",metadata={"custom_meta":"metadata"})
text_ingestion_request_mock2 = TextIngestionRequest(text="Hello this is another text",metadata={"custom_meta":"metadata2"})
docs = ingest_text([text_ingestion_request_mock,text_ingestion_request_mock2])


print("=" * 50)


node_parser = SentenceWindowNodeParser(
            window_size=5,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
nodes = node_parser.get_nodes_from_documents(docs)

for node in nodes:
    print(f"Node Text: {node.text}")
    print(f"Node metadata: {node.metadata}")
    print(f"Excluded LLM Metadata Keys: {node.excluded_llm_metadata_keys}")
    print("---")