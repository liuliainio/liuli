#!/bin/bash - 
#===============================================================================
#
#          FILE: logger.sh
# 
#         USAGE: ./logger.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 12/06/2013 04:50:39 PM CST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error


function _log()
{
    local level=$1
    shift
    local args="$*"
    echo "[$level] `date +'%Y-%m-%d %H:%M:%S'`: $args" | tee -a $log_file
}

function log()
{
    case $log_level in
        "DEBUG")
            _log $*
            ;;
        "INFO")
            if [[ $1 != "DEBUG" ]]; then
                _log $*
            fi
            ;;
        "WARN")
            if [[ $1 != "DEBUG" ]] && [[ $1 != "INFO" ]]; then
                _log $*
            fi
            ;;
        "ERROR")
            if [[ $1 == "ERROR" ]]; then
                _log $*
            fi
            ;;
        *)
            _log $*
            ;;
    esac
}

function log_info()
{
    log "INFO" $*
}

function log_error()
{
    log "ERROR" $*
}

function log_debug()
{
    log "DEBUG" $*
}

function log_warn()
{
    log "WARN" $*
}



