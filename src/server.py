import json
import http.server
import ssl
import system
import utils

class Health(http.server.BaseHTTPRequestHandler):
    server_version = "Health Server v0.1.0"

    def response(self, code, body):
        self.send_response(code)
        self.send_header("WWW-Authenticate", "Basic realm=\"Health\"")
        self.send_header("Content-Type", "application/json")
        if self.server.refresh and code // 100 == 2:
            self.send_header("Refresh", self.server.refresh)
        self.end_headers()

        wrapped_body = {"status" : "ok",
                        "result" : body}

        if code // 100 != 2:
            wrapped_body["status"] = "error"

        self.wfile.write(bytes(json.dumps(wrapped_body), "utf-8"))

    def authorized(self):
        return not self.server.auth or self.headers["Authorization"] == "Basic " + self.server.auth

    def do_GET(self):
        if not self.authorized():
            return self.response(401, "Unauthorized!")

        endpoints = {"/cpu/": system.cpu_usage,
                     "/load/": system.load,
                     "/memory/": system.memory,
                     "/network/" : system.network_stats,
                     "/temp/": system.temp,
                     "/uptime/": system.uptime,
                     "/": lambda: {"endpoints": list(sorted(endpoints))}}

        path = utils.fix_path(self.path)

        if path in endpoints:
            return self.response(200, endpoints[path]())

        else:
            return self.response(404, "Not found!")
