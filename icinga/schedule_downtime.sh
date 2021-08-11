#!/bin/bash

### This script schedules downtime through the Icinga API
### Requires the jo utility to be installed to create JSON objects
### The funcitonality is limited to get it done quicker, but later it would be good to add the option to authenticate with passwords instead of keys and add a few more options for arguments
### Will S - 12/2020

## Set default vars
PATH=$PATH:/opt/jo/bin:/opt/admin/bin # Update PATH to include jo
username= # Icinga API user
password= # Icinga API user's password
host= # address of Icinga API endpoint 
port=5665 # default port but change if necessary

downtime_pretty=true
downtime_type=Host
downtime_all_services=false                                                                                                                                                                                                        
downtime_fixed=true

## Get user args
while [ "$#" -gt 0 ]; do
    case "$1" in
        -s|--search)
            downtime_search="$2"
            shift 2
            ;;
        -f|--filter)
            downtime_filter="$2"
            shift 2
            ;;
        --all-services)
            downtime_all_services="true"
            shift
            ;;
        -a|--author)
            downtime_author="$2"
            shift 2
            ;;
        -c|--comment)
            downtime_comment="$2"
            shift 2
            ;;
        --start-time)
            downtime_start_time="$2"
            shift 2
            ;;
        --end-time)
            downtime_end_time="$2"
            shift 2
            ;;
        \?)
            echo "Invalid option: $1"
            exit 2
            ;;
        *)
            echo "Invalid option: $1"
            exit 2
            ;;
    esac
done

## Validate command
[ -z "$downtime_filter" ] && echo -e "ERROR: Please specify a filter with the --filter argument - e.g. --filter host.name | host.groups | host.vars.global_zone" && exit 2
[ -z "$downtime_search" ] && echo -e "ERROR: Please specify a search string with the --search argument - e.g. --search tmrds.dept.unix" && exit 2
[ -z "$downtime_start_time" ] && echo -e "ERROR: Please specify a start time with the --start-time argument - e.g. --start-time \$(date +%s -d \" +0 hour\")" && exit 2
[ -z "$downtime_end_time" ] && echo -e "ERROR: Please specify an end time with the --end-time argument - e.g. --end-time \$(date +%s -d \" +0 hour\")" && exit 2
[ -z "$downtime_author" ] && echo -e "ERROR: Please specify an author with the --author argument - e.g. --author w-stephenson" && exit 2
[ -z "$downtime_comment" ] && echo -e "ERROR: Please specify a comment with the --comment argument - e.g. --comment \"Monthly Patching\"" && exit 2

## API filter syntax changes when searching for hostgroups as opposed to any other filter
if [[ $downtime_filter == "host.groups" ]];then
    curl --noproxy "*" -k -s -u $username:$password -H "Accept: application/json" -X POST "https://$host:$port/v1/actions/schedule-downtime" \
        -d "$(jo -p \
            pretty="$downtime_pretty" \
            type="$downtime_type" \
            filter="\"$downtime_search\" in $downtime_filter" \
            all_services=$downtime_all_services \
            author="$downtime_author" \
            comment="$downtime_comment" \
            fixed=$downtime_fixed \
            start_time=$downtime_start_time \
            end_time=$downtime_end_time \
        )"
else
    curl --noproxy "*" -k -s -u $username:$password -H "Accept: application/json" -X POST "https://$host:$port/v1/actions/schedule-downtime" \
        -d "$(jo -p \
            pretty="$downtime_pretty" \
            type="$downtime_type" \
            filter='match("'$downtime_search'", '$downtime_filter')' \
            all_services=$downtime_all_services \
            author="$downtime_author" \
            comment="$downtime_comment" \
            fixed=$downtime_fixed \
            start_time=$downtime_start_time \
            end_time=$downtime_end_time \
        )"
fi

exit $?
