import json

from lambda_function import lambda_handler


def test_lambda_handler():
    ret = lambda_handler({})
    exp = {
        "body": json.dumps({"text": "Hello, Pythonista! ~ Lambda Gateway"}),
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
    }
    assert ret == exp
