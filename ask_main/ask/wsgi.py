"""
WSGI config for ask project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from guninginx.hello import simple_app


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ask.settings')

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']

#application = get_wsgi_application()
application = simple_app
