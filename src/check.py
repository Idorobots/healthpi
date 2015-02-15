#! /bin/env python

import getopt
import json
import re
import requests
import sys


def check_health(url, optlist):
    try:
        result = requests.get(url).json()

        if result["status"] == "error":
            print(url, "check failed!")
            return

        print("#######", url, "#######")

        endpoints = result["result"]["endpoints"]
        allowed = "--endpoints" in optlist and re.split(",", optlist["--endpoints"]) or endpoints

        for endpoint in endpoints:
            if endpoint != "/" and endpoint in allowed:
                check_endpoint(url, endpoint)

    except:
        print(url, "unreachable!")

def check_endpoint(url, endpoint):
    try:
        result = requests.get(url + endpoint).json()

        if result["status"] == "error":
            print(endpoint, "check failed!")

        else:
            print(endpoint, ":")

            for stat in result["result"]:
                print("\t", stat, ":", result["result"][stat])

    except:
        print(endpoint, "unreachable!")

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "", ["endpoints="])
    optlist = dict(optlist)

    for url in args:
        check_health("http://" + url, optlist)
