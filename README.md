# Lambda Gateway

[![pypi](https://img.shields.io/pypi/v/lambda-gateway?color=yellow&logo=python&logoColor=eee&style=flat-square)](https://pypi.org/project/lambda-gateway/)
[![python](https://img.shields.io/pypi/pyversions/lambda-gateway?logo=python&logoColor=eee&style=flat-square)](https://pypi.org/project/lambda-gateway/)
[![pytest](https://img.shields.io/github/workflow/status/amancevice/python-lambda-gateway/pytest?logo=github&style=flat-square)](https://github.com/amancevice/python-lambda-gateway/actions)
[![coverage](https://img.shields.io/codeclimate/coverage/amancevice/python-lambda-gateway?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/python-lambda-gateway/test_coverage)
[![maintainability](https://img.shields.io/codeclimate/maintainability/amancevice/python-lambda-gateway?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/python-lambda-gateway/maintainability)

Test AWS Lambda functions invoked as API Gateway proxy integrations locally.

This tool extends the native Python SimpleHTTPRequestHandler to proxy requests to a local Lambda function using the ThreadingHTTPServer.

This tool is was specifically implemented to use the standard Python library only. No additional pip installation is required.

After installing, navigate to the directory where your Lambda function is defined and invoke it with the CLI tool using the configured handler, eg:

```bash
lambda-gateway [-p PORT] [-t SECONDS] lambda_function.lambda_handler
# => Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

## Installation

Install with pip.

```bash
pip install lambda-gateway
```

## Usage

Create a Lambda function handler in Python 3

```python
# ./lambda_function.py
import json


def lambda_handler(event, context=None):
    # Get name from qs
    params = event.get('queryStringParameters') or {}
    name = params.get('name') or 'Pythonista'
    # Return response
    return {
        'body': json.dumps({'text': f'Hello, {name}! ~ Lambda Gateway'}),
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
```

Start a local server with the signature of your Lambda handler as the argument.

_Note — the handler must be importable from the current working directory_

```bash
lambda-gateway [-B PATH] [-b ADDR] [-p PORT] [-t SECONDS] lambda_function.lambda_handler
# => Starting LambdaRequestHandler at http://localhost:8000/
```

Test the function with cURL.

```bash
curl http://localhost:8000/?name=Pythonista
# => {"text": "Hello, Pythonista! ~ Lambda Gateway"}
```

## Timeouts

API Gateway imposes a 30 second timeout on Lambda responses. This constraint is implemented in this project using Python's async/await syntax.

The timeout length can be adjusted using the `-t / --timeout` CLI option.

```bash
lambda-gateway -t 3 lambda_function.lambda_handler
```

## API Gateway Payloads

API Gateway supports [two versions](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html) of proxied JSON payloads to Lambda integrations, `1.0` and `2.0`.

Versions `0.8+` of Lambda Gateway use `2.0` by default, but this can be changed at startup time using the `-V / --payload-version` option:

```bash
lambda-gateway -V1.0 lambda_function.lambda_handler
```
