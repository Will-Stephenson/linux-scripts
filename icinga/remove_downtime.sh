#!/bin/bash

### This script schedules downtime through the Icinga API
### The funcitonality is limited to get it done quicker, but later it would be good to add the option to authenticate with passwords instead of keys and add a few more options for arguments
### Will S - 12/2020

## Set default vars
PATH=$PATH:/opt/jo/bin:/opt/admin/bin # Update PATH to include jo
username= # Icinga API user
password= # Icinga API user's password
host= # Icinga API endpoint
port=5665

downtime_pretty=true

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
        -a|--author)
            downtime_author="$2"
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

## API filter syntax changes when searching for hostgroups as opposed to any other filter
if [[ $downtime_filter == "host.groups" ]];then
    curl --noproxy "*" -k -s -u $username:$password -H "Accept: application/json" -X POST "https://$host:$port/v1/actions/remove-downtime" \
        -d "$(jo -p \
            pretty="$downtime_pretty" \
            type=Host \
            filter="\"$downtime_search\" in $downtime_filter" \
            author="$downtime_author" \
        )"

    ## The remove-downtime api call has no '--all-services' flag so you have to perform the action once for Hosts and again for services
    curl --noproxy "*" -k -s -u $username:$password -H "Accept: application/json" -X POST "https://$host:$port/v1/actions/remove-downtime" \
        -d "$(jo -p \
            pretty="$downtime_pretty" \
            type=Service \
            filter="\"$downtime_search\" in $downtime_filter" \
            author="$downtime_author" \
        )"


else
    curl --noproxy "*" -k -s -u $username:$password -H "Accept: application/json" -X POST "https://$host:$port/v1/actions/remove-downtime" \
        -d "$(jo -p \
            pretty="$downtime_pretty" \
            type=Host \
            filter='match("'$downtime_search'", '$downtime_filter')' \
            author="$downtime_author" \
            comment="$downtime_comment" \
        )"

    ## The remove-downtime api call has no '--all-services' flag so you have to perform the action once for Hosts and again for services
    curl --noproxy "*" -k -s -u $username:$password -H "Accept: application/json" -X POST "https://$host:$port/v1/actions/remove-downtime" \
        -d "$(jo -p \
            pretty="$downtime_pretty" \
            type=Service \
            filter='match("'$downtime_search'", '$downtime_filter')' \
            author="$downtime_author" \
            comment="$downtime_comment" \
        )"


fi

exit $?
