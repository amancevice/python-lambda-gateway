"""
Example Lambda handler function.
"""
import json
import os
import time

SLEEP = os.getenv('SLEEP') or '0'


def lambda_handler(event, context=None):
    # Log event...
    print(json.dumps(event))
    # Do some work...
    time.sleep(float(SLEEP))
    # Return response
    return {
        'body': json.dumps({'text': 'Hello from Lambda Gateway!'}),
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
