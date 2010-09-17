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

    encoded_url = hashlib.md5(url).hexdigest()
    now = time.mktime(datetime.datetime.now().timetuple())
    image_sizes = app.config['IMAGE_SIZES']
    format = app.config['SCREENGRAB_FORMAT']
    files = {}

    # grab this full size first
    original_path = grabscreen(url)
    files['o'] = original_path

    with open(original_path) as original:
        # compute the files md5
        md5 = hashlib.md5(original.read()).hexdigest()

        # if this does not exist in the db we need to
        # create the other image sizes and remove the
        # old meta.
        if not redis.exists('meta:%s' % md5):
            # remove old meta.
            redis.delete(redis.get('url:%s' % encoded_url))

            # create other sizes (might do this with pil at some point)
            source = Image.open(original_path)
            for label, size in image_sizes.items():
                width, height = size
                filename = '%s_%s' % (original_path, label)
                resizescreen(source, filename, format, width, height)
                files[label] = filename

            for label, path in files.items():
                # create s3 key
                key = Key(bucket)
                key.key = '%s/%s.%s' % (md5, label, format)

                # save file to s3
                key.set_contents_from_filename(path)

                # remove tmp file
                os.remove(path)

            # update database
            redis.hmset('meta:%s' % md5, {
                'folder': md5,
                'url': url,
                'updated': now,
            })
        else:
            redis.hset('meta:%s' % md5, 'updated', now)

        # link the url to the meta
        redis.set('url:%s' % encoded_url, md5)
    return True
