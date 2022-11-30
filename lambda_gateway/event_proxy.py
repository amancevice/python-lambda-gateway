import asyncio
import importlib
import json
import os
import sys

from lambda_gateway import lambda_context, logger


class EventProxy:
    def __init__(self, handler, base_path, timeout=None):
        self.base_path = base_path
        self.handler = handler
        self.timeout = timeout

    def get_handler(self):
        """
        Load handler function.

        :returns function: Lambda handler function
        """
        *path, func = self.handler.split(".")
        name = ".".join(path)
        if not name:
            raise ValueError(f"Bad handler signature '{self.handler}'")
        try:
            sys.path.append(os.path.curdir)
            module = importlib.import_module(name)
            handler = getattr(module, func)
            return handler
        except ModuleNotFoundError:
            raise ValueError(f"Unable to import module '{name}'")
        except AttributeError:
            raise ValueError(f"Handler '{func}' missing on module '{name}'")

    def get_httpMethod(self, event):
        """
        Helper to get httpMethod from v1 or v2 events.
        """
        if event.get("version") == "2.0":
            return event["requestContext"]["http"]["method"]
        elif event.get("version") == "1.0":
            return event["httpMethod"]
        raise ValueError(  # pragma: no cover
            f"Unknown API Gateway payload version: {event.get('version')}"
        )

    def get_path(self, event):
        """
        Helper to get path from v1 or v2 events.
        """
        if event.get("version") == "2.0":
            return event["rawPath"]
        elif event.get("version") == "1.0":
            return event["path"]
        raise ValueError(  # pragma: no cover
            f"Unknown API Gateway payload version: {event.get('version')}"
        )

    def invoke(self, event):
        with lambda_context.start(self.timeout) as context:
            logger.info('Invoking "%s"', self.handler)
            return asyncio.run(self.invoke_async_with_timeout(event, context))

    async def invoke_async(self, event, context=None):
        """
        Wrapper to invoke the Lambda handler asynchronously.

        :param dict event: Lambda event object
        :param Context context: Mock Lambda context
        :returns dict: Lamnda invocation result
        """
        httpMethod = self.get_httpMethod(event)
        path = self.get_path(event)

        # Reject request if not starting at base path
        if not path.startswith(self.base_path):
            err = f"Rejected {path} :: Base path is {self.base_path}"
            logger.error(err)
            return self.jsonify(httpMethod, 403, message="Forbidden")

        # Get & invoke Lambda handler
        try:
            handler = self.get_handler()
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, handler, event, context)
        except Exception as err:
            logger.error(err)
            message = "Internal server error"
            return self.jsonify(httpMethod, 502, message=message)

    async def invoke_async_with_timeout(self, event, context=None):
        """
        Wrapper to invoke the Lambda handler with a timeout.

        :param dict event: Lambda event object
        :param Context context: Mock Lambda context
        :returns dict: Lamnda invocation result or 408 TIMEOUT
        """
        try:
            coroutine = self.invoke_async(event, context)
            return await asyncio.wait_for(coroutine, self.timeout)
        except asyncio.TimeoutError:
            httpMethod = self.get_httpMethod(event)
            message = "Endpoint request timed out"
            return self.jsonify(httpMethod, 504, message=message)

    @staticmethod
    def jsonify(httpMethod, statusCode, **kwargs):
        """
        Convert dict into API Gateway response object.

        :params str httpMethod: HTTP request method
        :params int statusCode: Response status code
        :params dict kwargs: Response object
        """
        body = "" if httpMethod in ["HEAD"] else json.dumps(kwargs)
        return {
            "body": body,
            "statusCode": statusCode,
            "headers": {
                "Content-Type": "application/json",
                "Content-Length": len(body),
            },
        }
