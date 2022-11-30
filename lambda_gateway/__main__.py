#!/usr/bin/env python3
# usage:
#   python server.py --help
import argparse
import os
import socket
import sys
from http import server

from lambda_gateway.event_proxy import EventProxy
from lambda_gateway.request_handler import LambdaRequestHandler

from lambda_gateway import __version__


def get_best_family(*address):  # pragma: no cover
    """
    Helper for Python 3.7 compat.

    :params tuple address: host/port tuple
    """
    # Python 3.8+
    try:
        return server._get_best_family(*address)

    # Python 3.7 -- taken from http.server._get_best_family() in 3.8
    except AttributeError:
        infos = socket.getaddrinfo(
            *address,
            type=socket.SOCK_STREAM,
            flags=socket.AI_PASSIVE,
        )
        family, type, proto, canonname, sockaddr = next(iter(infos))
        return family, sockaddr


def get_opts():
    """
    Get CLI options.
    """
    parser = argparse.ArgumentParser(
        prog="lambda-gateway",
        description="Start a simple Lambda Gateway server",
    )
    parser.add_argument(
        "-B",
        "--base-path",
        dest="base_path",
        help="Set base path for REST API",
        metavar="PATH",
    )
    parser.add_argument(
        "-b",
        "--bind",
        dest="bind",
        metavar="ADDR",
        help="Specify alternate bind address [default: all interfaces]",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        default=8000,
        help="Specify alternate port [default: 8000]",
        type=int,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        help="Lambda timeout.",
        metavar="SECONDS",
        type=int,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="Print version and exit",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-V",
        "--payload-version",
        choices=["1.0", "2.0"],
        default="2.0",
        help="API Gateway payload version [default: 2.0]",
    )
    parser.add_argument(
        "HANDLER",
        help="Lambda handler signature",
    )
    return parser.parse_args()


def run(httpd, base_path="/"):
    """
    Run Lambda Gateway server.

    :param object httpd: ThreadingHTTPServer instance
    :param str base_path: REST API base path
    """
    host, port = httpd.socket.getsockname()[:2]
    url_host = f"[{host}]" if ":" in host else host
    sys.stderr.write(
        f"Serving HTTP on {host} port {port} "
        f"(http://{url_host}:{port}{base_path}) ...\n"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("\nKeyboard interrupt received, exiting.\n")
    finally:
        httpd.shutdown()


def main():
    """
    Main entrypoint.
    """
    # Parse opts
    opts = get_opts()

    # Ensure base_path is wrapped in slashes
    base_path = os.path.join("/", str(opts.base_path or ""), "")

    # Setup handler
    address_family, addr = get_best_family(opts.bind, opts.port)
    proxy = EventProxy(opts.HANDLER, base_path, opts.timeout)
    LambdaRequestHandler.set_proxy(proxy, opts.payload_version)
    server.ThreadingHTTPServer.address_family = address_family

    # Start server
    with server.ThreadingHTTPServer(addr, LambdaRequestHandler) as httpd:
        run(httpd, base_path)


if __name__ == "__main__":  # pragma: no cover
    main()
