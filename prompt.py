from llama_index.core import PromptTemplate, BasePromptTemplate
from llama_index.core.prompts import LangchainPromptTemplate
from llama_index.core.response_synthesizers import TreeSummarize
from transformers import AutoTokenizer


def completion_to_prompt(completion):
    return f"{completion}"


class PromptProvider:
    def __init__(self, model_name, cache_dir=None):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cachedir=cache_dir)
        self.system_prompt = ("You are a Q&A assistant. Your goal is to answer questions as "
                              "accurately as"
                              "possible based on the instructions and context provided."
                              "If the required information is not available in the provided "
                              "context,"
                              "don't include the location or filepath"
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
            "<|eot_id|>","<|FOLLOWUP_QUESTION|>","<|USER|>" "<|FOLLOWUP_Q|>", "<|ASSISTANT|>"
        ]

    def get_system_prompt(self):
        return self.system_prompt


# qa_prompt_tmpl_str = (
#             "Context information is below.\n"
#             "---------------------\n"
#             "{context_str}\n"
#             "---------------------\n"
#             "Given the context information above I want you to think step by step to answer the query in a crisp "
#             "manner, And don't include this instruction in the answer incase case you don't know the answer say 'I don't know!'.\n"
#             "Query: {query_str}\n"
#             "Answer: "
#             )
#
# qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

# Define a custom prompt
qa_prompt_tmpl = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query.\n"
    "Please also write the answer in the tone of {tone_name}.\n"
    "Query: {query_str}\n"
    "Answer: "
)
qa_prompt = PromptTemplate(qa_prompt_tmpl)

# qa_prompt_tmpl_format = BasePromptTemplate(
#     template=qa_prompt,
#     template_var_mappings={"query_str": "question", "context_str": "context", "tone_name": "tone_name"},
# ) solid implementation required otherwise it will trow error
