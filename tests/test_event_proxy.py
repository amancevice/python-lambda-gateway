import asyncio
from unittest import mock

import pytest

from lambda_gateway.event_proxy import EventProxy


class TestEventProxy:
    def setup_method(self):
        self.subject = EventProxy("index.handler", "/simple/", 3)

    @pytest.mark.parametrize(
        ("handler", "exp"),
        [
            ("lambda_function.lambda_handler", "lambda_handler"),
        ],
    )
    def test_get_handler(self, handler, exp):
        self.subject.handler = handler
        ret = self.subject.get_handler().__name__
        assert ret == exp

    @pytest.mark.parametrize(
        "handler",
        [
            "lambda_function",
            "not_a_file.handler",
            "lambda_function.not_a_function",
        ],
    )
    def test_get_handler_error(self, handler):
        self.subject.handler = handler
        with pytest.raises(ValueError):
            self.subject.get_handler()

    @pytest.mark.parametrize(
        ("event", "exp"),
        [
            (
                {
                    "version": "1.0",
                    "httpMethod": "GET",
                    "path": "/simple/",
                },
                EventProxy.jsonify("GET", 200, message="OK"),
            ),
            (
                {
                    "version": "1.0",
                    "httpMethod": "HEAD",
                    "path": "/simple/",
                },
                EventProxy.jsonify("HEAD", 200, message="OK"),
            ),
            (
                {
                    "version": "1.0",
                    "httpMethod": "POST",
                    "path": "/simple/",
                    "body": '{"fizz": "buzz"}',
                },
                EventProxy.jsonify("POST", 200, message="OK"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("GET", 200, message="OK"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "HEAD",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("HEAD", 200, message="OK"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "body": '{"fizz": "buzz"}',
                    "requestContext": {
                        "http": {
                            "method": "POST",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("POST", 200, message="OK"),
            ),
        ],
    )
    def test_invoke_success(self, event, exp):
        self.subject.get_handler = lambda: lambda event, context: exp
        ret = self.subject.invoke(event)
        assert ret == exp

    @pytest.mark.parametrize(
        ("event", "exp"),
        [
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("GET", 502, message="Internal server error"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "HEAD",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("HEAD", 502, message="Internal server error"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "POST",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("POST", 502, message="Internal server error"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/",
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/",
                        },
                    },
                },
                EventProxy.jsonify("GET", 403, message="Forbidden"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/",
                    "requestContext": {
                        "http": {
                            "method": "HEAD",
                            "path": "/",
                        },
                    },
                },
                EventProxy.jsonify("HEAD", 403, message="Forbidden"),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/",
                    "requestContext": {
                        "http": {
                            "method": "POST",
                            "path": "/",
                        },
                    },
                },
                EventProxy.jsonify("POST", 403, message="Forbidden"),
            ),
        ],
    )
    def test_invoke_error(self, event, exp):
        def handler(event, context):
            raise Exception()

        self.subject.get_handler = lambda: handler
        ret = self.subject.invoke(event)
        assert ret == exp

    @pytest.mark.parametrize(
        ("event", "exp"),
        [
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify(
                    "GET",
                    504,
                    message="Endpoint request timed out",
                ),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "requestContext": {
                        "http": {
                            "method": "HEAD",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify("HEAD", 504),
            ),
            (
                {
                    "version": "2.0",
                    "rawPath": "/simple/",
                    "body": '{"fizz": "buzz"}',
                    "requestContext": {
                        "http": {
                            "method": "POST",
                            "path": "/simple/",
                        },
                    },
                },
                EventProxy.jsonify(
                    "POST",
                    504,
                    message="Endpoint request timed out",
                ),
            ),
        ],
    )
    def test_invoke_timeout(self, event, exp):
        patch = "lambda_gateway.event_proxy.EventProxy.invoke_async"
        with mock.patch(patch) as mock_invoke:
            mock_invoke.side_effect = asyncio.TimeoutError
            ret = self.subject.invoke(event)
            assert ret == exp

    @pytest.mark.parametrize(
        ("verb", "statusCode", "body", "exp"),
        [
            (
                "GET",
                200,
                {"message": "OK"},
                {
                    "body": '{"message": "OK"}',
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Content-Length": 17,
                    },
                },
            ),
            (
                "HEAD",
                200,
                {"message": "OK"},
                {
                    "body": "",
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Content-Length": 0,
                    },
                },
            ),
            (
                "POST",
                200,
                {"message": "OK"},
                {
                    "body": '{"message": "OK"}',
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Content-Length": 17,
                    },
                },
            ),
        ],
    )
    def test_jsonify(self, verb, statusCode, body, exp):
        ret = EventProxy.jsonify(verb, statusCode, **body)
        assert ret == exp
