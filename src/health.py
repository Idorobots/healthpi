#! /bin/env python

import base64
import daemon
import getopt
import http.server
import server
import ssl
import sys
import system

def run_server(options, args):
    port = int(options["--port"])

    print("Health server started on port", port)
    health = http.server.HTTPServer(("", port), server.Health)

    health.refresh = "--refresh" in options and options["--refresh"] or None

    if "--auth" in options:
        health.auth = base64.b64encode(bytes(options["--auth"], "utf-8")).decode("ascii")

    if "--ssl-cert" in options:
        health.socket = ssl.wrap_socket(health.socket, certfile=options["--ssl-cert"], server_side=True)

    system.cpu_usage() # NOTE Required to properly compute usage on the first /cpu/ request.
    health.serve_forever()

class HealthDaemon(daemon.Daemon):
    def __init__(self, pidfile, options):
        super(HealthDaemon, self).__init__(pidfile)
        self.options = options

    def run(self):
        run_server(self.options, [])

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "", ["daemon=", "ssl-cert=", "port=", "auth=", "refresh="])
    options = dict(optlist)

    if "--daemon" in options:
        daemon = HealthDaemon("/tmp/health-daemon.pid", options)
        action = options["--daemon"]

        if action == "start":
            daemon.start()

        elif action == "stop":
            daemon.stop()

        elif action == "restart":
            daemon.restart()

        else:
            print("Unknown action", action)

    else:
        run_server(options, args)
