import base64
import datetime
import hashlib
import time

from boto.s3.key import Key
from flask import redirect, request

from capgrab import app, redis, bucket
from capgrab.tasks import updatescreen


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
