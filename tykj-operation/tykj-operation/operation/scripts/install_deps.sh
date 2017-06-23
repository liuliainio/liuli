#!/bin/bash
#
# This scripts is used to install dependencies for the application.
#
#
#
# python-software-properties depend by add-apt-repository to add nginx ppa
SYS_DEPS=(python-pip python-software-properties python2.7-dev libxml2-dev python-mysqldb libjpeg8-dev ia32-libs bsdiff libfreetype6-dev python-imaging imagemagick) # add python*-dev libxml2-dev for uwsgi

PYTHON_DEPS=("django==1.3.1" "uwsgi==2.0.6" "django-authority" "ordereddict" "django-chart-tools" "django-qsstats-magic" "django-google-charts" "python-dateutil" "django-pagination==1.0.7" PIL "pyExcelerator") # as i known, uwsgi newest version 1.2.1 doesn't work with nginx 1.2.0'

function install_dependencies()
{
   # update to latest to avoid some packages can not found.
   apt-get update
   echo "Installing required system packages..."
   for sys_dep in ${SYS_DEPS[@]};do
       install_sys_dep $sys_dep
   done
   echo "Installing required system packages finished."


   echo "Installing required python packages..."
   for python_dep in ${PYTHON_DEPS[@]};do
       install_python_dep ${python_dep}
   done
   echo "Installing required python packages finished."

}


function install_sys_dep()
{
    # input args  $1 package name
    if [ `apt-cache  search  $1  | grep -c "^i \+${1} \+"` = 0 ];then
        apt-get -y install  $1
    else
        echo "Package ${1} already installed."
    fi
}

function install_python_dep()
{
    # input args $1 like simplejson==1.0 ,can only extractly match
    if [ `pip freeze | grep -c "${1}"` = 0 ];then
        pip install  $1
    else
        echo "Python package ${1} already installed."
    fi
}
function install_java(){
    sudo add-apt-repository ppa:sun-java-community-team/sun-java6
    sudo apt-get update
    sudo apt-get install sun-java6-jdk
}
install_dependencies
install_java
