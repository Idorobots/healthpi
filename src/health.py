#! /bin/env python

import daemon
import getopt
import http.server
import json
import os
import re
import sys

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

    def fixed_path(self):
        if self.path.endswith("/"):
            return self.path

        else:
            return self.path + "/"

    def do_GET(self):
        endpoints = {"/temp/": self.get_temp,
                     "/load/": self.get_load,
                     "/memory/": self.get_memory,
                     "/uptime/": self.get_uptime,
                     "/": lambda: {"endpoints": list(endpoints)}}

        path = self.fixed_path()

        if path in endpoints:
            return self.response(200, endpoints[path]())

        else:
            return self.response(404, path + " not found")

    def get_uptime(self):
        time = open("/proc/uptime").readline()
        times = re.split(" ", time)
        return {"uptime": float(times[0]),
                "idle": float(times[1])}

    def get_temp(self):
        temps = {}

        for dirname, dirnames, _ in os.walk("/sys/class/thermal/"):
            for zone in dirnames:
                if zone.startswith("thermal_zone"):
                    temp = open(os.path.join(dirname, zone, "temp"), "r").readline()
                    temps[zone] = int(temp)/1000

        return temps

    def get_load(self):
        load = open("/proc/loadavg", "r").readline()
        loads = re.split(" ", load)
        return {"1min": float(loads[0]),
                "5min": float(loads[1]),
                "15min": float(loads[2])}

    def get_memory(self):
        memory = {}

        for line in open("/proc/meminfo", "r"):
            info = re.split("\s+", line)
            stat = info[0]
            stat = stat[0:len(stat)-1]
            memory[stat] = 1024 * int(info[1])

        return memory

def run_server(options, args):
    port = int(args[0])

    print("Health server started on port ", port)
    http.server.HTTPServer(("", port), Health).serve_forever()

class HealthDaemon(daemon.daemon):
    def run(self):
        run_server({}, [8000])

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "", "daemon=")
    optlist = dict(optlist)

    if "--daemon" in optlist:
        daemon = HealthDaemon("/tmp/health-daemon.pid")
        action = optlist["--daemon"]

        if action == "start":
            daemon.start()

        elif action == "stop":
            daemon.stop()

        elif action == "restart":
            daemon.restart()

        else:
            print("Unknown action", action)

    else:
        run_server(optlist, args)
