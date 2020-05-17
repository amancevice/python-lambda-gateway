import asyncio
from unittest import mock

import pytest

from lambda_gateway.event_proxy import EventProxy


class TestEventProxy:
    def setup(self):
        self.subject = EventProxy('index.handler', '/simple/', 3)

    @pytest.mark.parametrize(('handler', 'exp'), [
        ('lambda_function.lambda_handler', 'lambda_handler'),
    ])
    def test_get_handler(self, handler, exp):
        self.subject.handler = handler
        ret = self.subject.get_handler().__name__
        assert ret == exp

    @pytest.mark.parametrize('handler', [
        'lambda_function',
        'not_a_file.handler',
        'lambda_function.not_a_function',
    ])
    def test_get_handler_error(self, handler):
        self.subject.handler = handler
        with pytest.raises(ValueError):
            self.subject.get_handler()

    @pytest.mark.parametrize(('verb', 'path', 'status', 'message'), [
        ('GET', '/simple/', 200, 'OK'),
        ('HEAD', '/simple/', 200, 'OK'),
        ('POST', '/simple/', 200, 'OK'),
    ])
    def test_invoke_success(self, verb, path, status, message):
        self.subject.get_handler = lambda: lambda event, context: exp
        exp = EventProxy.jsonify(verb, status, message=message)
        ret = self.subject.invoke({'httpMethod': verb, 'path': path})
        assert ret == exp

    @pytest.mark.parametrize(('verb', 'path', 'status', 'message'), [
        ('GET', '/simple/', 502, 'Internal server error'),
        ('HEAD', '/simple/', 502, 'Internal server error'),
        ('POST', '/simple/', 502, 'Internal server error'),
        ('GET', '/', 403, 'Forbidden'),
        ('HEAD', '/', 403, 'Forbidden'),
        ('POST', '/', 403, 'Forbidden'),
    ])
    def test_invoke_error(self, verb, path, status, message):
        def handler(event, context):
            raise Exception()
        self.subject.get_handler = lambda: handler
        exp = EventProxy.jsonify(verb, status, message=message)
        ret = self.subject.invoke({'httpMethod': verb, 'path': path})
        assert ret == exp

    @pytest.mark.parametrize(('verb', 'path', 'status', 'message'), [
        ('GET', '/simple/', 504, 'Endpoint request timed out'),
        ('HEAD', '/simple/', 504, 'Endpoint request timed out'),
        ('POST', '/simple/', 504, 'Endpoint request timed out'),
    ])
    def test_invoke_timeout(self, verb, path, status, message):
        patch = 'lambda_gateway.event_proxy.EventProxy.invoke_async'
        with mock.patch(patch) as mock_invoke:
            mock_invoke.side_effect = asyncio.TimeoutError
            exp = EventProxy.jsonify(verb, status, message=message)
            ret = self.subject.invoke({'httpMethod': verb, 'path': path})
            assert ret == exp

    @pytest.mark.parametrize(('verb', 'statusCode', 'body', 'exp'), [
        (
            'GET', 200, {'message': 'OK'},
            {
                'body': '{"message": "OK"}',
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Content-Length': 17,
                },
            },
        ),
        (
            'HEAD', 200, {'message': 'OK'},
            {
                'body': '',
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Content-Length': 0,
                },
            },
        ),
        (
            'POST', 200, {'message': 'OK'},
            {
                'body': '{"message": "OK"}',
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Content-Length': 17,
                },
            },
        ),
    ])
    def test_jsonify(self, verb, statusCode, body, exp):
        ret = EventProxy.jsonify(verb, statusCode, **body)
        assert ret == exp
