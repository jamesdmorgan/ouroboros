import json
from expects.matchers import Matcher
from pprint import PrettyPrinter
import httpretty

pp = PrettyPrinter(indent=4)

class have_posted_to(Matcher):

    _fail = "Expected {2} request to {0} but was {1}"

    def __init__(self, path, method=httpretty.POST):
        self._path = path
        self._method = method

    def _match(self, req):
        return self._path == req.path and self._method == req.method, "does not match"

    def _failure_message(self, req):
        return self._fail.format(self._path, req.path, self._method)


class have_json(Matcher):

    def __init__(self, body):
        self._body = body

    def _match(self, req):
        return json.loads(req.body.decode('Utf-8')) == self._body, "does not match"

    def _failure_message(self, req):
        return "Expected request with body {0} but was {1}".format(
            pp.pformat(json.loads(req.body.decode('Utf-8'))),
            pp.pformat(self._body))
