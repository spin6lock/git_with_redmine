#!/usr/bin/env python
#encoding:utf8
from __future__ import print_function
import argparse

import requests
from requests.auth import HTTPBasicAuth

import config

def get_issue_url(issue_no):
    return config.issue_base_url.format(issue_no=issue_no)

def get_issue(url):
    print("checking url:", url)
    r = requests.get(url, auth=HTTPBasicAuth(config.key, ""), timeout=10)
    return r.json()["issue"]

def get_status_msg(issue_info):
    issue_id = issue_info["tracker"]["id"]
    new_state = config.state[issue_id]
    data = {
        "issue": {
            "status_id": new_state,
        }
    }
    return data

def close_redmine_issue(issue_no):
    url = get_issue_url(issue_no)
    issue_info = get_issue(url)
    data = get_status_msg(issue_info)
    resp = requests.put(url, json=data, auth=HTTPBasicAuth(config.key, ""),
                        timeout=10)
    return issue_info["tracker"]["name"], resp.status_code

def main():
    parser = argparse.ArgumentParser(description="close issue by cmdline")
    parser.add_argument(default = [], dest="issue_numbers", help="the issue you wanted to close", nargs="+")
    args = parser.parse_args()
    for issue_no in args.issue_numbers:
        issue_type, resp = close_redmine_issue(issue_no)
        print(issue_no, issue_type, resp)

if __name__ == "__main__":
    main()
