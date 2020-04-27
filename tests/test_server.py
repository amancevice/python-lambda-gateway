import pytest

from lambda_gateway import server


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
