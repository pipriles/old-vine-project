#!/bin/sh

FOLDER="/tmp/SCRAPE"

mkdir -p $FOLDER
chgrp -R www-data $FOLDER
chmod -R 770 $FOLDER
chmod -R g+s $FOLDER
