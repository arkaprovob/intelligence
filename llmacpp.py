from llama_index.llms.llama_cpp import LlamaCPP
from utility import get_config_value


class LlamaProvider:
    def __init__(self, model_url, system_prompt, completion_to_prompt, stopping_ids,
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

    def get_llm(self):
        return self.llm
