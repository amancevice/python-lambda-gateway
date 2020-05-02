import asyncio
import http
import io
import json
import sys
from unittest import mock

import pytest

from lambda_gateway import server
from lambda_gateway.server import LambdaRequestHandler as Handler


class TestLambdaRequestHandler:
    def setup(self):
        self.body = json.dumps({'text': 'py.test'})
        self.subject = mock.Mock(Handler)
        self.subject.headers = {'Content-Length': len(self.body)}
        self.subject.path = '/'
        self.subject.rfile = io.BytesIO(self.body.encode())
        self.subject.timeout = 30

    def test_set_handler(self):
        handler = 'lambda_function.lambda_handler'
        Handler.set_handler(handler)
        assert Handler.handler == handler

    def test_set_timeout(self):
        Handler.set_timeout(11)
        assert Handler.timeout == 11

    @pytest.mark.parametrize('verb', ['GET', 'HEAD', 'POST'])
    def test_do(self, verb):
        func = getattr(Handler, f'do_{verb}')
        func(self.subject)
        self.subject.invoke.assert_called_once_with(verb)

    def test_get_body(self):
        assert Handler.get_body(self.subject) == self.body

    def test_get_body_err(self):
        self.subject.headers = {}
        assert Handler.get_body(self.subject) == ''

    @pytest.mark.parametrize('verb', ['GET', 'HEAD', 'POST'])
    def test_get_event(self, verb):
        self.subject.get_body.return_value = self.body
        ret = Handler.get_event(self.subject, verb)
        exp = {
            'body': self.body,
            'headers': self.subject.headers,
            'httpMethod': verb,
            'path': '/',
        }
        assert ret == exp

    @mock.patch('lambda_gateway.server.get_handler')
    def test_invoke_async(self, mock_get_handler):

        def handler(event, context=None):
            return event

        mock_get_handler.return_value = handler
        evt = {'text': 'py.test'}
        cor = Handler.invoke_async(self.subject, evt)
        ret = asyncio.run(cor)
        assert ret == evt

    def test_invoke_with_timeout(self):
        evt = {'text': 'py.test'}
        self.subject.invoke_async.return_value = evt
        ret = asyncio.run(Handler.invoke_with_timeout(self.subject, evt))
        self.subject.invoke_async.assert_awaited_once_with(evt, None)
        assert ret == evt

    @mock.patch('asyncio.wait_for')
    def test_invoke_with_timeout_err(self, mock_wait):
        mock_wait.side_effect = asyncio.TimeoutError
        evt = {'text': 'py.test'}
        ret = asyncio.run(Handler.invoke_with_timeout(self.subject, evt))
        assert ret == {
            'body': json.dumps({'Error': 'TIMEOUT'}),
            'statusCode': 408,
        }

    def test_invoke(self):
        pass


def test_get_opts():
    sys.argv = [
        'lambda-gateway',
        '-b', '0.0.0.0',
        '-p', '8888',
        '-t', '3',
        'index.handler',
    ]
    opts = server.get_opts()
    assert opts.bind == '0.0.0.0'
    assert opts.port == 8888
    assert opts.timeout == 3
    assert opts.HANDLER == 'index.handler'


@pytest.mark.parametrize(
    ('signature', 'exp'),
    [
        ('lambda_function.lambda_handler', 'lambda_handler'),
    ]
)
def test_get_handler(signature, exp):
    ret = server.get_handler(signature).__name__
    assert ret == exp


def test_get_handler_bad_sig():
    with pytest.raises(SystemExit):
        server.get_handler('lambda_function')


def test_get_handler_no_file():
    with pytest.raises(SystemExit):
        server.get_handler('not_a_file.handler')


def test_get_handler_no_handler():
    with pytest.raises(SystemExit):
        server.get_handler('lambda_function.not_a_function')


def test_setup():
    server.setup('0.0.0.0', 8000, 30, 'index.handler')
    assert Handler.timeout == 30
    assert Handler.handler == 'index.handler'


@mock.patch('http.server.ThreadingHTTPServer')
def test_run(mock_httpd):
    mock_httpd.socket.getsockname.return_value = ['host', 8000]
    server.run(mock_httpd)
    mock_httpd.serve_forever.assert_called_once_with()


@mock.patch('http.server.ThreadingHTTPServer')
def test_run_int(mock_httpd):
    mock_httpd.socket.getsockname.return_value = ['host', 8000]
    mock_httpd.serve_forever.side_effect = KeyboardInterrupt
    server.run(mock_httpd)
    mock_httpd.serve_forever.assert_called_once_with()
    mock_httpd.shutdown.assert_called_once_with()


@mock.patch('http.server.ThreadingHTTPServer.__enter__')
@mock.patch('lambda_gateway.server.run')
@mock.patch('lambda_gateway.server.setup')
@mock.patch('lambda_gateway.server.get_opts')
def test_main(mock_opts, mock_setup, mock_run, mock_httpd):
    mock_httpd.return_value = '<httpd>'
    mock_setup.return_value = (
        http.server.ThreadingHTTPServer,
        ('localhost', 8000),
        Handler,
    )
    server.main()
    mock_run.assert_called_once_with('<httpd>')
