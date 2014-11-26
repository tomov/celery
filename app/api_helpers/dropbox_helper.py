import os
import dropbox
import urllib
import json
import requests
from flask import Blueprint, render_template

DROPBOX_APP_ID = os.environ['DROPBOX_APP_ID']
DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']

# fucking dropbox API requires SSL for real authentication
# so for now, just manually generating the oauth token from the dropbox dev website
DROPBOX_OAUTH_TOKEN = os.environ['DROPBOX_OAUTH_TOKEN']

LOCAL_TEMP_DIRECTORY = './temp' # where to save the files locally -- this is w/ respect to run.py
DROPBOX_UPLOAD_DIRECTORY = '/' # where to put files in dropbox -- this is w/ respect to startuplinx directory

dropbox_bp = Blueprint('dropbox_bp', __name__)

client = dropbox.client.DropboxClient(DROPBOX_OAUTH_TOKEN)

def dropbox_share(path):
    res = client.share(path)
    r = requests.get(res['url'])
    url = r.url.split('?')[0]
    url += '?raw=1'
    return url

def dropbox_upload(local_path, dropbox_path):
    f = open(local_path, 'rb')
    res = client.put_file(dropbox_path, f)
    f.close()
    path = res['path']
    return path

def wget_to_dropbox(url, filename):
    opener = urllib.URLopener()
    local_path = os.path.join(LOCAL_TEMP_DIRECTORY, filename)
    opener.retrieve(url, local_path)
    try:
        dropbox_path = os.path.join(DROPBOX_UPLOAD_DIRECTORY, filename)
        dropbox_path = dropbox_upload(local_path, dropbox_path)
        dropbox_url = dropbox_share(dropbox_path)
    except:
        raise
    finally:
        os.remove(local_path)
    return dropbox_url

@dropbox_bp.route('/dropbox_bogus_wget')
def dropbox_bogus_wget():
    url = wget_to_dropbox('http://www.memsql.com/static/images/customers/zynga.png', 'w000t-zynga')
    return render_template('dropbox_bogus.html', img_url=url, data="bla")

@dropbox_bp.route('/dropbox_bogus_upload')
def dropbox_bogus_upload():
    path = dropbox_upload('temp/2000px-Smiley.svg.png', '/test_bla.png')
    url = dropbox_share(path)
    return render_template('dropbox_bogus.html', img_url=url, data="bla")

@dropbox_bp.route('/dropbox_bogus_share')
def dropbox_bogus_share():
    url = dropbox_share('/test_smiley.png')
    return render_template('dropbox_bogus.html', img_url=url, data="bla")

