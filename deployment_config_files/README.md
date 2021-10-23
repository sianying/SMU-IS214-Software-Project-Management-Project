# Server Setup Guide

1. Install Nginx 
Use following command to install
    $ sudo amazon-linux-extras list | grep nginx
    $ sudo amazon-linux-extras enable nginx1
    $ sudo yum clean metadata
    $ sudo yum -y install nginx

Check Installation
`$ nginx -v`

2. Copy Files
* Copy frontend.conf to /etc/nginx/conf.d
* Copy backend.conf to /etc/nginx/conf.d
* Copy gunicorn.service to /etc/systemd/system
* Copy gunicorn.socket to /etc/systemd/system

3. Start Nginx
`sudo systemctl start nginx`

Use command `sudo systemctl enable nginx` to enable nginx on boot

4. Start Gunicorn Socket
`sudo systemctl enable --now gunicorn.socket`

5. Allow Jenkins to Restart Gunicorn Socket
Use `sudo visudo` to open sudoers file
Add the following
    Cmnd_Alias GUNICORN_CMND = /usr/bin/systemctl start gunicorn.socket, /usr/bin/systemctl restart gunicorn.socket, /usr/bin/systemctl stop gunicorn.socket

    jenkins ALL=(ALL) NOPASSWD: GUNICORN_CMND
