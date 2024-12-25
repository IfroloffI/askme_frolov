import os
import sys
from django.core.wsgi import get_wsgi_application
from waitress import serve


def simple_application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)

    get_params = environ.get('QUERY_STRING', '')

    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_params = environ['wsgi.input'].read(content_length).decode('utf-8')
    except (ValueError, KeyError):
        post_params = ''

    response_body = f"GET Parameters: {get_params}\nPOST Parameters: {post_params}"
    return [response_body.encode('utf-8')]

# ?хз, мб: python -m waitress --host=0.0.0.0 --port=8081 main_application:application
def main_application():
    sys.path.append('A:/PycharmProjects/askme_frolov/baseapp')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseapp.settings')

    application = get_wsgi_application()
    serve(application, host='0.0.0.0', port=8081)


if __name__ == "__main__":
    main_application()
