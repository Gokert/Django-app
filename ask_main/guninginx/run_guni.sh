#!/bin/bash
gunicorn -c gun_conf.py hello:application
