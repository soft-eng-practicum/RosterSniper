#!/bin/bash

sock_path="roster_sniper.sock"
if [ -n "$1" ]; then
    sock_path="$1"
fi
wsgi_path="roster_sniper.wsgi:application"

gunicorn --access-logfile - --workers 3 --bind unix:$sock_path $wsgi_path