from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.fastembed import FastEmbedEmbedding

reader = SimpleDirectoryReader(
    input_files=["/Users/arbhatta/Documents/2024/instructlab-fusion/intelligence/backup_docs/spaship.txt"]
)

embedding = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5")

documents = reader.load_data()

splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embedding, include_prev_next_rel=True
)

nodes = splitter.get_nodes_from_documents(documents)

for node in nodes:
    print(node.get_content())
    print(node.metadata)
    print("-----------------------------------------------")

# parser = MarkdownNodeParser()
# md_nodes = parser.get_nodes_from_documents(documents)
# print(len(md_nodes))
# for md_node in md_nodes:
#     print(md_node.get_content())
#     print(md_node.metadata)
#     print("-----------------------------------------------")
