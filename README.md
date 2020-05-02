# Lambda Gateway

[![PyPI Version](https://badge.fury.io/py/lambda-gateway.svg)](https://badge.fury.io/py/lambda-gateway)

Test AWS Lambda functions invoked as API Gateway proxy integrations locally.

This tool extends the native Python SimpleHTTPRequestHandler to proxy requests to a local Lambda function.

After installing, navigate to the directory where your Lambda function is defined and invoke it with the CLI tool using the configured handler, eg:

```bash
lambda-gateway [-p PORT] lambda_function.lambda_handler
# => Starting LambdaRequestHandler at http://localhost:8000/
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


def lambda_handler(event, context):
    return {
        'headers': {
            'Content-Type': 'application/json',
        },
        'statusCode': 200,
        'body': json.dumps({'text': 'Hello from Lambda Gateway!'})
    }
```

Start a local server with the signature of your Lambda handler as the argument.

_Note — the handler must be importable from the current working directory_

```bash
lambda-gateway [-H HOST] [-p PORT] [-b BASE_PATH] lambda_function.lambda_handler
# => Starting LambdaRequestHandler at http://localhost:8000/
```

Test the function with cURL.

```bash
curl http://localhost:8000/
# => {"text": "Hello from Lambda Gateway!"}
```
