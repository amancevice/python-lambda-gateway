import io
import json
from unittest.mock import Mock
from unittest.mock import call
from urllib.parse import urlencode

import pytest

from lambda_gateway.event_proxy import EventProxy
from lambda_gateway.request_handler import LambdaRequestHandler


class TestLambdaRequestHandler:
    def setup_method(self):
        self.subject = Mock(LambdaRequestHandler)
        self.subject.proxy = Mock(EventProxy)
        self.subject.version = "2.0"
        self.subject.get_event_v1 = lambda x: LambdaRequestHandler.get_event_v1(
            self.subject, x
        )
        self.subject.get_event_v2 = lambda x: LambdaRequestHandler.get_event_v2(
            self.subject, x
        )

    def set_request(self, verb, path="/", version="2.0", **params):
        rawPath = path
        if verb in ["POST"]:
            body = json.dumps({"data": "POST_DATA"})
            headers = {"Content-Length": len(body)}
        else:
            body = ""
            headers = {}
        if params:
            path += f"?{urlencode(params)}"
        self.subject.headers = headers
        self.subject.path = path
        self.subject.rfile = io.BytesIO(body.encode())
        self.subject.wfile = Mock()

        req = {
            "version": version,
            "body": body,
            "headers": headers,
            "queryStringParameters": params,
        }
        if version == "2.0":
            req.update(
                {
                    "routeKey": f"{verb} {rawPath}",
                    "rawPath": rawPath,
                    "rawQueryString": urlencode(params),
                    "queryStringParameters": params,
                    "requestContext": {
                        "http": {
                            "method": verb,
                            "path": rawPath,
                        },
                    },
                }
            )
        elif version == "1.0":
            req.update(
                {"httpMethod": verb, "path": rawPath, "queryStringParameters": params}
            )

        return req

    @pytest.mark.parametrize(
        ("proxy", "version"),
        [
            (EventProxy("index.handler", "/simple/", None), "1.0"),
            (EventProxy("index.handler", "/simple/", 3), "1.0"),
            (EventProxy("index.handler", "/simple/", None), "2.0"),
            (EventProxy("index.handler", "/simple/", 3), "2.0"),
        ],
    )
    def test_set_proxy(self, proxy, version):
        LambdaRequestHandler.set_proxy(proxy, version)
        assert LambdaRequestHandler.proxy == proxy
        assert LambdaRequestHandler.version == version

    @pytest.mark.parametrize(
        "verb", ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    )
    def test_do(self, verb):
        getattr(LambdaRequestHandler, f"do_{verb}")(self.subject)
        self.subject.invoke.assert_called_once_with(verb)

    @pytest.mark.parametrize("verb", ["GET", "HEAD", "POST"])
    def test_get_body(self, verb):
        req = self.set_request(verb)
        ret = LambdaRequestHandler.get_body(self.subject)
        assert ret == req["body"]

    @pytest.mark.parametrize(
        ("verb", "path", "version", "params"),
        [
            ("GET", "/", "1.0", dict(fizz="buzz")),
            ("HEAD", "/", "1.0", dict(fizz="buzz")),
            ("POST", "/", "1.0", dict(fizz="buzz")),
            ("GET", "/", "2.0", dict(fizz="buzz")),
            ("HEAD", "/", "2.0", dict(fizz="buzz")),
            ("POST", "/", "2.0", dict(fizz="buzz")),
        ],
    )
    def test_get_event(self, verb, path, version, params):
        exp = self.set_request(verb, path, version, **params)
        self.subject.version = version
        self.subject.get_body.return_value = exp["body"]
        ret = LambdaRequestHandler.get_event(self.subject, verb)
        assert ret == exp

    @pytest.mark.parametrize(
        ("verb", "path", "version", "params"),
        [
            ("GET", "/", "1.0", dict(fizz="buzz")),
            ("HEAD", "/", "1.0", dict(fizz="buzz")),
            ("POST", "/", "1.0", dict(fizz="buzz")),
            ("GET", "/", "2.0", dict(fizz="buzz")),
            ("HEAD", "/", "2.0", dict(fizz="buzz")),
            ("POST", "/", "2.0", dict(fizz="buzz")),
        ],
    )
    def test_invoke(self, verb, path, version, params):
        req = self.set_request(verb, path, version, **params)
        self.subject.get_event.return_value = req
        self.subject.proxy.invoke.return_value = {
            "body": "OK",
            "statusCode": 200,
            "headers": {
                "Content-Length": 2,
                "Content-Type": "application/json",
            },
        }
        LambdaRequestHandler.invoke(self.subject, verb)
        self.subject.proxy.invoke.assert_called_once_with(req)
        self.subject.send_response.assert_called_once_with(200)
        self.subject.send_header.assert_has_calls(
            [
                call("Content-Length", 2),
                call("Content-Type", "application/json"),
            ]
        )
        self.subject.end_headers.assert_called_once_with()
        self.subject.wfile.write.assert_called_once_with("OK".encode())
