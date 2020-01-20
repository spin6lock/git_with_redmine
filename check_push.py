#!/usr/bin/env python3
#encoding:utf8
"""
This module check your pre-push commit message's issue_no.
It fail the commit without issue_no
"""

import sys
import re
import subprocess
import difflib
import itertools

import requests
from requests.auth import HTTPBasicAuth

import config

NEED_KEYS = ["project", "subject", "id"]
def cleanup_issue(issue):
    tmp = {
        "project":1,
        "subject":1,
        "id":1,
    }
    for k in NEED_KEYS:
        tmp[k] = issue[k]
    return tmp

#全局唯一连接
def get_session():
    cache = {}
    def _get_session():
        if not cache.get("session", None):
            cache["session"] = requests.Session()
        return cache["session"]
    return _get_session()

def find_one_batch_my_issues(offset):
    url = config.all_my_issue_url
    payload = {
        "limit":config.search_limit,
        "assigned_to_id":"me",
        "status_id":"*",
        "offset":offset,
    }
    session = get_session()
    r = session.get(url, auth=HTTPBasicAuth(config.key, ""),
                    timeout=10, params=payload)
    data = r.json()
    data["issues"] = [cleanup_issue(issue) for issue in data["issues"]]
    return data

def find_all_my_issues():
    issues = []
    offset = 0
    data = find_one_batch_my_issues(offset)
    issues.extend(data["issues"])
    page_count = data["total_count"] // config.search_limit
    for i in range(1, page_count + 1):
        offset = i * config.search_limit
        data = find_one_batch_my_issues(offset)
        issues.extend(data["issues"])
    return issues

def reconstruct_issues(issues):
    issue_no2title = {}
    title2issue_no = {}
    issue_no2issue = {}
    for d in issues:
        issue_no2title[d["id"]] = d["subject"]
        title2issue_no[d["subject"]] = d["id"]
        issue_no2issue[d["id"]] = d
    return {
        "issue_no2title" : issue_no2title,
        "title2issue_no" : title2issue_no,
        "issue_no2issue" : issue_no2issue,
    }

def find_most_likely_issue(title2issue_no, title):
    result = difflib.get_close_matches(
        title, [t for t in title2issue_no.keys() if t != title])
    issue_numbers = [title2issue_no[t] for t in result]
    return issue_numbers

def find_all_same_issue(issue_no, issues, project_name):
    issue_no2title = issues["issue_no2title"]
    issue_no2issue = issues["issue_no2issue"]
    title = issue_no2title.get(issue_no, None)
    if not title:
        return
    exact_title_issue_no = [
        i for i, t in issue_no2title.items() if t == title and i != issue_no]
    match_title_issue_no = find_most_likely_issue(issues["title2issue_no"], title)
    candidate = itertools.chain(exact_title_issue_no, match_title_issue_no)
    for i in candidate:
        issue_info = issue_no2issue[i]
        if issue_info["project"]["name"] == project_name:
            return issue_info
    return None

def get_meesage():
    #get last commit
    return subprocess.check_output(["git", "log", "-1", "--pretty=%B"])

def get_issue(issue_no):
    url = config.issue_base_url.format(issue_no=issue_no)
    print("checking url:", url)
    session = get_session()
    r = session.get(url, auth=HTTPBasicAuth(config.key, ""), timeout=10)
    return r.json()["issue"]

def get_all_issues():
    cache = {}
    def _get_all_issues():
        if not cache.get("issues", None):
            i = find_all_my_issues()
            cache["issues"] = reconstruct_issues(i)
        return cache["issues"]
    return _get_all_issues()

def is_correct_issue(curr_branch, issue_no):
    if issue_no == 0: #去掉#0
        return
    issue_info = get_issue(issue_no)
    project_name = issue_info["project"]["name"]
    branchs = config.project_name_maps.get(project_name, [])
    branch_names = config.branch_names
    is_match = any(map(curr_branch.startswith, branchs))
    not_temp_branch = any(map(curr_branch.startswith, iter(branch_names.keys())))
    wrong_branch = False
    if not is_match and not_temp_branch:
        wrong_branch = True
    if wrong_branch:
        print("wrong branch, the issue you mention:\n", issue_no, issue_info["subject"])
        print("ready to find something similar")
        branch_name = list(filter(curr_branch.startswith, iter(branch_names.keys())))[0]
        branch_project_name = branch_names[branch_name]
        issues = get_all_issues()
        possible_issue = find_all_same_issue(issue_no, issues, branch_project_name)
        if possible_issue:
            print("maybe you means:\n", possible_issue["id"], possible_issue["subject"])
        else:
            print("can't find similar issue")
        sys.exit(1)

PATTERN = re.compile(r"#(?P<issue_no>\d+)")
def main():
    try:
        upstream = subprocess.check_output(["git", "rev-parse", "@{u}"]).strip() #sha1
    except subprocess.CalledProcessError as e:
        print("got:", e.output, "code:", e.returncode)
        return
    all_commits = subprocess.check_output(["git", "log", upstream+b"..HEAD", "--pretty=%h"]).split()
    curr_branch = subprocess.check_output(["git", "symbolic-ref", "--short", "HEAD"]).strip().decode("utf-8")
    for short_hash in all_commits:
        commit_message = subprocess.check_output(["git", "log", "-1", short_hash,
                                                  "--pretty=%B"])
        result = PATTERN.findall(commit_message.decode("utf-8"))
        if result:
            issue_numbers = [int(issue_no) for issue_no in result]
        else:
            print(short_hash, "you should write down the issue_no")
            sys.exit(1)
        for issue_no in issue_numbers:
            is_correct_issue(curr_branch, issue_no)

if __name__ == "__main__":
    main()
