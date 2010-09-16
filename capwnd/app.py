from boto.s3.connection import S3Connection
from boto.s3.key import Key
from itty import *
from redis import Redis


DEBUG = True

S3_BUCKET_NAME = 'capwnd'
S3_ACCESS_KEY = '0EMND7QMCXGS6ANXQKG2'
S3_SECRET_KEY = '1A6+dA7H89agWY7vmp8J/w7Y76BxCPfHuLPWqqhM'

DEFAULT_PATH = 'default'
IMAGE_SIZES = {
    's': (75, 75),
    't': (100, 63),
    'm': (640, 400),
    'l': (1024, 640),
}
DEFAULT_SIZE = 't'


def serve_image(request, path, size):
    connection = S3Connection(
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    )
    bucket = connection.get_bucket(S3_BUCKET_NAME)
    key = Key(bucket)
    key.key = '%s/%s.jpg' % (path, size)

    if DEBUG:
        data = key.get_contents_as_string()
        return Response(data, content_type='image/jpeg')

    return path


@get('/i/(?P<encoded_url>\w.+)/')
def serve(request, encoded_url):
    rdb = Redis()
    key = rdb.get(encoded_url)
    if key is None:
        return serve_image(request, DEFAULT_PATH, DEFAULT_SIZE)
    return 'HELLO'


def app(environ, start_response):
    return handle_request(environ, start_response)
