import asyncio
import uuid
from typing import List

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
            # system_prompt=system_prompt,
            # completion_to_prompt=completion_to_prompt,
            verbose=True
        )

    def get_llm(self):
        return self.llm


class LLMInstance:
    def __init__(self, llm: LlamaProvider):
        self.llm = llm
        self.lock = asyncio.Lock()
        self.id = str(uuid.uuid4())  # Unique ID for each instance


class LLMPool:
    def __init__(self, num_instances: int, model_url: str, system_prompt: str,
                 completion_to_prompt, stopping_ids, model_path: str):
        self.instances: List[LLMInstance] = []
        self.semaphore = asyncio.Semaphore(num_instances)
        self.lock = asyncio.Lock()
        self.queue = asyncio.Queue()
        self.model_url = model_url
        self.system_prompt = system_prompt
        self.completion_to_prompt = completion_to_prompt
        self.stopping_ids = stopping_ids
        self.model_path = model_path

    async def initialize(self):
        async with self.lock:
            if not self.instances:
                for _ in range(self.semaphore._value):
                    llm = LlamaProvider(
                        self.model_url,
                        self.system_prompt,
                        self.completion_to_prompt,
                        self.stopping_ids,
                        model_path=self.model_path
                    )
                    self.instances.append(LLMInstance(llm))

    async def get_instance(self):
        was_queued = False
        if self.semaphore._value == 0:  # All instances are in use
            was_queued = True
            future = asyncio.Future()
            await self.queue.put(future)
            await future

        await self.semaphore.acquire()
        async with self.lock:
            if not self.instances:
                # This shouldn't happen, but let's handle it just in case
                raise RuntimeError("No LLM instances available")
            return self.instances.pop(), was_queued

    async def release_instance(self, instance: LLMInstance):
        async with self.lock:
            self.instances.append(instance)
            self.semaphore.release()
            if not self.queue.empty():
                waiting_future = self.queue.get_nowait()
                waiting_future.set_result(None)
