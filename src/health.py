#! /bin/env python

import daemon
import getopt
import http.server
import json
import os
import re
import ssl
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
        endpoints = {"/cpu/": self.get_cpu_usage,
                     "/load/": self.get_load,
                     "/memory/": self.get_memory,
                     "/network/" : self.get_net_stats,
                     "/temp/": self.get_temp,
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
        prefix = "/sys/class/thermal/"

        for zone in os.listdir(prefix):
            if zone.startswith("thermal_zone"):
                temp = open(os.path.join(prefix, zone, "temp")).readline()
                temps[zone] = int(temp)/1000

        return temps

    def get_load(self):
        load = open("/proc/loadavg", "r").readline()
        loads = re.split(" ", load)
        return {"1min": float(loads[0]),
                "5min": float(loads[1]),
                "15min": float(loads[2])}

    def get_cpu_usage(self):
        cpu = {}

        for line in open("/proc/stat"):
            if line.startswith("cpu"):
                stats = re.split("\s+", line)
                cpu[stats[0]] = {"user": int(stats[1]),
                                 "nice": int(stats[2]),
                                 "system": int(stats[3]),
                                 "idle": int(stats[4]),
                                 "iowait": int(stats[5]),
                                 "irq": int(stats[6]),
                                 "softirq": int(stats[7])}

            else:
                break

        return cpu

    def get_memory(self):
        memory = {}

        for line in open("/proc/meminfo"):
            info = re.split("\s+", line)
            stat = info[0]
            stat = stat[0:len(stat)-1]
            memory[stat] = 1024 * int(info[1])

        return memory

    def get_net_stats(self):
        net = {}
        prefix = "/sys/class/net/"

        for interface in os.listdir(prefix):
            stats = {}
            path = os.path.join(prefix, interface, "statistics")

            for name in os.listdir(path):
                stats[name] = int(open(os.path.join(path, name)).readline())

            net[interface] = stats

        return net

def run_server(options, args):
    port = int(options["--port"])

    print("Health server started on port ", port)
    server = http.server.HTTPServer(("", port), Health)

    if "--ssl-cert" in options:
        server.socket = ssl.wrap_socket(server.socket, certfile=options["--ssl-cert"], server_side=True)

    server.serve_forever()

class HealthDaemon(daemon.Daemon):
    def __init__(self, pidfile, options):
        super(HealthDaemon, self).__init__(pidfile)
        self.options = options

    def run(self):
        run_server(self.options, [])

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "", ["daemon=", "ssl-cert=", "port="])
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
