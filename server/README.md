# Server Directory
This directory contains files used in our production environment to run the [rostersniper.com](https://rostersniper.com) website. These files are not needed to run the project in a development environment.

## nginx
This directory contains nginx web server configuration files. Here, nginx is told to server static files directly and pass all other requests to gunicorn.

## systemd
This directory contains systemd service and socket configuration files.

The `rs_gunicorn.socket` file creates an inter-process communication socket used by gunicorn and nginx. When an HTTP request comes in and nginx decides to send it to gunicorn (e.g. not /static/), it communicates over this socket. When gunicorn is ready with its response, it sends it back over this socket to nginx which then relays it to the original requester.

The `rs_gunicorn.service` file launches the gunicorn service with 3 worker processes.
