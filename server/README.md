# Server Stuff
This folder contains files used in our production environment to run the [rostersniper.com](https://rostersniper.com) website. These files are not needed to run the project in a development environment.

### rostersniper.com.conf
This is our nginx web server configuration file. Here, nginx is told to server static files directly and pass all other requests to gunicorn.

### rs_gunicorn.socket
This systemd socket file creates an inter-process communication socket used by gunicorn and nginx. When an HTTP request comes in and nginx decides to send it to gunicorn (e.g. not /static/), it communicates over this socket. When gunicorn is ready with its response, it sends it back over this socket to nginx which then relays it to the original requester.

### rs_gunicorn.service
This systemd service file launches the gunicorn service with 3 worker processes.

### crontab
This file contains cron jobs that update RosterSniper's terms, sections, and favorites. To edit the file on the server, run `crontab -u rostersniper -e`.
