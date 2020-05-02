"""
Example Lambda handler function.
"""
import json


def lambda_handler(event, context=None):
    return {
        'body': json.dumps({'text': 'Hello from Lambda Gateway!'}),
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
