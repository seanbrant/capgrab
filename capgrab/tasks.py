import datetime
import hashlib
import os
import time

from boto.s3.key import Key
from PIL import Image
from celery.decorators import task


@task
def updatescreen(url):
    from capgrab.app import app, redis, bucket
    from capgrab.utils import grabscreen, resizescreen

    url_md5 = hashlib.md5(url).hexdigest()
    now = time.mktime(datetime.datetime.now().timetuple())
    image_sizes = app.config['IMAGE_SIZES']
    format = app.config['SCREENGRAB_FORMAT']
    files = {}

    if redis.exists('inprogress:%s' % url_md5):
        return True
    else:
        redis.setex('inprogress:%s' % url_md5, now, 60)

    original_path = grabscreen(url, url_md5)

    if original_path is False:
        redis.delete('inprogress:%s' % url_md5)
        return True

    files['o'] = original_path

    with open(original_path) as original:
        source = Image.open(original_path)
        for label, size in image_sizes.items():
            width, height = size
            filename = '%s_%s' % (original_path, label)
            resizescreen(source, filename, format, width, height)
            files[label] = filename

        for label, path in files.items():
            key = Key(bucket)
            key.key = '%s/%s.%s' % (url_md5, label, format)
            key.set_contents_from_filename(path)
            os.remove(path)

        redis.hmset('url:%s' % url_md5, {
            'folder': url_md5,
            'url': url,
            'updated': now,
        })

    redis.delete('inprogress:%s' % url_md5)
    return True
