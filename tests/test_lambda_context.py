from datetime import timedelta

from lambda_gateway import lambda_context
from lambda_gateway.lambda_context import Context


def test_start():
    with lambda_context.start(11) as ret:
        assert isinstance(ret, Context)
        assert ret._timeout == 11


class TestContext:
    def setup_method(self):
        self.subject = Context(1)

    def test_function_name(self):
        assert self.subject.function_name == "lambda-gateway"

    def test_function_version(self):
        assert self.subject.function_version == "$LATEST"

    def test_invoked_function_arn(self):
        assert (
            self.subject.invoked_function_arn
            == "arn:aws:lambda:us-east-1:123456789012:function:lambda-gateway"
        )

    def test_memory_limit_in_mb(self):
        assert self.subject.memory_limit_in_mb == 128

    def test_aws_request_id(self):
        assert self.subject.aws_request_id is not None

    def test_log_group_name(self):
        assert self.subject.log_group_name == "/aws/lambda/lambda-gateway"

    def test_log_stream_name(self):
        assert self.subject.log_stream_name is not None

    def test_get_remaining_time_in_millis(self):
        assert 0 < self.subject.get_remaining_time_in_millis() < 1000
        self.subject._start -= timedelta(seconds=1)
        assert self.subject.get_remaining_time_in_millis() == 0
