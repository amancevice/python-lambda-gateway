"""
Example Lambda handler function.
"""
import json


def lambda_handler(event, context):
    return {
        'headers': {
            'Content-Type': 'application/json',
        },
        'statusCode': 200,
        'body': json.dumps({'text': 'Hello from Lambda Gateway!'})
    }
