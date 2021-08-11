#!/usr/bin/python3

### Updates local repositories using the Aptly agent
### Must be run on server with aptly set up as root
### The script expects a snapshot to already exist so it will not work if migrating to a new server with no aptly snapshots configured - this can be fixed by switching the 'publish switch' command for 'publish snapshot'
### Will - June 2021

"""
Basic Aptly upgrade process:
1. Update mirror (local copy of remote repo from http://archive.ubuntu.com/ubuntu)
2. Create a snapshot of the updated mirror (in aptly - not an actual OS snapshot)
3. Publish the new snapshot
"""

import sys
import subprocess
from datetime import date

# Aptly repos to update
repos = ["focal", "focal-updates", "focal-security", "focal-backports"]

# Update, snapshot and publish each repo
for repo in repos:

    """
    Perform mirror update
    Mirror updates error a lot so attempt it three times before giving up
    If it still does not work after the third attempt, you may need to filter certain packages out
        This can be done with the following syntax:
            aptly mirror edit -filter='!package-A,!package-B' dsg-focall
        Make sure to check the filter settings first as this will override any previous settings
            aptly mirror show dsg-focal | grep Filter:
    """

    mirror_update_successful = False
    attempts = 1
    while (not mirror_update_successful and attempts <= 3):
        print("Attempt " + str(attempts) + " at " + repo + " update")
        aptly_mirror = subprocess.run(["aptly", "mirror", "update", repo ])
        if (aptly_mirror.returncode == 0):
            mirror_update_successful = True
            print("\n\n### " + repo + " updated successfully on attempt " + str(attempts) + " ###\n\n")
        else:
            print("\n\nError: " + repo + " failed to update ")
            sys.exit(2)
        attempts += 1

# Snapshot and publishing in it's own loop so it will only begin when all the repos are successfully sync'd
for repo in repos:

    # Create new snasphot
    snapshot_name =  date.today().strftime("%b%Y") + "_" + repo
    aptly_create_snap = subprocess.run(["aptly", "snapshot", "create", snapshot_name , "from", "mirror", repo ])
    if (aptly_create_snap.returncode == 0):
        print("\n\n### Snapshot " + snapshot_name + " successfully created from " + repo + " ###\n\n")
    else:
        print("\n\nError: " + repo + " snapshot failed ")
        sys.exit(2)

    # Publish snapshots
    distribution_name = repo.split("-", 1)[1]
    aptly_publish_snap = subprocess.run(["aptly", "publish", "switch", distribution_name, snapshot_name])
    if (aptly_publish_snap.returncode == 0):
        print("\n\n### Snapshot " + snapshot_name + "successfully published ###\n\n")
    else:
        print("\n\nError: " + snapshot_name + " failed to publish")
        sys.exit(2)

print("\n\n### Repo sync successfully completed ###\n")
sys.exit(0)



