import httpretty
import os
import re
from ouroboros.client import Client
import requests


class with_fake_http:

    def start_mocking_http(self):
        self.host = "fake-eventstore.com"
        self.port = 12345
        self.client = Client(self.host, self.port, "admin", "changeit", no_ssl=True)
        httpretty.enable()

    def cleanup_httpretty(self):
        httpretty.reset()
        httpretty.disable()

    def fake_response(self, path, file=None, status=200, body=None):
        if file:
            fn = os.path.join(os.path.dirname(__file__), 'fake-data', file)
            with open(fn, 'r') as f:
                body = f.read()
        uri = "http://{0}:{1}{2}".format(self.host, self.port, path)
        print(uri)
        httpretty.register_uri(httpretty.GET, uri, body=body, status=status)

    def expect_call(self, path, method):
        uri = "http://{0}:{1}{2}".format(self.host, self.port, path)
        httpretty.register_uri(method, uri)
