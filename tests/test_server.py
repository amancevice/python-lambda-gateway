import http
import types
from unittest import mock

import pytest

from lambda_gateway import server


class TestLambdaRequestHandler:
    def test_set_handler(self):
        handler = 'lambda_function.lambda_handler'
        server.LambdaRequestHandler.set_handler(handler)
        assert server.LambdaRequestHandler.handler == handler

    def test_set_timeout(self):
        server.LambdaRequestHandler.set_timeout(11)
        assert server.LambdaRequestHandler.timeout == 11


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


@mock.patch('lambda_gateway.server.get_opts')
def test_setup(mock_opts):
    mock_opts.return_value = types.SimpleNamespace(
        HANDLER='lambda_function.lambda_handler',
        bind=None,
        port=8000,
        timeout=30,
    )
    server.setup()
    assert server.LambdaRequestHandler.timeout == 30
    assert server.LambdaRequestHandler.handler == \
        'lambda_function.lambda_handler'


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
def test_main(mock_setup, mock_run, mock_httpd):
    mock_httpd.return_value = '<httpd>'
    mock_setup.return_value = (
        http.server.ThreadingHTTPServer,
        ('localhost', 8000),
        server.LambdaRequestHandler,
    )
    server.main()
    mock_run.assert_called_once_with('<httpd>')
