#!/bin/bash

sock_path="/var/www/rostersniper.com/roster_sniper.sock"
wsgi_path="roster_sniper.wsgi:application"

gunicorn --access-logfile - --workers 3 --bind unix:$sock_path $wsgi_path