from typing import Optional, List
from llama_index.core import PromptTemplate


class PromptProvider:
    """A class to provide prompt templates for language models."""

    @staticmethod
    def default_prompt() -> str:
        """Return the default prompt template as a string."""
        return """
        ### Context:
        {context_str}

        ### Query: {query_str}

        ### Instructions:
        1. If the context doesn't contain enough information to fully answer the query, explicitly state: "The provided information is not sufficient to answer this query."
        2. If any part of the query cannot be answered based on the context, clearly indicate which parts lack information.
        3. Write in a {tone_name} tone.
        4. If you're unsure about any aspect of the answer, state your uncertainty clearly.

        ### Answer:
        """

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
