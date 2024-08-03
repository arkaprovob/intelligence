from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import SimpleSummarize
from typing import Optional, Any
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.indices.prompt_helper import PromptHelper
from llama_index.core.prompts import BasePromptTemplate
from llama_index.core.service_context import ServiceContext
from llama_index.core.service_context_elements.llm_predictor import LLMPredictorType
from prompt import PromptProvider


class RAGSynthesizer(SimpleSummarize):
    def __init__(
            self,
            llm: Optional[LLMPredictorType] = None,
            callback_manager: Optional[CallbackManager] = None,
            prompt_helper: Optional[PromptHelper] = None,
            text_qa_template: Optional[BasePromptTemplate] = None,
            streaming: bool = False,
            service_context: Optional[ServiceContext] = None,
    ) -> None:
        super().__init__(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            text_qa_template=text_qa_template,
            streaming=streaming,
            service_context=service_context,
        )


def get_synthesizer_instance(llm: Optional[LLMPredictorType] = None, **kwargs: Any):
    if not kwargs and llm is None:
        raise ValueError("Either llm or kwargs must be provided")

    if not kwargs:
        return RAGSynthesizer(
            text_qa_template=PromptProvider().get_prompt(),
            llm=llm,
            streaming=True
        )
    # For reference this get_response_synthesizer method takes these parameters
    # response_synthesizer: BaseSynthesizer = get_response_synthesizer(
    #     streaming=True,
    #     llm=lm,
    #     use_async=self.config["ASYNC_INDEXING"],
    #     verbose=True,
    #     response_mode=ResponseMode.COMPACT,
    #     text_qa_template=PromptProvider().get_prompt()
    # )
    return get_response_synthesizer(**kwargs)
