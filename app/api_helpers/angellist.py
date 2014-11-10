import os
from flask import Flask, render_template, redirect, url_for, session, request, Blueprint
from flask_oauthlib.client import OAuth, OAuthException
import json
import urllib

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # this is a hack to make it work without SSL
# don't know how the other api's work without that...

ANGELLIST_APP_ID = os.environ['ANGELLIST_APP_ID']
ANGELLIST_APP_SECRET = os.environ['ANGELLIST_APP_SECRET'] 

angellist_bp  = Blueprint('angellist_bp', __name__)
oauth = OAuth(angellist_bp)

angellist = oauth.remote_app(
    'angellist',
    consumer_key=ANGELLIST_APP_ID,
    consumer_secret=ANGELLIST_APP_SECRET,
    request_token_params={
        'scope': 'email',
        'state': 'RandomString'
    },
    base_url=' https://api.angel.co/1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://angel.co/api/oauth/token',
    authorize_url='https://angel.co/api/oauth/authorize'
)


@angellist_bp.route('/angellist_home')
def angellist_home():
    return render_template('angellist_home.html', token=session.get('angellist_token'))

@angellist_bp.route('/angellist_login')
def angellist_login():
    callback = url_for('angellist_bp.angellist_authorized', _external=True)
    return angellist.authorize(callback=callback)

@angellist_bp.route('/angellist_logout')
def angellist_logout():
    session.pop('angellist_token', None)
    return redirect(url_for('angellist_bp.angellist_home'))

@angellist_bp.route('/angellist_authorized')
def angellist_authorized():
    resp = angellist.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['angellist_token'] = (resp['access_token'], '')
    return redirect(url_for('angellist_bp.angellist_home'))

@angellist_bp.route('/angellist_search/<name>')
def angellist_search(name):
    name = urllib.quote_plus(name.encode('utf-8'))
    result = angellist.get('search?query=' + name + '&type=Startup')
    return json.dumps(result.data)

@angellist_bp.route('/angellist_startup_with_id/<id>')
def angellist_startup_with_id(id):
    result = angellist.get('startups/' + str(id))
    return json.dumps(result.data)

@angellist.tokengetter
def get_angellist_oauth_token():
    return session.get('angellist_token')

