import sys
from unittest import mock

from lambda_gateway import __main__


def test_get_opts_default():
    sys.argv = [
        "lambda-gateway",
        "index.handler",
    ]
    opts = __main__.get_opts()
    assert opts.bind is None
    assert opts.port == 8000
    assert opts.timeout is None
    assert opts.HANDLER == "index.handler"


def test_get_opts():
    sys.argv = [
        "lambda-gateway",
        "-b",
        "0.0.0.0",
        "-p",
        "8888",
        "-t",
        "3",
        "index.handler",
    ]
    opts = __main__.get_opts()
    assert opts.bind == "0.0.0.0"
    assert opts.port == 8888
    assert opts.timeout == 3
    assert opts.HANDLER == "index.handler"


@mock.patch("http.server.ThreadingHTTPServer")
def test_run(mock_httpd):
    mock_httpd.socket.getsockname.return_value = ["host", 8000]
    __main__.run(mock_httpd)
    mock_httpd.serve_forever.assert_called_once_with()


@mock.patch("http.server.ThreadingHTTPServer")
def test_run_int(mock_httpd):
    mock_httpd.socket.getsockname.return_value = ["host", 8000]
    mock_httpd.serve_forever.side_effect = KeyboardInterrupt
    __main__.run(mock_httpd)
    mock_httpd.serve_forever.assert_called_once_with()
    mock_httpd.shutdown.assert_called_once_with()


@mock.patch("http.server.ThreadingHTTPServer.__enter__")
@mock.patch("lambda_gateway.__main__.run")
def test_main(mock_run, mock_httpd):
    sys.argv = [
        "lambda-gateway",
        "-B",
        "simple",
        "index.handler",
    ]
    mock_httpd.return_value = "<httpd>"
    __main__.main()
    mock_run.assert_called_once_with("<httpd>", "/simple/")
