#!/usr/bin/env python3
# usage:
#   python server.py --help
import argparse
import asyncio
import importlib
import json
import os
import socketserver
from http import server

from lambda_gateway import lambda_context


class LambdaRequestHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.invoke('GET')

    def do_HEAD(self):
        self.invoke('HEAD')

    def do_POST(self):
        self.invoke('POST')

    def get_event(self, httpMethod):
        """ Get Lambda input event object.

            :param str httpMethod: HTTP request method
            :return dict: Lambda event object
        """
        # Get body
        try:
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length).decode()
        except TypeError:
            body = ''

        # Construct event
        return {
            'body': body,
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
        return type(self).handler(event, context)

    async def invoke_with_timeout(self, event, context=None):
        """ Wrapper to invoke the Lambda handler with a timeout.

            :param dict event: Lambda event object
            :param Context context: Mock Lambda context
            :returns dict: Lamnda invocation result or 408 TIMEOUT
        """
        try:
            return await asyncio.wait_for(
                self.invoke_async(event, context),
                self.timeout,
            )
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
    parser = argparse.ArgumentParser(description='Start a simple PyPI server')
    parser.add_argument(
        '-b', '--base-path',
        dest='base_path',
        help='Base path.',
    )
    parser.add_argument(
        '-H', '--host',
        dest='host',
        default='localhost',
        help='Hostname.',
    )
    parser.add_argument(
        '-p', '--port',
        dest='port',
        default='8000',
        help='Port number.',
        type=int,
    )
    parser.add_argument(
        '-t', '--timeout',
        dest='timeout',
        default=30,
        help='Lambda timeout.',
        type=int,
    )
    parser.add_argument('HANDLER', help='Lambda handler signature.')
    return parser.parse_args()


def get_url(host, port, base_path=None):
    """ Get URL of service. """
    url = f'http://{host}'
    if port != 80:
        url += f':{port}'
    if base_path:
        url += f'/{base_path}'
    url += '/'
    return url


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


def run():
    """ Run Lambda Gateway server. """
    opts = get_opts()
    url = get_url(opts.host, opts.port, opts.base_path)
    server_address = (opts.host, opts.port)
    LambdaRequestHandler.set_handler(get_handler(opts.HANDLER))
    LambdaRequestHandler.set_timeout(opts.timeout)
    with socketserver.TCPServer(server_address, LambdaRequestHandler) as httpd:
        print(f'Starting LambdaRequestHandler at {url}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nStopping LambdaRequestHandler')
        finally:
            httpd.shutdown()


if __name__ == '__main__':
    run()
