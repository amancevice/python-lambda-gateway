"""
Example Lambda handler function.
"""


def handler(event, context=None):
    """ Handle Lambda event. """
    return {
        'headers': {
            'Content-Type': 'application/json',
        },
        'statusCode': 200,
        'body': '{"text": "Hello from Lambda Gateway!"}'
    }
