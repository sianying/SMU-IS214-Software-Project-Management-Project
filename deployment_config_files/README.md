# Server Setup Guide

## 1. Install Nginx 
Use following command to install<br>
```
$ sudo amazon-linux-extras list | grep nginx
$ sudo amazon-linux-extras enable nginx1
$ sudo yum clean metadata
$ sudo yum -y install nginx
```
## 2. Check Installation 
```
nginx -v
```

## 3. Copy Files
* Copy frontend.conf to /etc/nginx/conf.d
* Copy backend.conf to /etc/nginx/conf.d
* Copy gunicorn.service to /etc/systemd/system
* Copy gunicorn.socket to /etc/systemd/system

## 4. Start Nginx 
```
sudo systemctl start nginx
sudo systemctl enable nginx
```
Second command to enable nginx on boot

## 5. Start Gunicorn Socket
`sudo systemctl enable --now gunicorn.socket`

## 6. Allow Jenkins to Restart Gunicorn Socket<br>
Use `sudo visudo` to open sudoers file<br>
Add the following
```
Cmnd_Alias GUNICORN_CMND = /usr/bin/systemctl start gunicorn.socket, /usr/bin/systemctl restart gunicorn.socket, /usr/bin/systemctl stop gunicorn.socket

jenkins ALL=(ALL) NOPASSWD: GUNICORN_CMND
```