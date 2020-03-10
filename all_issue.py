#!/usr/bin/env python3
#encoding:utf8
import argparse
import pprint

import requests
from requests.auth import HTTPBasicAuth

from fix_issue import get_issue_url, get_issue
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
    issue_no2issue = {}
    for d in issues:
        issue_no2title[d["id"]] = d["subject"]
        title2issue_no[d["subject"]] = d["id"]
        issue_no2issue[d["id"]] = d
    return issue_no2title, title2issue_no, issue_no2issue

def get_args():
    parser = argparse.ArgumentParser(description="close issue by cmdline")
    parser.add_argument("-i", default = [], dest="issue_numbers", help="the issue you wanted to close", nargs="+")
    args = parser.parse_args()
    return args

def get_issues(issue_numbers):
    for issue_no in issue_numbers:
        print(issue_no, issue_numbers)
        issue_no = int(issue_no)
        url = get_issue_url(issue_no)
        issue_info = get_issue(url)
        pprint.pprint(issue_info)

def get_all():
    issues = find_all_my_issues()
    result, _, issue_no2issue = find_issue_title(issues)
    for issue_no, title in result.items():
        issue = issue_no2issue[issue_no]
        status = issue["status"]["name"]
        project_name = issue["project"]["name"]
        print(issue_no, status, title, project_name)

def main():
    args = get_args()
    if args.issue_numbers:
        get_issues(args.issue_numbers)
    else:
        get_all()

if __name__ == "__main__":
    main()
