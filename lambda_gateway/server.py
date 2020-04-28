#!/usr/bin/env python3
# usage:
#   python server.py --help
import argparse
import importlib
import os
import socketserver
from http import server


class LambdaRequestHandler(server.SimpleHTTPRequestHandler):
    def invoke(self, httpMethod):
        # Get body
        try:
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length).decode()
        except TypeError:
            body = ''

        # Construct event
        event = {
            'body': body,
            'headers': dict(self.headers),
            'httpMethod': httpMethod,
            'path': self.path,
        }

        # Get response
        response = LambdaRequestHandler.handler(event)
        status = response.get('statusCode')
        headers = response.get('headers')
        body = response.get('body')

        # Send response
        self.send_response(status)
        for key, val in headers.items():
            self.send_header(key, val)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        self.invoke('GET')

    def do_HEAD(self):
        self.invoke('HEAD')

    def do_POST(self):
        self.invoke('POST')


def get_opts():
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
    parser.add_argument('HANDLER', help='Lambda handler signature.')
    return parser.parse_args()


def get_url(host, port, base_path=None):
    url = f'http://{host}'
    if port != 80:
        url += f':{port}'
    if base_path:
        url += f'/{base_path}'
    url += '/'
    return url


def get_handler(signature):
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
    opts = get_opts()
    url = get_url(opts.host, opts.port, opts.base_path)
    server_address = (opts.host, opts.port)
    LambdaRequestHandler.handler = get_handler(opts.HANDLER)
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
