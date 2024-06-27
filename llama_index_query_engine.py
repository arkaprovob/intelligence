from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.postprocessor import SentenceTransformerRerank, \
    MetadataReplacementPostProcessor
import time
import json
import logging

from utility import get_config_value

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)


class QueryEngineProvider:
    def __init__(self, llm, index):
        postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
        rerank = SentenceTransformerRerank(model=get_config_value("RERANKING_MODEL"), top_n=3)

        if get_config_value("USE_NODE_PARSER"):
            node_postprocessors = [postproc, rerank]
        else:
            node_postprocessors = [rerank]
        print(f"the length of the node_postprocessors is {len(node_postprocessors)}")
        # todo handle async indexing
        async_indexing = get_config_value("ASYNC_INDEXING")
        self.query_engine: BaseQueryEngine = index.as_query_engine(similarity_top_k=10, streaming=True,
                                                                   node_postprocessors=node_postprocessors,
                                                                   llm=llm, use_async=async_indexing)

    # todo handle async indexing
    def generate_answer(self, query):
        try:
            now = time.time()
            # print(self.query_engine.get_prompts())
            response = self.query_engine.query(query)
            for text in response.response_gen:
                yield f"data: {json.dumps({'text': text})}\n\n"
            yield f"data: {json.dumps({'time_taken': round(time.time() - now, 2), 'done': True})}\n\n"
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': False})}\n\n"
