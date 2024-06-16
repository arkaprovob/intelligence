from transformers import AutoTokenizer


def completion_to_prompt(completion):
    return f"<|USER|>{completion}<|ASSISTANT|>"


class PromptProvider:
    def __init__(self, model_name, cache_dir=None):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cachedir=cache_dir)
        self.system_prompt = ("You are a Q&A assistant. Your goal is to answer questions as "
                              "accurately as"
                              "possible based on the instructions and context provided."
                              "If the required information is not available in the provided "
                              "context,"
                              "you should inform the user at the end of your response that a "
                              "ticket will be"
                              "created for further investigation."
                              )

    def get_stopping_ids(self):
        return [
            self.tokenizer.eos_token,
            "<|eot_id|>",
        ]

    def get_system_prompt(self):
        return self.system_prompt
