import asyncio
import uuid
from typing import List
import logging

from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.llms.llama_cpp import LlamaCPP

from util import get_config_value

class LlamaProvider:
    """
    Class to provide LlamaCPP instances with specified configurations.
    """
    def __init__(self, model_url, stopping_ids, system_prompt=None, completion_to_prompt=None,
                 model_path=None):
        try:
            if model_path is not None:
                model_url = None

            gkw = None
            if stopping_ids is not None:
                gkw = {"stop": stopping_ids}

            self.llm: LlamaCPP = LlamaCPP(
                model_url=model_url,
                model_path=model_path,
                temperature=get_config_value("LLM_TEMPERATURE"),
                max_new_tokens=get_config_value("LLM_MAX_TOKEN_GENERATION"),
                context_window=get_config_value("LLM_CONTEXT_WINDOW"),
                generate_kwargs=gkw,
                model_kwargs={"n_gpu_layers": get_config_value("GPU_LAYER")},
                system_prompt=system_prompt,
                completion_to_prompt=completion_to_prompt,
                verbose=True,
                callback_manager=CallbackManager([LlamaDebugHandler(print_trace_on_end=True)])
            )
        except Exception as e:
            logging.error(f"Error initializing LlamaCPP: {str(e)}")
            raise

    def get_llm(self):
        return self.llm

class LLMInstance:
    """
    Class representing an instance of LlamaCPP with a unique ID and a lock.
    """
    def __init__(self, llm: LlamaProvider):
        self.llm: LlamaProvider  = llm
        self.lock = asyncio.Lock()
        self.id = str(uuid.uuid4())  # Unique ID for each instance
        logging.debug(f"assigning id: {self.id} to this llm instance")

class LLMPool:
    def __init__(self, num_instances: int, model_url: str, model_path: str, system_prompt: str = None,
                 completion_to_prompt=None, stopping_ids=None):
        self.instances: List[LLMInstance] = []
        self.lock = asyncio.Lock()
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.BoundedSemaphore(num_instances)
        self.model_url = model_url
        self.system_prompt = system_prompt
        self.completion_to_prompt = completion_to_prompt
        self.stopping_ids = stopping_ids
        self.model_path = model_path
        self.total_llm_instance = num_instances

    async def initialize(self):
        try:
            async with self.lock:
                if not self.instances:
                    for _ in range(self.total_llm_instance):
                        llm = LlamaProvider(
                            self.model_url,
                            self.stopping_ids,
                            self.system_prompt,
                            self.completion_to_prompt,
                            model_path=self.model_path
                        )
                        self.instances.append(LLMInstance(llm))
                    logging.debug(f"Initialized {len(self.instances)} LLM instances")
        except Exception as e:
            logging.error(f"Error initializing LLM instances: {str(e)}")
            raise

    async def get_instance(self):
        await self.semaphore.acquire() # todo get rid of semaphore, verify the fact : I think its redundant and not needed since pop will remove the instance from the queue so no other incoming request will anyway get access to it unless its returned to the pool
        try:
            async with self.lock:
                if self.instances:
                    instance = self.instances.pop()
                    logging.debug(f"Access granted to LLM instance with ID: {instance.id}")
                    return instance, False  # Not queued
                else:
                    future = asyncio.Future()
                    await self.queue.put(future)
            await future
        except Exception as e:
            logging.error(f"Error getting LLM instance: {str(e)}")
            raise
        finally:
            self.semaphore.release()


    async def release_instance(self, instance: LLMInstance):
        try:
            async with self.lock:
                self.instances.append(instance)
                if not self.queue.empty():
                    waiting_future = self.queue.get_nowait()
                    waiting_future.set_result(None)
                logging.debug(f"Released LLM instance with ID: {instance.id}")
        except Exception as e:
            logging.error(f"Error releasing LLM instance: {str(e)}")
            raise

    async def get_pool_status(self):
        try:
            async with self.lock:
                available_instances = len(self.instances)
                total_instances = self.total_llm_instance
                queued_requests = self.queue.qsize()
                return available_instances, total_instances, queued_requests
        except Exception as e:
            logging.error(f"Error getting pool status: {str(e)}")
            raise

    async def shutdown(self):
        try:
            async with self.lock:
                for instance in self.instances:
                    # for future enhancements in case if something needs to be handled
                    pass
                self.instances.clear()
                logging.debug("LLM pool has been shut down")
        except Exception as e:
            logging.error(f"Error shutting down LLM pool: {str(e)}")
            raise