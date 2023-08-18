#!/bin/bash

rm -rf reports
mkdir reports

#with proxy cache
ab -c 10 -n 10000 http://localhost:80/ > reports/proxy.txt
#without proxy cache
ab -c 10 -n 10000 http://localhost:8081/ > reports/noproxy.txt
#static
ab -c 10 -n 10000 http://localhost/static/ > reports/nginx_static.txt