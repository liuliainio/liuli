#!/bin/bash - 
#===============================================================================
#
#          FILE: env.sh
# 
#         USAGE: ./env.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年12月13日 20时34分39秒 CST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

mode=
case `hostname` in
    "gmliaovm")
        mysql_conn='mysql -uroot -p1111 -hlocalhost market'
        mode=local
        ;;
    "ip-10-134-6-128")
        mysql_conn='mysql -udev_market -pmarket_dev_pwd -h10.134.6.128 market_india'
        mode=diandian-international
        ;;
    *)
        mysql_conn='mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market'
        mode=ct
        ;;
esac


