from typing import Optional, List
from llama_index.core import PromptTemplate

_PROMPT_TEMPLATE_PHI = """
<|system|>

You are an {tone_name} that answers questions about technical documentations and user guides    .

You are given some extracted parts from machine learning papers along with a question.

If you don't know the answer, just say "I don't know." Don't try to make up an answer.

It is very important that you ALWAYS answer the question in the same language the question is in. Remember to always do that.

Use only the following pieces of context to answer the question at the end.

<|end|>

<|user|>

Context: {context_str}

Question is below. Remember to answer in the same language:

Question: {query_str}

<|end|>

<|assistant|>

"""

_PROMPT_TEMPLATE_LLAMA_3 = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a {tone_name} with a witty sense of humor who answers questions based on provided context. Your goal is to be informative yet entertaining, like a knowledgeable friend at a dinner party.

Instructions:
1. Channel your inner detective: examine the context thoroughly and piece together the answer step by step.
2. Stick to the facts from the provided context like glue to paper - no making stuff up!
3. If you're stumped, admit it with a touch of humor. Say something like, "Well, looks like this question has outsmarted me! I don't have enough information to crack this case."
4. Be a language chameleon - always answer in the same tongue as the question.
5. Sprinkle in light-hearted jokes or puns when appropriate, but keep it classy - we're aiming for 'witty professional', not 'amateur comedian'.
6. Feel free to use playful metaphors or analogies to explain complex ideas.

Remember: Your mission is to inform and delight in equal measure. Let's make learning fun!

Context:
{context_str}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{query_str}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

_PROMPT_TEMPLATE_GEMMA = """<start_of_turn>user
You are a {tone_name} who answers questions based on provided context. Please follow these instructions:
1. Carefully examine the context and think step-by-step before answering.
2. Use only the information provided in the context to answer the question.
3. If you don't have enough information to answer, say "I don't have enough information to answer this question."
4. Always answer in the same language as the question.
5. Feel free to use appropriate humor or analogies to make your answers engaging, while maintaining professionalism.

Here's the context:
{context_str}

Now, please answer this question:
{query_str}<end_of_turn>
<start_of_turn>model
"""


class PromptProvider:
    """A class to provide prompt templates for language models."""

    @staticmethod
    def default_prompt() -> str:
        """Return the default prompt template as a string."""
        return _PROMPT_TEMPLATE_GEMMA

    def __init__(self, prompt_template: Optional[str] = None, required_placeholders: Optional[List[str]] = None):
        """
        Initialize the PromptProvider with an optional custom prompt template and required placeholders.

        :param prompt_template: A custom prompt template string. If None, uses the default prompt.
        :param required_placeholders: A list of placeholders that must be present in the template.
        """
        self.required_placeholders = required_placeholders or ["{context_str}", "{query_str}", "{tone_name}"]
        template = prompt_template or self.default_prompt()
        self._validate_template(template)
        self.prompt_template = template

    def _validate_template(self, template: str) -> None:
        """
        Validate that the given template contains all required placeholders.

        :param template: The prompt template to validate.
        :raises ValueError: If the template is missing any required placeholders.
        """
        missing_placeholders = [p for p in self.required_placeholders if p not in template]
        if missing_placeholders:
            raise ValueError(
                f"Prompt template is missing the following required placeholders: {', '.join(missing_placeholders)}")

    def validate_current_template(self) -> None:
        """
        Validate that the current prompt template contains all required placeholders.

        :raises ValueError: If the current template is missing any required placeholders.
        """
        self._validate_template(self.prompt_template)

    def get_prompt(self) -> PromptTemplate:
        """Return the PromptTemplate object based on the stored prompt template string."""
        return PromptTemplate(self.prompt_template)

    def update_prompt(self, new_template: str) -> None:
        """
        Update the prompt template with a new string.

        :param new_template: The new prompt template string.
        :raises ValueError: If the new template is invalid.
        """
        self._validate_template(new_template)
        self.prompt_template = new_template

    def add_required_placeholder(self, placeholder: str) -> None:
        """
        Add a new required placeholder to the list.

        :param placeholder: The new placeholder to add.
        :raises ValueError: If the current template doesn't contain the new placeholder.
        """
        if placeholder not in self.prompt_template:
            raise ValueError(f"Current template does not contain the new placeholder: {placeholder}")
        self.required_placeholders.append(placeholder)

    def remove_required_placeholder(self, placeholder: str) -> None:
        """
        Remove a placeholder from the list of required placeholders.

        :param placeholder: The placeholder to remove.
        :raises ValueError: If the placeholder is not in the list of required placeholders.
        """
        if placeholder not in self.required_placeholders:
            raise ValueError(f"Placeholder {placeholder} is not in the list of required placeholders")
        self.required_placeholders.remove(placeholder)
