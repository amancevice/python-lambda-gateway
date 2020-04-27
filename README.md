# Lambda Gateway

Simple HTTP server to invoke a Lambda function locally

## Installation

Install with pip.

```bash
pip install lambda-gateway
```

## Usage

Start a local server with the signature of your Lambda handler as the argument.

_Note — the handler must be importable from the current working directory_

```bash
lambda-gateway [-H host] [-p port] [-b base_path] 'index.handler'
```

Test the function with cURL.

```bash
curl http://localhost:8000/ | jq
# {
#   "text": "Hello from Lambda Gateway!"
#  }
```
