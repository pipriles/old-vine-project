#!/bin/sh

FOLDER="/tmp/SCRAPE"
GROUP=$(ps -ef | egrep '(httpd|apache2|apache)' | grep -v root | head -n1 | awk '{print $1}')

mkdir -p $FOLDER
sudo chgrp -R $GROUP $FOLDER
sudo chmod -R 770 $FOLDER
sudo chmod -R g+s $FOLDER
