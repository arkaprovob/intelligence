from llama_index.core import Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core.postprocessor import SentenceTransformerRerank
import time
import json
import logging

from utility import get_config_value

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)


class QueryEngineProvider:
    def __init__(self, model_url, system_prompt, completion_to_prompt, stopping_ids, index,
                 model_path=None):

        if model_path is not None:
            model_url = None

        self.llm = LlamaCPP(
            model_url=model_url,
            model_path=model_path,
            temperature=get_config_value("LLM_TEMPERATURE"),
            max_new_tokens=get_config_value("LLM_MAX_TOKEN_GENERATION"),
            context_window=get_config_value("LLM_CONTEXT_WINDOW"),
            generate_kwargs={"stop": stopping_ids},
            model_kwargs={"n_gpu_layers": get_config_value("GPU_LAYER")},
            system_prompt=system_prompt,
            completion_to_prompt=completion_to_prompt,
            verbose=True
        )
        Settings.llm = self.llm
        Settings.chunk_size = get_config_value("CHUNK_SIZE")
        Settings.chunk_overlap = get_config_value("CHUNK_OVERLAP")
        rerank = SentenceTransformerRerank(model=get_config_value("RERANKING_MODEL"), top_n=3)
        self.query_engine = index.as_query_engine(similarity_top_k=10, streaming=True,
                                                  node_postprocessors=[
                                                      rerank],
                                                  llm=self.llm)

    def generate_answer(self, query):
        try:
            now = time.time()
            response = self.query_engine.query(query)
            for text in response.response_gen:
                yield f"data: {json.dumps({'text': text})}\n\n"
            yield f"data: {json.dumps({'time_taken': round(time.time() - now, 2), 'done': True})}\n\n"
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            yield f"data: {json.dumps({'error': str(e),'done': False})}\n\n"
