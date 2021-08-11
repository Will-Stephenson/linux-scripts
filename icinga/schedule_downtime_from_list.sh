#!/usr/bin/bash

# Check an input file has been passed 
[ -z "$1" ] && echo -e "Incorrect Usage: A file containing a list of VMs must be passed \ne.g.: ./dowtime_from_list.sh /tmp/hosts_for_downtime" && exit 1

input_file=$1

# Check the file is readable
[ ! -r "$input_file" ] && echo "Error: File $input_file cannot be read" && exit 2

# Confirm that the user has checked the default values
echo -e "IMPORTANT: This script contains default values for the API call which should be edited before running.\nOne day I might make this as nice as the regular script but in the meantime this will have to do.\n"
echo "Have you modified the values?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "Okay: running scipt"; break;;
        No ) echo "Script call cancelled"; exit 1;;
    esac
done

while read line; do
    /opt/admin/bin/icinga/schedule_downtime.sh --search $line.* --filter host.name --author CTS-IS --comment "Downtime scheduled en mass via schedule_downtime_from_list.sh" --all-services --start-time $(date +%s -d " +0 hour") --end-time $(date +%s -d " +1 hour")
done < $input_file

exit 0

