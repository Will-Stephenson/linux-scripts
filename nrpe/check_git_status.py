#!/usr/bin/python3

### Script checks whether or not a git repo has any unstaged/uncommited changes
### TODO: Check for changes at origin which need to be pulled still (will require git fetch with an SSH key)
### Retun codes:
###   0: No changes to be committed or pushed
###   1: Changes have been committed but not pushed
###   2: Changes to be committed 
### Will S - July 2021

import sys
import os
import argparse
import subprocess

output = "OK: All changes synchronised with remote repository"
exit_code = 0

# Debug print function (so I'm not checking args.debug before every print statement)
def dprint(debug_output):
    if args.debug: print(debug_output)

# Read and validate args
parser = argparse.ArgumentParser()
parser.add_argument("repo", help="The path to the repository being checked", type=str)
parser.add_argument("--debug", help="Print debug info", action="store_true")
args = parser.parse_args()
repo_location = args.repo
if args.debug: print("Checking for git repo at " + repo_location)

# Check there is actually repo at the location
if os.path.isdir(repo_location):
    dprint("Git repo found at " + repo_location + "\n")
    os.chdir(repo_location)
else:
    print("Error: No git repo found at " + repo_location)
    sys.exit(2)

# Check for unstaged/uncommit changes
uncommitted_changes = subprocess.Popen(["git", "status", "--porcelain"], stdout=subprocess.PIPE)
count_uncommitted_changes = subprocess.check_output(["wc", "-l"], stdin=uncommitted_changes.stdout, text=True)
uncommitted_changes.wait()

# Report change status and exit if any found
if int(count_uncommitted_changes) > 0:
    dprint("Uncommitted changes found: " + count_uncommitted_changes)
    output = "Warning: " + count_uncommitted_changes.rstrip() + " uncommitted change(s) found"
    exit_code = 1
else:
    dprint("All changes checked in")

# If there are none, check for unpushed changes
unpushed_changes = subprocess.Popen(["git", "status", "-uno"], stdout=subprocess.PIPE)
check_unpushed_changes = subprocess.run(["grep", "ahead"], stdin=unpushed_changes.stdout, stdout=subprocess.DEVNULL)
unpushed_changes.wait()

# Report if local branch is ahead of the origin
if check_unpushed_changes.returncode == 0:
    dprint("Warning: Unpushed changes found")
    output = "Warning: Unpushed changes found"
    exit_code = 1
else:
    dprint("All changes pushed")

print(output)
sys.exit(exit_code)
