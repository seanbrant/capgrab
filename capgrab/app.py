import datetime
import hashlib
import time

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


@app.route('/i/')
def serve():
    url = request.args['url'].strip()
    default_size = app.config['DEFAULT_SIZE']
    size = request.args.get('size', default_size)
    if size not in app.config['IMAGE_SIZES'].keys():
        size = default_size

    now = time.mktime(datetime.datetime.now().timetuple())
    encoded_url = hashlib.md5(url).hexdigest()
    md5 = redis.get('url:%s' % encoded_url)
    meta = None

    if md5:
        meta = redis.hgetall('meta:%s' % md5)

    if not meta:
        meta = {'folder': app.config['DEFAULT_FOLDER']}
        updatescreen.delay(url)
    elif (float(meta['updated']) - now) > app.config['STALE_AFTER']:
        updatescreen.delay(url)

    key = Key(bucket)
    key.key = '%s/%s.jpg' % (meta['folder'], size)
    url = key.generate_url(app.config['URL_TIMEOUT'])

    return redirect(url)


if __name__ == '__main__':
    app.run(debug=True)
