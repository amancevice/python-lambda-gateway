from http.server import SimpleHTTPRequestHandler


class LambdaRequestHandler(SimpleHTTPRequestHandler):
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

    def invoke(self, httpMethod):
        """ Proxy requests to Lambda handler

            :param dict event: Lambda event object
            :param Context context: Mock Lambda context
            :returns dict: Lamnda invocation result
        """
        # Get Lambda event
        event = self.get_event(httpMethod)

        # Get Lambda result
        res = self.proxy.invoke(event)

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
    def set_proxy(cls, proxy):
        cls.proxy = proxy
