import io
import json
from unittest.mock import Mock
from unittest.mock import call

import pytest

from lambda_gateway.event_proxy import EventProxy
from lambda_gateway.request_handler import LambdaRequestHandler


class TestLambdaRequestHandler:
    def setup(self):
        self.subject = Mock(LambdaRequestHandler)
        self.subject.proxy = Mock(EventProxy)

    def set_request(self, verb, path='/'):
        if verb in ['POST']:
            body = json.dumps({'data': 'POST_DATA'})
            headers = {'Content-Length': len(body)}
        else:
            body = ''
            headers = {}
        req = {
            'body': body,
            'headers': headers,
            'httpMethod': verb,
            'path': path,
        }
        self.subject.headers = headers
        self.subject.path = path
        self.subject.rfile = io.BytesIO(body.encode())
        self.subject.wfile = Mock()
        return req

    @pytest.mark.parametrize(
        ('proxy'),
        [
            EventProxy('index.handler', '/simple/', None),
            EventProxy('index.handler', '/simple/', 3),
        ],
    )
    def test_set_proxy(self, proxy):
        LambdaRequestHandler.set_proxy(proxy)
        assert LambdaRequestHandler.proxy == proxy

    @pytest.mark.parametrize('verb', ['GET', 'HEAD', 'POST'])
    def test_do(self, verb):
        getattr(LambdaRequestHandler, f'do_{verb}')(self.subject)
        self.subject.invoke.assert_called_once_with(verb)

    @pytest.mark.parametrize('verb', ['GET', 'HEAD', 'POST'])
    def test_get_body(self, verb):
        req = self.set_request(verb)
        ret = LambdaRequestHandler.get_body(self.subject)
        assert ret == req['body']

    @pytest.mark.parametrize('verb', ['GET', 'HEAD', 'POST'])
    def test_get_event(self, verb):
        req = self.set_request(verb)
        self.subject.get_body.return_value = req['body']
        ret = LambdaRequestHandler.get_event(self.subject, verb)
        assert ret == req

    @pytest.mark.parametrize('verb', ['GET', 'HEAD', 'POST'])
    def test_invoke(self, verb):
        req = self.set_request(verb)
        self.subject.get_event.return_value = req
        self.subject.proxy.invoke.return_value = {
            'body': 'OK',
            'statusCode': 200,
            'headers': {
                'Content-Length': 2,
                'Content-Type': 'application/json',
            }
        }
        LambdaRequestHandler.invoke(self.subject, verb)
        self.subject.proxy.invoke.assert_called_once_with(req)
        self.subject.send_response.assert_called_once_with(200)
        self.subject.send_header.assert_has_calls([
            call('Content-Length', 2),
            call('Content-Type', 'application/json'),
        ])
        self.subject.end_headers.assert_called_once_with()
        self.subject.wfile.write.assert_called_once_with('OK'.encode())
