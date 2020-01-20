#!/usr/bin/env python3
#encoding:utf8
"""
对conflict的文件逐一调用editor修复
修复完检查一下<<<
然后自动git add
"""

import subprocess
import os
import re
import sys

def get_char():
    ch = sys.stdin.read(1)
    return ch

def check_if_miss(filename):
    result = None
    with open(filename, "r") as fh:
        content = fh.read()
        if content.find("<<< HEAD") != -1:
            print("still <<< HEAD in it, rework") 
            result = True
        elif content.find(">>>>>>>") != -1:
            print("still >>> in it, rework") 
            result = True
        else:
            result = False
    if result:
        get_char()
    return result
    
def main():
    #get conflict files
    conflict_files = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=U"]).split()
    #remove deleted by us, because no need to edit
    git_st_lines = subprocess.check_output(["git", "status"]).decode("utf-8").splitlines()
    deleted_by_us_files = [x for x in git_st_lines if x.find("deleted by us") > 0]
    if deleted_by_us_files:
        CONST_TIPS = "\tdeleted by us:   "
        delete_filenames = {f.replace(CONST_TIPS,'').encode('utf-8'):True for f in deleted_by_us_files}
    #get precise conflict files
    conflict_files = [f for f in conflict_files if f not in delete_filenames]
    #call up editor
    EDITOR = os.environ.get("EDITOR", "vim")
    for filename in conflict_files:
        print("ready to edit:%s" %filename)
        subprocess.call([EDITOR, filename])
        if_miss = check_if_miss(filename)
        while if_miss:
            subprocess.call([EDITOR, filename])
            if_miss = check_if_miss(filename)
        subprocess.call(["git", "add", filename])
    #optional: show merge diff

if __name__ == "__main__":
    main()
