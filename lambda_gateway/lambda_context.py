import uuid
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def start(timeout=None):
    """
    Yield mock Lambda context object.
    """
    yield Context(timeout)


class Context:
    """
    Mock Lambda context object.

    :param int timeout: Lambda timeout in seconds
    """

    def __init__(self, timeout=None):
        self._start = datetime.utcnow()
        self._timeout = timeout or 30

    @property
    def function_name(self):
        return "lambda-gateway"

    @property
    def function_version(self):
        return "$LATEST"

    @property
    def invoked_function_arn(self):
        account_id = "123456789012"
        region = "us-east-1"
        function_name = self.function_name
        return f"arn:aws:lambda:{region}:{account_id}:function:{function_name}"

    @property
    def memory_limit_in_mb(self):
        return 128

    @property
    def aws_request_id(self):
        return str(uuid.uuid1())

    @property
    def log_group_name(self):
        return "/aws/lambda/lambda-gateway"

    @property
    def log_stream_name(self):
        return str(uuid.uuid1())

    def get_remaining_time_in_millis(self):
        """
        Get remaining TTL for Lambda context.
        """
        delta = datetime.utcnow() - self._start
        remaining_time_in_s = self._timeout - delta.total_seconds()
        if remaining_time_in_s < 0:
            return 0
        return remaining_time_in_s * 1000
