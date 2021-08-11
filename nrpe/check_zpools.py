#!/usr/bin/python3

### Check the status of zpools and return nrpe friendly output and performance data

import os
import sys
import subprocess

#"$mountpoint=$perc;$WARN%;$CRIT%;;100%"
warning_threshold=80
critical_threshold=90

# Get zpool output and divide it by line
zpool_output = str(subprocess.run(['zpool', 'list'], stdout=subprocess.PIPE))
raw_zpools = zpool_output.split("\\")

# Trim first and last elements to remove header line and trailing newline
del raw_zpools[0]
del raw_zpools[-1]

zpools = []
for i, zpool in enumerate(raw_zpools):
    zpoolDetails = zpool.split()
    zpool = {
        "name": zpoolDetails[0][1:], # Split doesn't remove the 'n' from '\n' delimiter so this cuts the first char
        "size": zpoolDetails[1],
        "used": zpoolDetails[2],
        "free": zpoolDetails[3],
        "usedPerc": zpoolDetails[7][:-1],
	"status": ""
    }
    zpools.append(zpool)

# Determine the status and add zpool to correct list
status=3 # will be 'unknown' unless at least one zpool is found
okay_zpools = []
warning_zpools = []
critical_zpools = []

for zpool in zpools:
    used=int(zpool['usedPerc'])
    if used >= warning_threshold and used < critical_threshold:
        if status <= 1: status=1
        zpool['status'] = "Warning"
        warning_zpools.append(zpool)
    elif used >= critical_threshold:
        status=2
        zpool['status'] = "Critical"
        critical_zpools.append(zpool)
    else:
        status=0
        zpool['status'] = "OK"
        okay_zpools.append(zpool)

if status == 0: statusText="OK"
if status == 1: statusText="Warning"
if status == 2: statusText="Critical"
if status == 3: statusText="Unknown"


# Print status and any pools with issues first
print("zpools " + statusText + "\n")
for zpool in critical_zpools:
    print(zpool['name'] + " is " + zpool['usedPerc'] + "% full (Used " + zpool['used'] + " / " + zpool['free'] + ") <br>")

for zpool in warning_zpools:
    print(zpool['name'] + " is " + zpool['usedPerc'] + "% full (Used " + zpool['used'] + " / " + zpool['free'] + ") <br>")

# Print full HTML table and perfdata
print("<br><table>")
print("<tr><th>Status</th><th>zpool</th><th>Used</th><th>Capacity</td><th>Used(%)</th><th>Thresholds</th></tr>")
for zpool in critical_zpools:
    print("<tr><td>(" + zpool['status'].upper() + ")</td><td>" + zpool['name'] + "</td><td>" + zpool['used'] + "</td><td>" + zpool['size'] + "</td><td>" + zpool['usedPerc'] + "%</td><td> Warn=" + str(warning_threshold) + "% Crit=" + str(critical_threshold) + "%</td></tr>" + " | " + zpool['name'] + "=" + zpool['usedPerc'] + "%;" + str(warning_threshold) + "%;" + str(critical_threshold) + "%;;100%")
for zpool in warning_zpools:
    print("<tr><td>(" + zpool['status'].upper() + ")</td><td>" + zpool['name'] + "</td><td>" + zpool['used'] + "</td><td>" + zpool['size'] + "</td><td>" + zpool['usedPerc'] + "%</td><td> Warn=" + str(warning_threshold) + "% Crit=" + str(critical_threshold) + "%</td></tr>" + " | " + zpool['name'] + "=" + zpool['usedPerc'] + "%;" + str(warning_threshold) + "%;" + str(critical_threshold) + "%;;100%")
for zpool in okay_zpools:
    print("<tr><td>(" + zpool['status'].upper() + ")</td><td>" + zpool['name'] + "</td><td>" + zpool['used'] + "</td><td>" + zpool['size'] + "</td><td>" + zpool['usedPerc'] + "%</td><td> Warn=" + str(warning_threshold) + "% Crit=" + str(critical_threshold) + "%</td></tr>" + " | " + zpool['name'] + "=" + zpool['usedPerc'] + "%;" + str(warning_threshold) + "%;" + str(critical_threshold) + "%;;100%")
print("</table>\n")

sys.exit(status)
