from llama_index.core import Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core.postprocessor import SentenceTransformerRerank
import time
import json


class QueryEngineProvider:
    def __init__(self, model_url, system_prompt, completion_to_prompt, stopping_ids, index,
                 embed_model):
        self.llm = LlamaCPP(
            model_url=model_url,
            model_path=None,
            temperature=0.1,
            max_new_tokens=256,
            context_window=8192,
            generate_kwargs={"stop": stopping_ids},
            model_kwargs={"n_gpu_layers": -1},
            system_prompt=system_prompt,
            completion_to_prompt=completion_to_prompt,
            verbose=True
        )
        Settings.llm = self.llm
        Settings.chunk_size = 512
        rerank = SentenceTransformerRerank(model="cross-encoder/ms-marco-MiniLM-L-2-v2", top_n=3)
        self.query_engine = index.as_query_engine(similarity_top_k=10, streaming=True,
                                                  node_postprocessors=[
                                                      rerank],
                                                  llm=self.llm)

    def generate_answer(self, query):
        now = time.time()
        response = self.query_engine.query(query)
        for text in response.response_gen:
            yield f"data: {json.dumps({'text': text})}\n\n"
        yield f"data: {json.dumps({'time_taken': round(time.time() - now, 2), 'done': True})}\n\n"
