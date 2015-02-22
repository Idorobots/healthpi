#! /bin/env python

import getopt
import json
import re
import requests
import sys

def request_args(options):
    kwargs = {"verify": False}

    if "--auth" in options:
        kwargs["auth"] = options["--auth"]

    return kwargs

def check_health(url, options):
    try:
        result = requests.get(url, **request_args(options)).json()

        if result["status"] == "error":
            print(url, "check failed!")
            return

        print(url)

        endpoints = sorted(result["result"]["endpoints"])
        allowed = "--endpoints" in options and options["--endpoints"] or endpoints

        for endpoint in endpoints:
            if endpoint != "/" and endpoint in allowed:
                check_endpoint(url, endpoint, options)

    except:
        print(url, "unreachable!")

def check_endpoint(url, endpoint, options):
    try:
        result = requests.get(url + endpoint, **request_args(options)).json()

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
    optlist, args = getopt.getopt(sys.argv[1:], "", ["endpoints=", "auth="])
    options = dict(optlist)

    if "--endpoints" in options:
        options["--endpoints"] = re.split(",", options["--endpoints"])

    if "--auth" in options:
        options["--auth"] = tuple(re.split(":", options["--auth"]))

    for url in sorted(args):
        check_health(url, options)
