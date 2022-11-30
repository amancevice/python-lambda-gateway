"""
Example Lambda handler function.
"""
import json
import os
import time

SLEEP = os.getenv("SLEEP") or "0"


def lambda_handler(event, context=None):
    # Log event...
    print(json.dumps(event))
    # Do some work...
    time.sleep(float(SLEEP))
    # Get name from qs
    params = event.get("queryStringParameters") or {}
    name = params.get("name") or "Pythonista"
    # Return response
    return {
        "body": json.dumps({"text": f"Hello, {name}! ~ Lambda Gateway"}),
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
    }
