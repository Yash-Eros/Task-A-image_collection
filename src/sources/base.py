import time
import requests
from config import REQUEST_DELAY
from urllib.parse import quote

class BaseSource:

    def __init__(self, name):
        self.name = name

    def get(self, url, headers=None, params=None):
        time.sleep(REQUEST_DELAY)
        
        # Add explicit encoding handling for params
        if params and 'query' in params:
            # Ensure query is properly encoded
            query_str = params['query']
            if isinstance(query_str, str):
                # Verify encoding is clean
                params['query'] = query_str.encode('utf-8').decode('utf-8')
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def paginate(self, query, limit):
        raise NotImplementedError