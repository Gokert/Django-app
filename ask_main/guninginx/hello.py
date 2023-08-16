from pprint import pformat

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']


class AppClass:
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield "Hello world!\n"


def application(environ, start_response):

    output = []

    output.append('<form method="post">')
    output.append('<input type="text" name = "data">')
    output.append('<input type="submit" value="Send post data">')
    output.append('</form>')

    d = parse_qsl(environ['QUERY_STRING'])
    if environ['REQUEST_METHOD'] == 'POST':
        output.append(pformat(environ['wsgi.input'].read()))

    if environ['REQUEST_METHOD'] == 'GET':
        if environ['QUERY_STRING'] != '':
            output.append('<label>')
            for ch in d:
                output.append(' = '.join(ch))
            output.append('</label>')

    output_len = sum(len(line) for line in output)
    start_response('200 OK', [('Content-type', 'text/html'), ('Content-Length', str(output_len))])

    return output