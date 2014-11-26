import os
from flask import redirect, url_for, session, request, jsonify, Blueprint, render_template
from flask_oauthlib.client import OAuth

DROPBOX_APP_ID = os.environ['DROPBOX_APP_ID']
DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']

dropbox_bp = Blueprint('dropbox_bp', __name__)
oauth = OAuth(dropbox_bp)

dropbox = oauth.remote_app(
    'dropbox',
    consumer_key=DROPBOX_APP_ID,
    consumer_secret=DROPBOX_APP_SECRET,
    request_token_params={},
    base_url='https://www.dropbox.com/1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.dropbox.com/1/oauth2/token',
    authorize_url='https://www.dropbox.com/1/oauth2/authorize',
)

@dropbox_bp.route('/dropbox_home')
def dropbox_home():
    data = []
    if 'dropbox_token' in session:
        me = dropbox.get('account/info')
        data = jsonify(me.data)
    return render_template('dropbox_home.html', token=session.get('dropbox_token'), data=data)

@dropbox_bp.route('/dropbox_login')
def dropbox_login():
    return dropbox.authorize(callback=url_for('dropbox_bp.dropbox_authorized', _external=True))

@dropbox_bp.route('/dropbox_logout')
def dropbox_logout():
    session.pop('dropbox_token', None)
    return redirect(url_for('dropbox_bp.dropbox_home'))

@dropbox_bp.route('/dropbox_authorized')
def dropbox_authorized():
    resp = dropbox.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['dropbox_token'] = (resp['access_token'], '')
    me = dropbox.get('account/info')
    return jsonify(me.data)

@dropbox.tokengetter
def get_dropbox_oauth_token():
    return session.get('dropbox_token')

