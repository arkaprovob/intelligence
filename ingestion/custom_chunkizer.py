import re
from typing import List, Sequence, Any

from llama_index.core.bridge.pydantic import Field
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import Document, NodeRelationship, RelatedNodeInfo, BaseNode


class ChunkNodeParser(NodeParser):
    window_size: int = Field(default=3, description="The size of the context window")

    def _parse_nodes(
            self,
            nodes: Sequence[BaseNode],
            show_progress: bool = False,
            **kwargs: Any,
    ) -> List[BaseNode]:
        all_nodes = []
        for original_node in nodes:
            chunks, metadata = self._split_chunks_and_extract_metadata(original_node.get_content())
            doc_nodes = []
            for i, chunk in enumerate(chunks):
                node = Document(
                    text=chunk,
                    metadata={**original_node.metadata, **metadata, "chunk_id": i},
                    relationships={
                        NodeRelationship.SOURCE: RelatedNodeInfo(node_id=original_node.node_id)
                    },
                    id_=self.id_func(i, original_node)
                )
                doc_nodes.append(node)

            # Add window information
            for i, node in enumerate(doc_nodes):
                window_start = max(0, i - self.window_size)
                window_end = min(len(doc_nodes), i + self.window_size + 1)
                window_text = " ".join([n.get_content() for n in doc_nodes[window_start:window_end]])
                node.metadata["window"] = window_text

            all_nodes.extend(doc_nodes)
        return all_nodes

    @classmethod
    def _split_chunks_and_extract_metadata(self, text: str) -> tuple[List[str], dict]:
        metadata_match = re.search(r'<meta-data>(.*?)</meta-data>', text, re.DOTALL)
        metadata = {}
        if metadata_match:
            metadata_str = metadata_match.group(1)
            metadata = eval(metadata_str)  # Convert string to dictionary

        # Remove metadata from text
        text = re.sub(r'<meta-data>.*?</meta-data>', '', text, flags=re.DOTALL)

        # Split text into chunks
        chunks = re.findall(r'<chunk>(.*?)</chunk>', text, re.DOTALL)
        chunks = [chunk.strip() for chunk in chunks]

        return chunks, metadata
