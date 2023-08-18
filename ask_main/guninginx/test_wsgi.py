import urllib.parse
from pprint import pformat


def simple_app(environ, start_response):
    output = []

    output.append('<form method="post">')
    output.append('<div></div>')
    output.append('<input type="submit" value="Send post data">')
    output.append('</form>')

    d = urllib.parse.parse_qs(environ['QUERY_STRING'])
    if environ['REQUEST_METHOD'] == 'POST':
        output.append(pformat(environ['wsgi.input'].read()))

    if environ['REQUEST_METHOD'] == 'GET':
        if environ['QUERY_STRING'] != '':
            output.append('<label>')
            for ch in d:
                output.append(' = '.join(ch))
            output.append('</label>')

    output_str = '\n'.join(output)

    output_len = len(output_str)
    start_response('200 OK', [('Content-type', 'text/html'), ('Content-Length', str(output_len))])

    return [output_str.encode('utf-8')]


application = simple_app