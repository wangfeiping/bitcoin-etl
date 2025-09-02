import hashlib
import time
import threading

import requests

_session_cache = {}


class RateLimiter:
    def __init__(self, requests_per_second):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        if self.min_interval <= 0:
            return
        
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            self.last_request_time = time.time()


def _get_session(endpoint_uri):
    cache_key = hashlib.md5(endpoint_uri.encode('utf-8')).hexdigest()
    if cache_key not in _session_cache:
        _session_cache[cache_key] = requests.Session()
    return _session_cache[cache_key]


def make_post_request(endpoint_uri, data, *args, **kwargs):
    kwargs.setdefault('timeout', 10)
    session = _get_session(endpoint_uri)
    response = session.post(endpoint_uri, data=data, *args, **kwargs)
    response.raise_for_status()

    return response.content


def make_post_request_with_rate_limit(endpoint_uri, data, rate_limiter, *args, **kwargs):
    if rate_limiter:
        rate_limiter.wait_if_needed()
    return make_post_request(endpoint_uri, data, *args, **kwargs)
