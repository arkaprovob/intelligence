from typing import Optional, List, Mapping, Any, Union

from llama_index.core import SimpleDirectoryReader, SummaryIndex, PromptTemplate
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core import Settings

from threading import Thread

import torch
import transformers
from torch import bfloat16
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, StoppingCriteria, \
    TextIteratorStreamer
import time
import json
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.bridge.pydantic import Field


class OurLLM(CustomLLM):
    context_window: int = 3900
    num_output: int = 256
    model_name: str = "UCLA-AGI/Llama-3-Instruct-8B-SPPO-Iter3"
    dummy_response: str = "My response"
    device: str = "auto"
    trust_remote_code: bool = True
    cache_dir: str = "/media/arko/work/.hfcache"
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=bfloat16
    )
    model_config = transformers.AutoConfig.from_pretrained(
        model_name,
        trust_remote_code=trust_remote_code,
        cache_dir=cache_dir
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=trust_remote_code,
        config=model_config,
        quantization_config=bnb_config,
        device_map=device,
        torch_dtype=torch.bfloat16,
        cache_dir=cache_dir
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False, padding_side='left',
                                              cache_dir=cache_dir)
    result: Optional[Any] = None

    query_wrapper_prompt: PromptTemplate = Field(
        default=PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>"),
        description=(
            "The query wrapper prompt, containing the query placeholder. "
            "The model card on HuggingFace should specify if this is needed. "
            "Should contain a `{query_str}` placeholder."
        ),
    )
    system_prompt: str = Field(
        default=("You are a Q&A assistant. Your goal is to answer questions as "
                 "accurately as"
                 "possible based on the instructions and context provided."
                 "If the required information is not available in the provided "
                 "context,"
                 "you should inform the user at the end of your response that they "
                 "can open a jira ticket in issues.redhat.com/SPASHIP and provide "
                 "them the issue summary and description"
                 ),
        description=(
            "The system prompt, containing any extra instructions or context. "
            "The model card on HuggingFace should specify if this is needed."
        ),
    )

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ CONTROL IS HERE $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        return CompletionResponse(text=self.dummy_response)

    @llm_completion_callback()
    def stream_complete(
            self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        print("@@@@@@@@@@@@@@@@@@@@@@ CONTROL IS HERE @@@@@@@@@@@@@@@@@@@@@@@@@")

        response = ""

        formatted_prompt = self.format_prompt(prompt)
        # print(f"Formatted prompt: {formatted_prompt}")

        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        streamer = TextIteratorStreamer(self.tokenizer,skip_prompt=True, skip_special_tokens=True)
        input_ids = inputs.input_ids.to(self.model.device)
        attention_mask = inputs.attention_mask.to(self.model.device)
        generation_kwargs = dict(input_ids=input_ids, attention_mask=attention_mask,
                                 do_sample=False,
                                 top_k=50, top_p=0.95, temperature=0.1, num_return_sequences=1,
                                 no_repeat_ngram_size=3, pad_token_id=0,
                                 streamer=streamer, max_new_tokens=2048)

        thread = Thread(target=self._generate, kwargs=generation_kwargs)
        thread.start()

        for token in streamer:
            # if "▁▁" in token:
            #     token = token.replace("▁▁", "")
            yield CompletionResponse(text=response, delta=token)
        thread.join()

    def _generate(self, **kwargs):
        self.result = self.model.generate(**kwargs)

    def format_prompt(self, prompt: str) -> str:
        full_prompt = ""
        if self.query_wrapper_prompt:
            full_prompt = self.query_wrapper_prompt.format(query_str=prompt)
        if self.system_prompt:
            full_prompt = f"{self.system_prompt} {full_prompt}"
        return full_prompt
