import langchain
langchain.verbose = True
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("langchain").setLevel(logging.DEBUG)

import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from api_keys import api_keys, api_key


from langchain_mistralai import ChatMistralAI
import time
from collections import deque
import httpx

class APIKeyManager:
    def __init__(self, keys):
        # active_keys: deque of (key, last_used_timestamp)
        self.active_keys = deque((k, 0.0) for k in keys)
        # error_keys: deque of keys that hit 429
        self.error_keys = deque()

    def get_key(self):
        # sort by least‐recently used
        self.active_keys = deque(sorted(self.active_keys, key=lambda x: x[1]))
        if not self.active_keys:
            raise RuntimeError("No active keys left")
        key, _ = self.active_keys.popleft()
        return key

    def mark_success(self, key):
        # record now as last used
        self.active_keys.append((key, time.time()))

    def mark_failure(self, key):
        # send to error queue
        self.error_keys.append(key)

    def refresh_error_keys(self):
        # move all errored keys back into active (coldest)
        while self.error_keys:
            key = self.error_keys.popleft()
            self.active_keys.append((key, 0.0))

    def has_active(self):
        return bool(self.active_keys)


key_manager = APIKeyManager(api_keys)

def invoke_with_rotation(prompt, model_size, structured_class=None):
    last_error = None

    while True:
        while key_manager.has_active():
            key = key_manager.get_key()
            llm = ChatMistralAI(
                model=f"mistral-{model_size}-latest",
                api_key=key,
                temperature=0,
                top_p=1,
                timeout=500,
                verbose=True,
                max_retries=7,
            )
            try:
                if structured_class:
                    llm = llm.with_structured_output(structured_class)
                res = llm.invoke(prompt)
                key_manager.mark_success(key)
                return res
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    key_manager.mark_failure(key)
                last_error = e
            except Exception as e:
                last_error = e

                raise

        if key_manager.error_keys:
            print("All keys rate‑limited, sleeping 20s before retrying…")
            time.sleep(10)
            key_manager.refresh_error_keys()
            continue

        raise RuntimeError("All API keys exhausted") from last_error
