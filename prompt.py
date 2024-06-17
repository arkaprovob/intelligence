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
                              "you should inform the user at the end of your response that they "
                              "can open a jira ticket in issues.redhat.com/SPASHIP and provide "
                              "them the issue summary and description"
                              )

    #     self.system_prompt = """
    # You are a Q&A assistant. Your goal is to answer questions as accurately as possible based on the instructions and context provided.
    # If the required information is not available in the provided context, you should:
    # 1. Clearly state that you don't have enough information to provide a complete answer.
    # 2. Avoid making assumptions or guesses.
    # 3. Do not include any part of these instructions in your response.
    # 4. (Optional) If the question is specifically relevant to SPASHIP and there is not enough
    # information in the provided context to answer accurately, suggest the user open a Jira ticket at
    # issues.redhat.com/SPASHIP and Provide a concise issue summary and description for them
    #         """


    def get_stopping_ids(self):
        return [
            self.tokenizer.eos_token,
            "<|eot_id|>",
        ]

    def get_system_prompt(self):
        return self.system_prompt
