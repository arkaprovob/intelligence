from llama_index.core.node_parser import SentenceWindowNodeParser

from docsbot_docu_builder import read_docs_bot_file

file: str = ("/Users/arbhatta/Documents/2024/instructlab-fusion/intelligence/test_resources"
             "/StreamliningDeploymentWithGitBroker.docsbot")

docs = read_docs_bot_file(file)
node_parser = SentenceWindowNodeParser(
    window_size=5,
    window_metadata_key="window",
    original_text_metadata_key="original_text"
)

nodes = node_parser.get_nodes_from_documents(docs)

for node in nodes:
    print(f"node content is {node}")
    print(f" window content : {node.metadata['window']}")
    print("\n")
