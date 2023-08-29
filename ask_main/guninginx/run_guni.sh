#!/bin/bash
gunicorn -c guninginx/gun_conf.py ask.wsgi

