#!/usr/bin/env python
#encoding:utf8
"""
对conflict的文件逐一调用editor修复
修复完检查一下<<<
然后自动git add
"""
from __future__ import print_function
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
    #call up editor
    EDITOR = os.environ.get("EDITOR", "vim")
    for filename in conflict_files:
        print(filename)
        subprocess.call([EDITOR, filename])
        if_miss = check_if_miss(filename)
        while if_miss:
            subprocess.call([EDITOR, filename])
            if_miss = check_if_miss(filename)
        subprocess.call(["git", "add", filename])
    #optional: show merge diff

if __name__ == "__main__":
    main()
