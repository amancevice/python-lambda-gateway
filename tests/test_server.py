import pytest

from lambda_gateway import server


class TestLambdaRequestHandler:
    def test_set_handler(self):
        def func(event, context):
            pass

        server.LambdaRequestHandler.set_handler(func)
        assert server.LambdaRequestHandler.handler == func

    def test_set_timeout(self):
        server.LambdaRequestHandler.set_timeout(11)
        assert server.LambdaRequestHandler.timeout == 11


@pytest.mark.parametrize(
    ('host', 'port', 'base_path', 'exp'),
    [
        ('localhost', 8000, None, 'http://localhost:8000/'),
        ('localhost', 80, None, 'http://localhost/'),
        ('localhost', 8000, 'base', 'http://localhost:8000/base/'),
        ('localhost', 80, 'base', 'http://localhost/base/'),
    ]
)
def test_get_url(host, port, base_path, exp):
    ret = server.get_url(host, port, base_path)
    assert ret == exp


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
