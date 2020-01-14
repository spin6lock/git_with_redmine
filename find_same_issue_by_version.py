#encoding:utf8
from __future__ import print_function
import argparse
import difflib

import requests
from requests.auth import HTTPBasicAuth

import all_issue

def find_most_likely_issue(title2issue_no, title):
    result = difflib.get_close_matches(title, title2issue_no.iterkeys())
    result.remove(title)
    return result

def find_all_same_issue(issue_no):
    issues = all_issue.find_all_my_issues()
    issue_no2title, title2issue_no = all_issue.find_issue_title(issues)
    title = issue_no2title[issue_no]
    match_titles = find_most_likely_issue(title2issue_no, title)
    print("origin title:", title)
    for title in match_titles:
        print(title, title2issue_no[title])

def main():
    parser = argparse.ArgumentParser(description="find same issue by different version")
    parser.add_argument(action="store", dest="issue_number", help="the origin issue")
    parser.add_argument(action="store", dest="version", help="the version you want, eg: jp")
    args = parser.parse_args()
    find_all_same_issue(int(args.issue_number))

if __name__ == "__main__":
    main()
