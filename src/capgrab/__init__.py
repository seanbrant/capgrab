import base64
import datetime
import hashlib
import time
import urllib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import Flask, redirect, request
from redis import Redis


app = Flask(__name__)
app.config.from_object('capgrab.settings')

connection = S3Connection(
    aws_access_key_id=app.config['S3_ACCESS_KEY'],
    aws_secret_access_key=app.config['S3_SECRET_KEY'],
)
bucket = connection.get_bucket(app.config['S3_BUCKET_NAME'])

redis = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])


import capgrab.views  # so view functions get loaded
