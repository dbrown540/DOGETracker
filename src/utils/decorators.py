import functools
import logging
import time

import requests
from typing import Callable

from settings import MAX_RETRIES, RETRY_TIMEOUT

def api_retry(func: Callable) -> None:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                logging.info(
                    "[%s] (Attempt: %d/%d) – Successfully connected to the url!",
                    func.__name__, attempt + 1, MAX_RETRIES
                )
                return result
            except requests.exceptions.Timeout as e:
                logging.warning(
                    "[%s] (Attempt: %d/%d) – Failed to connect to the url due to timeout: %s "
                    "Retrying in %d seconds...", 
                    func.__name__, attempt + 1, MAX_RETRIES, str(e), RETRY_TIMEOUT
                )
                time.sleep(RETRY_TIMEOUT)
                continue

            except requests.exceptions.ConnectionError as e:
                logging.warning(
                    "[%s] (Attempt: %d/%d) – Connection failed: %s. "
                    "Check your internet or the target server. Retrying in %d seconds...",
                    func.__name__, attempt + 1, MAX_RETRIES, str(e), RETRY_TIMEOUT
                )
                time.sleep(RETRY_TIMEOUT)
                continue

        logging.error(
            "[%s] (Attempts exceeded!) – Failed to connect to the url!",
            func.__name__
        )
    return wrapper