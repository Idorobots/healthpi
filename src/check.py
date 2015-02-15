#! /bin/env python

import json
import requests
import sys


def check_health(url):
    result = requests.get(url).json()

    if result["status"] == "error":
        print(url, "check failed!")
        return

    print("#######", url, "#######")

    for endpoint in result["result"]["endpoints"]:
        if endpoint != "/":
            check_endpoint(url, endpoint)

def check_endpoint(url, endpoint):
    result = requests.get(url + endpoint).json()

    if result["status"] == "error":
        print(endpoint, "check failed!")

    else:
        print(endpoint, ":")

        for stat in result["result"]:
            print("\t", stat, ":", result["result"][stat])

if __name__ == "__main__":
    for url in sys.argv[1:]:
        check_health("http://" + url)
