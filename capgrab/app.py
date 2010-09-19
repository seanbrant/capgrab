import base64
import datetime
import hashlib
import time
import urllib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import Flask, redirect, request
from redis import Redis

from capgrab.tasks import updatescreen


app = Flask(__name__)
app.config.from_object('capgrab.settings')

connection = S3Connection(
    aws_access_key_id=app.config['S3_ACCESS_KEY'],
    aws_secret_access_key=app.config['S3_SECRET_KEY'],
)
bucket = connection.get_bucket(app.config['S3_BUCKET_NAME'])

redis = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])


@app.route('/caps/<url>/')
@app.route('/caps/<url>/<size>/')
def caps(url, size=app.config['DEFAULT_SIZE']):
    url = base64.b16decode(url)

    default = request.args.get('default', None)
    print default

    if not url.startswith('http'):
        url = 'http://%s' % url

    if size not in app.config['IMAGE_SIZES'].keys():
        size = app.config['DEFAULT_SIZE']

    now = time.mktime(datetime.datetime.now().timetuple())
    url_md5 = hashlib.md5(url).hexdigest()
    meta = redis.hgetall('url:%s' % url_md5)

    if not meta:
        meta = {'folder': app.config['DEFAULT_FOLDER']}
        updatescreen.delay(url)
        if default:
            return redirect(default)
    elif (float(meta['updated']) - now) > app.config['STALE_AFTER']:
        updatescreen.delay(url)

    key = Key(bucket)
    key.key = '%s/%s.jpg' % (meta['folder'], size)
    url = key.generate_url(app.config['URL_TIMEOUT'])

    return redirect(url)


if __name__ == '__main__':
    app.run(debug=True)
