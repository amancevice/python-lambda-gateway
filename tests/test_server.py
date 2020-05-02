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
