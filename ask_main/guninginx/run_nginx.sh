#!/bin/bash

sudo service nginx stop
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo service nginx start