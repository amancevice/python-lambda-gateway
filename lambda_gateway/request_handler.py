from urllib import parse
from http.server import SimpleHTTPRequestHandler


class LambdaRequestHandler(SimpleHTTPRequestHandler):
    def do_DELETE(self):
        self.invoke("DELETE")

    def do_GET(self):
        self.invoke("GET")

    def do_HEAD(self):
        self.invoke("HEAD")

    def do_OPTIONS(self):
        self.invoke("OPTIONS")

    def do_PATCH(self):
        self.invoke("PATCH")

    def do_POST(self):
        self.invoke("POST")

    def do_PUT(self):
        self.invoke("PUT")

    def get_body(self):
        """
        Get request body to forward to Lambda handler.
        """
        try:
            content_length = int(self.headers.get("Content-Length"))
            return self.rfile.read(content_length).decode()
        except TypeError:
            return ""

    def get_event(self, httpMethod):
        """
        Get Lambda input event object.

        :param str httpMethod: HTTP request method
        :return dict: Lambda event object
        """
        if self.version == "1.0":
            return self.get_event_v1(httpMethod)
        elif self.version == "2.0":
            return self.get_event_v2(httpMethod)
        raise ValueError(  # pragma: no cover
            f"Unknown API Gateway payload version: {self.version}"
        )

    def get_event_v1(self, httpMethod):
        """
        Get Lambda input event object (v1).

        :param str httpMethod: HTTP request method
        :return dict: Lambda event object
        """
        url = parse.urlparse(self.path)
        path, *_ = url.path.split("?")
        return {
            "version": "1.0",
            "body": self.get_body(),
            "headers": dict(self.headers),
            "httpMethod": httpMethod,
            "path": path,
            "queryStringParameters": dict(parse.parse_qsl(url.query)),
        }

    def get_event_v2(self, httpMethod):
        """
        Get Lambda input event object (v2).

        :param str httpMethod: HTTP request method
        :return dict: Lambda event object
        """
        url = parse.urlparse(self.path)
        path, *_ = url.path.split("?")
        route_key = self.headers.get("x-route-key") or f"{httpMethod} {path}"
        return {
            "version": "2.0",
            "body": self.get_body(),
            "routeKey": route_key,
            "rawPath": path,
            "rawQueryString": url.query,
            "headers": dict(self.headers),
            "queryStringParameters": dict(parse.parse_qsl(url.query)),
            "requestContext": {
                "http": {
                    "method": httpMethod,
                    "path": path,
                },
            },
        }

    def invoke(self, httpMethod):
        """
        Proxy requests to Lambda handler

        :param dict event: Lambda event object
        :param Context context: Mock Lambda context
        :returns dict: Lamnda invocation result
        """
        # Get Lambda event
        event = self.get_event(httpMethod)

        # Get Lambda result
        res = self.proxy.invoke(event)

        # Parse response
        status = res.get("statusCode") or 500
        headers = res.get("headers") or {}
        body = res.get("body") or ""

        # Send response
        self.send_response(status)
        for key, val in headers.items():
            self.send_header(key, val)
        self.end_headers()
        self.wfile.write(body.encode())

    @classmethod
    def set_proxy(cls, proxy, version):
        """
        Set up LambdaRequestHandler.
        """
        cls.proxy = proxy
        cls.version = version
