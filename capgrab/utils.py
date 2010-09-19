import os
import subprocess

from PIL import Image

from capgrab.app import app


def grabscreen(url, md5):
    out = os.path.join(app.config['TEMP_DIR'], '%s.%s' % \
        (md5, app.config['SCREENGRAB_FORMAT']))
    args = [
        app.config['CUTYCAP'],
        '--url=%s' % url,
        '--out=%s' % out,
        '--plugins=on',
    ]
    if app.config['USE_XVFB']:
        args = [
            'run-xvfb',
            '--server-args=-screen 0, 1024x768x24',
        ] + args
    try:
        subprocess.check_call(args)
    except Exception:
        return False
    return out


def resizescreen(source, outfile, format, width, height):
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
