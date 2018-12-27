import os
import zipfile
import binascii
from flask import Flask, render_template, request, session, redirect
import ujson
import logging

app = Flask(__name__)

app.secret_key = binascii.hexlify(os.urandom(24))

# GZIP
COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/csv', 'text/xml', 'application/json',
                      'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/sub', methods=['POST','GET'])
def hello_world():
    dic = ujson.load( open('data.json'))
    print(dic['users'])

    return ''


if __name__ == '__main__':
    app.run()
