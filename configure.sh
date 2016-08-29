#!/bin/sh
# This should be called when the script is running

FOLDER="/tmp/SCRAPE"
SOCKET=$FOLDER'/SCRAPE_SOCKET'
GROUP=$(ps -ef | egrep '(httpd|apache2|apache)' | grep -v root | head -n1 | awk '{print $1}')

# Create the folder
mkdir -p $FOLDER

# Change the permissions
sudo chgrp -R $GROUP $FOLDER
sudo chmod -R 770 $FOLDER
sudo chmod -R g+s $FOLDER	# Not very useful
