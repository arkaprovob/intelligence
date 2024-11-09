# Extra contents not for shipping
from typing import Callable, List

from fastembed import TextEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import (
     SentenceSplitter,
     SemanticSplitterNodeParser, SentenceWindowNodeParser,
)
from llama_index.embeddings.fastembed import FastEmbedEmbedding


documents = SimpleDirectoryReader(input_files=["/Users/arbhatta/Documents/2024/instructlab-fusion/intelligence/static/paul_graham_essay.txt"]).load_data()

print(f"the length od the document is {len(documents)}")
sentence_splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=256
        )
try:
    embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5",cache_dir=None)
except:
    print("supported models are as follows")
    for entry in TextEmbedding.list_supported_models():
        print(entry)


splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model, #sentence_splitter=splitter
)


def split_by_sentence_splitter() -> Callable[[str], List[str]]:

    splitter = SentenceSplitter(
        chunk_size=256,
        chunk_overlap=0
    )

    def split(text: str) -> List[str]:
        # The SentenceSplitter's split_text method returns a list of strings
        # which are already sentences, so we don't need to do additional processing
        return splitter.split_text(text)

    return split

node_parser = SentenceWindowNodeParser(
            window_size=5,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
            sentence_splitter = split_by_sentence_splitter()
        )
nodes = node_parser.get_nodes_from_documents(documents)
# nodes = splitter.build_semantic_nodes_from_documents(documents)

print(f" size of the regular nodes are as follows {len(nodes)}")
#print(f"size of the semantic node is {len(semantic_nodes)}")
for node in nodes:
     print(node.get_content())
     # print("----------------------------")
     # print(node.metadata.get("window"))
     print(" == end of Node == ")