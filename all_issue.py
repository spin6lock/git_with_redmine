#!/usr/bin/env python
#encoding:utf8
from __future__ import print_function

import requests
from requests.auth import HTTPBasicAuth

import config

def find_all_my_issues():
    url = config.all_my_issue_url
    payload = {
            "limit":config.search_limit,
            "assigned_to_id":"me",
        }
    r = requests.get(url, auth=HTTPBasicAuth(config.key, ""), timeout=10, params=payload)
    data = r.json()["issues"]
    return data

def find_issue_title(issues):
    issue_no2title = {}
    title2issue_no = {}
    for d in issues:
        issue_no2title[d["id"]] = d["subject"]
        title2issue_no[d["subject"]] = d["id"]
    return issue_no2title, title2issue_no

def main():
    issues = find_all_my_issues()
    result, _ = find_issue_title(issues)
    for issue_no, title in result.iteritems():
        print(issue_no, title.encode("utf8"))

if __name__ == "__main__":
    main()
