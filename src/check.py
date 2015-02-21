#! /bin/env python

import getopt
import json
import re
import requests
import sys


def check_health(url, optlist):
    try:
        result = requests.get(url, verify = False).json()

        if result["status"] == "error":
            print(url, "check failed!")
            return

        print(url)

        endpoints = sorted(result["result"]["endpoints"])
        allowed = "--endpoints" in optlist and re.split(",", optlist["--endpoints"]) or endpoints

        for endpoint in endpoints:
            if endpoint != "/" and endpoint in allowed:
                check_endpoint(url, endpoint)

    except:
        print(url, "unreachable!")

def check_endpoint(url, endpoint):
    try:
        result = requests.get(url + endpoint, verify = False).json()

        if result["status"] == "error":
            print(url + endpoint, "check failed!")

        else:
            print_value(endpoint, result["result"])

    except:
        print(url + endpoint, "unreachable!")


def print_value(endpoint, value):
    if type(value) == type({}):
        for stat in sorted(value):
            print_value(endpoint + stat + "/", value[stat])

    else:
        print("\t", endpoint, "\t", value)

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "", ["endpoints="])
    options = dict(optlist)

    for url in sorted(args):
        check_health(url, options)
