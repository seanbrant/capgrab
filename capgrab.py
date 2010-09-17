import base64
import datetime
import os
import subprocess
import uuid

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import Flask, redirect
from pyres import ResQ
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from redis import Redis


S3_BUCKET_NAME = 'capwnd'
S3_ACCESS_KEY = '0EMND7QMCXGS6ANXQKG2'
S3_SECRET_KEY = '1A6+dA7H89agWY7vmp8J/w7Y76BxCPfHuLPWqqhM'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

STALE_AFTER = 4320000  # 5 days

SCREENGRAB_TIMEOUT = 60
SCREENGRAB_WAIT = 0
SCREENGRAB_FORMAT = 'jpg'

TEMP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tmp')

DEFAULT_FOLDER = 'default'
DEFAULT_SIZE = 't'
FULL_SIZE = 'l'
IMAGE_SIZES = {
    's': (75, 75),
    't': (100, 63),
    'm': (640, 400),
    'l': (1024, 640),
}


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)


connection = S3Connection(
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)
bucket = connection.get_bucket(S3_BUCKET_NAME)

redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
queue = ResQ(server=redis)


@app.route('/i/<encoded_url>/')
@app.route('/i/<encoded_url>/<size>/')
def serve(encoded_url, size=DEFAULT_SIZE):
    sha1 = redis.get('url:%s' % encoded_url)
    if sha1:
        meta = redis.hgetall('meta:%s' % sha1)
    else:
        meta = {'folder': DEFAULT_FOLDER}
        UpdateScreenShotTask.perform(encoded_url)
        #queue.enqueue(UpdateScreenShotTask, encoded_url, size)

    key = Key(bucket)
    key.key = '%s/%s.jpg' % (meta['folder'], size)
    url = key.generate_url(30)

    return (url)


def grabscreen(url, path, width, height, timeout=SCREENGRAB_TIMEOUT,
        wait=SCREENGRAB_WAIT):
    p = subprocess.Popen([
        'python',
        'webkit2png.py',
        '-o', path,
        '-g', str(width), str(height),
        #'-t', str(timeout),
        #'-w', str(wait),
        url,
    ])
    print p.communicate()


def savescreen(path):
    print path


class UpdateScreenShotTask(object):
    queue = 'UpdateScreenShotTask'

    @staticmethod
    def perform(encoded_url):
        url = base64.b64decode(encoded_url)
        width, height = IMAGE_SIZES.get(FULL_SIZE)
        path = os.path.join(TEMP_DIR, '%s.png' % uuid.uuid4())
        grabscreen(url, path, width, height)
        savescreen(path)


if __name__ == "__main__":
    app.run(debug=True)
