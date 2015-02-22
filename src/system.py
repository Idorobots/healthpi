import os
import re
import utils

def uptime():
    time = open("/proc/uptime").readline()
    times = re.split(" ", time)
    return {"uptime": float(times[0]),
            "idle": float(times[1])}

def temp():
    temps = {}
    prefix = "/sys/class/thermal/"

    for zone in os.listdir(prefix):
        if zone.startswith("thermal_zone"):
            temp = open(os.path.join(prefix, zone, "temp")).readline()
            temps[zone] = int(temp)/1000

    return temps

def load():
    load = open("/proc/loadavg", "r").readline()
    loads = re.split(" ", load)
    return {"1min": float(loads[0]),
            "5min": float(loads[1]),
            "15min": float(loads[2])}

@utils.with_state(cpu = {})
def cpu_usage(self):
    cpu = {}

    for line in open("/proc/stat"):
        if line.startswith("cpu"):
            stats = re.split("\s+", line)
            name = stats[0]
            stats = {"user": int(stats[1]),
                     "nice": int(stats[2]),
                     "system": int(stats[3]),
                     "idle": int(stats[4]),
                     "iowait": int(stats[5]),
                     "irq": int(stats[6]),
                     "softirq": int(stats[7])}

            if name in self.cpu:
                prev = self.cpu[name]
                user = stats["user"] + stats["nice"]
                prev_user = prev["user"] + prev["nice"]
                total = (user + stats["system"] + stats["idle"])
                prev_total = (prev_user + prev["system"] + prev["idle"])
                denominator = (total - prev_total) / 100
                stats["usage"] = {"user": round((user - prev_user) / denominator),
                                  "system": round((stats["system"] - prev["system"]) / denominator),
                                  "io": round((stats["iowait"] - prev["iowait"]) / denominator)}

            else:
                stats["usage"] = None

            cpu[name] = stats

        else:
            break

    self.cpu = cpu
    return cpu

def memory():
    memory = {}

    for line in open("/proc/meminfo"):
        info = re.split("\s+", line)
        stat = info[0]
        stat = stat[0:len(stat)-1]
        memory[stat] = 1024 * int(info[1])

    return memory

def network_stats():
    net = {}
    prefix = "/sys/class/net/"

    for interface in os.listdir(prefix):
        stats = {}
        path = os.path.join(prefix, interface, "statistics")

        for name in os.listdir(path):
            stats[name] = int(open(os.path.join(path, name)).readline())

        net[interface] = stats

    return net

