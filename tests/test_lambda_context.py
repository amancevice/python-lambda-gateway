from datetime import timedelta

from lambda_gateway import lambda_context


def test_start():
    with lambda_context.start(11) as ret:
        assert isinstance(ret, lambda_context.Context)
        assert ret._timeout == 11


def test_function_name():
    assert lambda_context.Context().function_name == 'lambda-gateway'


def test_function_version():
    assert lambda_context.Context().function_version == '$LATEST'


def test_invoked_function_arn():
    assert lambda_context.Context().invoked_function_arn == \
        'arn:aws:lambda:us-east-1:123456789012:function:lambda-gateway'


def test_memory_limit_in_mb():
    assert lambda_context.Context().memory_limit_in_mb == 128


def test_aws_request_id():
    assert lambda_context.Context().aws_request_id is not None


def test_log_group_name():
    assert lambda_context.Context().log_group_name == \
        '/aws/lambda/lambda-gateway'


def test_log_stream_name():
    assert lambda_context.Context().log_stream_name is not None


def test_get_remaining_time_in_millis():
    context = lambda_context.Context(1)
    assert 0 < context.get_remaining_time_in_millis() < 1000
    context._start -= timedelta(seconds=1)
    assert context.get_remaining_time_in_millis() == 0
