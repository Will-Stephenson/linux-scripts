#!/usr/bin/python3 -u

### Manages the patching of Ubuntu operating system
### Disables any non-standard repos (so application patching can be handled separately), emails results and reboots if successful
### Haven't tested with other apt-based distro's but should work with little modification

import os
import sys
import subprocess
import socket
import io
import time
import smtplib
from email.message import EmailMessage
from datetime import date

out_file = "/var/log/auto_patching/auto_patching." + date.today().strftime("%Y%m")
extra_repos_dir = "/etc/apt/sources.list.d/" # Directory containing non-standard repos that should be disabled 

hostname = socket.gethostname() # more reliable/portable than checking for ENV variables 
short_hostname = hostname.split(".")[0]

email_recipients = ["william.stephenson@stategrowth.tas.gov.au"]
email_address = short_hostname + "@stategrowth.tas.gov.au"

# Write all output to file instead of stdout
output_directory = "/var/log/auto_patching"
if os.path.isdir(output_directory):
  print("Output directory found")
else:
  try:
    os.mkdir(output_directory)
  except OSError:
    print("Creation of directory %s failed" % output_directory)
    sys.exit(2)
  else:
    print("Successfully created the directory %s" % ouput_directory)

#sys.stdout = open(out_file, 'w')

## Functions
def disable_repos(directory):
  print("\n\n### Disabling extra repositories ###\n", flush=True)
  for file in os.listdir(directory):
    if file.endswith(".list"):
      file_fq = directory + file
      os.rename(file_fq, file_fq + ".temp_disabled")
      print(file_fq + " disabled\n", flush=True)

def enable_repos(directory):
  print("\n\n### Re-enabling disabled repos ###\n", flush=True)
  for repo_file in os.listdir(extra_repos_dir):
    if repo_file.endswith(".temp_disabled"):
        repo_file_fq = extra_repos_dir + repo_file.rsplit(".", 1)[0]
        os.rename(repo_file_fq + ".temp_disabled", repo_file_fq)
        print(repo_file_fq + " re-enabled", flush=True)

def email(message):
  try:
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "Linux Automated Patching"
    msg['From'] = email_address
    msg['To'] = email_recipients
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.send_message(msg)
    print("\nEmail report sent to " + str(email_recipients) + " successfully")
  except smtplib.SMTPException:
    print("\nError: Unable to send email")

# Set Icinga downtime for the host (replace this line with an API call to any relevant monitoring software)
#print("\n\n### Putting host into downtime in Icinga ###\n\n", flush=True)
#subprocess.run(["/opt/admin/bin/schedule_downtime.sh", "--filter", "host.name", "--search", hostname, "--all-services", "--author", "Automated Patching Agent", "--comment", "Patching", "--start-time", str(time.time()), "--end-time", str(int(time.time())+3600)], bufsize=0, stdout=sys.stdout)

# Disable any non-default repos
disable_repos(extra_repos_dir)

# Update repos
apt_update = subprocess.run(["apt-get", "update"], bufsize=0, stdout=sys.stdout)
if apt_update.returncode != 0:
  print("\n\n!!! apt-update failed - exiting !!!\n\n")
  email("Patching failed at apt-update stage - See " + out_file + " on " + short_hostname + " for more details")
  enable_repos(extra_repos_dir)
  sys.exit(2)

print("\n\n### apt-update complete ###\n\n", flush=True)

# Patch host
apt_upgrade = subprocess.run(["apt-get", "upgrade", "--assume-yes"], bufsize=0, stdout=sys.stdout)
if apt_upgrade.returncode != 0:
  print("\n\n!!! apt-upgrade failed - exiting !!!\n\n")
  email("Patching failed at apt-upgrade stage - See " + out_file + " on " + short_hostname + " for more details")
  enable_repos(extra_repos_dir)
  sys.exit(2)

print("\n\n### apt-upgrade complete ###\n\n", flush=True)

# Clean up
apt_autoremove = subprocess.run(["apt-get", "auto-remove", "--assume-yes"], bufsize=0, stdout=sys.stdout)
if apt_autoremove.returncode != 0:
  print("\n\n!!! apt-autoremove failed - exiting !!!\n\n")
  email("Patching failed at apt-autoremove stage - See " + out_file + " on " + short_hostname + " for more details")
  enable_repos(extra_repos_dir)
  sys.exit(2)

print("\n\n### apt-autoremove complete ###\n\n", flush=True)

# Re-enable any disabled repos
enable_repos(extra_repos_dir)

# Email results
email("Patching successful - See " + out_file + " on " + short_hostname + " for more details")

# Reboot
print("\n\n### Rebooting ###\n\n", flush=True)
subprocess.run(["/usr/sbin/reboot", "reboot"])
