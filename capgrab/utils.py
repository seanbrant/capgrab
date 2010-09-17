import os
import subprocess
import uuid

from PIL import Image

from capgrab.app import app


def grabscreen(url):
    uid = uuid.uuid4()
    out = os.path.join(app.config['TEMP_DIR'], '%s.%s' % \
        (uid, app.config['SCREENGRAB_FORMAT']))
    args = [
        app.config['CUTYCAP'],
        '--url=%s' % url,
        '--out=%s' % out,
        '--min-width=1100',
    ]
    subprocess.call(args)
    return out


def resizescreen(source, outfile, format, width, height):
    # special case for jpg
    if format in ('jpg'):
        format = 'jpeg'
    resized = crop(source, width, height)
    resized.save(outfile, format.upper(), quality=100)


def crop(source, width, height):
    sw, sh = source.size
    sr = float(sw) / float(sh)
    dw, dh = width, height
    dr = float(dw) / float(dh)
    if dr < sr:
        ch = sh
        cw = ch * dr
        x = float(sw - cw) / 2
        y = 0
    else:
        cw = sw
        ch = cw / dr
        x = 0
        y = 0
    new = source.crop((int(x), int(y), int(x) + int(cw), int(y) + int(ch)))
    new = new.resize((dw, dh), Image.ANTIALIAS)
    return new
