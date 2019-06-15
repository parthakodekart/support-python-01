"""
Pull the data from the given REST API Url
"""
import os
import requests


class APIParser:

    client = None

    def __init__(self, *args, **kwargs):
        self.API_HOST = kwargs.get('API_HOST', os.getenv('API_HOST', None))
        API_KEY = kwargs.get('API_KEY', os.getenv('API_KEY', None))
        API_SECRET = kwargs.get('API_SECRET', os.getenv('API_SECRET', None))
        self._connect()

    def _connect(self):
        pass

    def fetch(self):
        pass
