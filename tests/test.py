import datetime
import logging
import os
import socket

import click
from werkzeug._compat import reraise
from werkzeug.exceptions import InternalServerError
from werkzeug.serving import WSGIRequestHandler
from werkzeug.urls import uri_to_iri

from server import create_app


class TestRequestHandler(WSGIRequestHandler):
    def log(self, type, message, *args):
        _logger = logging.getLogger("werkzeug")

        if _logger.level > 15:
            _logger.setLevel(15)

        message = "%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), message % args)
        _logger.log(logging.getLevelName(type.upper()), message.rstrip())

    def log_date_time_string(self) -> str:
        return datetime.datetime.now().isoformat(sep=' ')

    def send_response(self, code, message=None):
        """Send the response header and log the response code."""
        if message is None:
            message = code in self.responses and self.responses[code][0] or ""
        if self.request_version != "HTTP/0.9":
            hdr = "%s %d %s\r\n" % (self.protocol_version, code, message)
            self.wfile.write(hdr.encode("ascii"))

    def log_request(self, code="-", size="-"):
        try:
            path = uri_to_iri(self.path)
            msg = "%s %s %s" % (self.command, path, self.request_version)
        except AttributeError:
            # path isn't set if the requestline was bad
            msg = self.requestline

        code = str(code)

        if click:
            color = click.style

            if code[0] == "1":  # 1xx - Informational
                msg = color(msg, bold=True)
            elif code[0] == "2":  # 2xx - Success
                msg = color(msg, fg="white")
            elif code == "304":  # 304 - Resource Not Modified
                msg = color(msg, fg="cyan")
            elif code[0] == "3":  # 3xx - Redirection
                msg = color(msg, fg="green")
            elif code == "404":  # 404 - Resource Not Found
                msg = color(msg, fg="yellow")
            elif code[0] == "4":  # 4xx - Client Error
                msg = color(msg, fg="red", bold=True)
            else:  # 5xx, or any other response
                msg = color(msg, fg="magenta", bold=True)

        self.log("access", '"%s" %s %s', msg, code, size)

    def run_wsgi(self):
        if self.headers.get("Expect", "").lower().strip() == "100-continue":
            self.wfile.write(b"HTTP/1.1 100 Continue\r\n\r\n")

        self.environ = environ = self.make_environ()
        headers_set = []
        headers_sent = []

        def write(data):
            assert headers_set, "write() before start_response"
            if not headers_sent:
                status, response_headers = headers_sent[:] = headers_set
                try:
                    code, msg = status.split(None, 1)
                except ValueError:
                    code, msg = status, ""
                code = int(code)
                self.log_request(code, data.__len__())
                self.send_response(code, msg)
                header_keys = set()
                for key, value in response_headers:
                    self.send_header(key, value)
                    key = key.lower()
                    header_keys.add(key)
                if not (
                    "content-length" in header_keys
                    or environ["REQUEST_METHOD"] == "HEAD"
                    or code < 200
                    or code in (204, 304)
                ):
                    self.close_connection = True
                    self.send_header("Connection", "close")
                if "server" not in header_keys:
                    self.send_header("Server", self.version_string())
                if "date" not in header_keys:
                    self.send_header("Date", self.date_time_string())
                self.end_headers()

            assert isinstance(data, bytes), "applications must write bytes"
            if data:
                # Only write data if there is any to avoid Python 3.5 SSL bug
                self.wfile.write(data)
            self.wfile.flush()

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        reraise(*exc_info)
                finally:
                    exc_info = None
            elif headers_set:
                raise AssertionError("Headers already set")
            headers_set[:] = [status, response_headers]
            return write

        def execute(app):
            application_iter = app(environ, start_response)
            try:
                for data in application_iter:
                    write(data)
                if not headers_sent:
                    write(b"")
            finally:
                if hasattr(application_iter, "close"):
                    application_iter.close()

        try:
            execute(self.server.app)
        except (ConnectionError, socket.timeout) as e:
            self.connection_dropped(e, environ)
        except Exception:
            if self.server.passthrough_errors:
                raise
            from werkzeug.debug.tbtools import get_current_traceback

            traceback = get_current_traceback(ignore_system_exceptions=True)
            try:
                # if we haven't yet sent the headers but they are set
                # we roll back to be able to set them again.
                if not headers_sent:
                    del headers_set[:]
                execute(InternalServerError())
            except Exception:
                pass
            self.server.log("error", "Error on request:\n%s", traceback.plaintext)


if __name__ == '__main__':
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ.setdefault('APP_CONFIG', r'../settings-dev.json')
    create_app().run(request_handler=TestRequestHandler)
