#!/usr/bin/env python3
# usage:
#   python server.py --help
import argparse
import asyncio
import importlib
import json
import os
from http import server

from lambda_gateway import lambda_context


class LambdaRequestHandler(server.SimpleHTTPRequestHandler):
    timeout = 30

    def do_GET(self):
        self.invoke('GET')

    def do_HEAD(self):
        self.invoke('HEAD')

    def do_POST(self):
        self.invoke('POST')

    def get_body(self):
        """ Get request body to forward to Lambda handler. """
        try:
            content_length = int(self.headers.get('Content-Length'))
            return self.rfile.read(content_length).decode()
        except TypeError:
            return ''

    def get_event(self, httpMethod):
        """ Get Lambda input event object.

            :param str httpMethod: HTTP request method
            :return dict: Lambda event object
        """
        return {
            'body': self.get_body(),
            'headers': dict(self.headers),
            'httpMethod': httpMethod,
            'path': self.path,
        }

    async def invoke_async(self, event, context=None):
        """ Wrapper to invoke the Lambda handler asynchronously.

            :param dict event: Lambda event object
            :param Context context: Mock Lambda context
            :returns dict: Lamnda invocation result
        """
        # await asyncio.sleep(31)
        handler = get_handler(self.handler)
        return handler(event, context)

    async def invoke_with_timeout(self, event, context=None):
        """ Wrapper to invoke the Lambda handler with a timeout.

            :param dict event: Lambda event object
            :param Context context: Mock Lambda context
            :returns dict: Lamnda invocation result or 408 TIMEOUT
        """
        try:
            coroutine = self.invoke_async(event, context)
            return await asyncio.wait_for(coroutine, self.timeout)
        except asyncio.TimeoutError:
            return {
                'body': json.dumps({'Error': 'TIMEOUT'}),
                'statusCode': 408,
            }

    def invoke(self, httpMethod):
        """ Proxy requests to Lambda handler

            :param dict event: Lambda event object
            :param Context context: Mock Lambda context
            :returns dict: Lamnda invocation result
        """
        # Get Lambda event
        event = self.get_event(httpMethod)

        # Get Lambda result
        with lambda_context.start(self.timeout) as context:
            res = asyncio.run(self.invoke_with_timeout(event, context))

        # Parse response
        status = res.get('statusCode', 500)
        headers = res.get('headers', {})
        body = res.get('body', '')

        # Send response
        self.send_response(status)
        for key, val in headers.items():
            self.send_header(key, val)
        self.end_headers()
        self.wfile.write(body.encode())

    @classmethod
    def set_handler(cls, handler):
        """ Set Lambda handler for server.

            :param function handler: Lambda handler function
        """
        cls.handler = handler

    @classmethod
    def set_timeout(cls, timeout):
        """ Set Lambda context timeout.

            :param int timouet: Lambda context timeout in seconds
        """
        cls.timeout = timeout


def get_opts():
    """ Get CLI options. """
    parser = argparse.ArgumentParser(
        description='Start a simple Lambda Gateway server',
    )
    parser.add_argument(
        '-b', '--bind',
        dest='bind',
        metavar='ADDRESS',
        help='Specify alternate bind address [default: all interfaces]',
    )
    parser.add_argument(
        '-p', '--port',
        dest='port',
        default=8000,
        help='Specify alternate port [default: 8000]',
        type=int,
    )
    parser.add_argument(
        '-t', '--timeout',
        dest='timeout',
        default=30,
        help='Lambda timeout.',
        type=int,
    )
    parser.add_argument(
        'HANDLER',
        help='Lambda handler signature',
    )
    return parser.parse_args()


def get_handler(signature):
    """ Load handler function.

        :param str signature: Lambda handler signature (eg, 'index.handler')
        :returns function: Lambda handler function
    """
    *path, func = signature.split('.')
    name = '.'.join(path)
    if not name:
        raise SystemExit(f"Bad handler signature '{signature}'")
    try:
        pypath = os.path.join(os.path.curdir, f'{name}.py')
        spec = importlib.util.spec_from_file_location(name, pypath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, func)
    except FileNotFoundError:
        raise SystemExit(f"Unable to import module '{name}'")
    except AttributeError:
        raise SystemExit(f"Handler '{func}' missing on module '{name}'")


def setup(bind, port, timeout, handler):
    """ Setup server. """
    address_family, addr = server._get_best_family(bind, port)
    LambdaRequestHandler.set_handler(handler)
    LambdaRequestHandler.set_timeout(timeout)
    server.ThreadingHTTPServer.address_family = address_family
    return (server.ThreadingHTTPServer, addr, LambdaRequestHandler)


def run(httpd):
    """ Run Lambda Gateway server.

        :param object httpd: ThreadingHTTPServer instance
    """
    host, port = httpd.socket.getsockname()[:2]
    url_host = f'[{host}]' if ':' in host else host
    print(
        f'Serving HTTP on {host} port {port} '
        f'(http://{url_host}:{port}/) ...'
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')
    finally:
        httpd.shutdown()


def main():
    """ Main entrypoint. """
    opts = get_opts()
    bind = opts.bind
    port = opts.port
    timeout = opts.timeout
    handler = opts.HANDLER
    HTTPServer, addr, Handler = setup(bind, port, timeout, handler)
    with HTTPServer(addr, Handler) as httpd:
        run(httpd)


if __name__ == '__main__':  # pragma: no cover
    main()
