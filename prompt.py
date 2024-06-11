from transformers import AutoTokenizer


class PromptProvider:
    def __init__(self, model_name):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
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

    def completion_to_prompt(self, completion):
        return f"<|USER|>{completion}<|ASSISTANT|>"
