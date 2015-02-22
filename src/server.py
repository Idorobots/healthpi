import json
import http.server
import ssl
import system
import utils

class Health(http.server.BaseHTTPRequestHandler):
    def response(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        wrapped_body = {"status" : "ok",
                        "result" : body}

        if code // 100 != 2:
            wrapped_body["status"] = "error"

        self.wfile.write(bytes(json.dumps(wrapped_body), "utf-8"))

    def do_GET(self):
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
            return self.response(404, path + " not found")
