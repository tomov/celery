from flask_oauthlib.client import OAuth
from flask import url_for, Blueprint, session, redirect, request, render_template
import os


LINKEDIN_API_KEY = os.environ['LINKEDIN_API_KEY']
LINKEDIN_SECRET_KEY = os.environ['LINKEDIN_SECRET_KEY']

# NOTE: locally, always open as localhost:5000
# MAKE SURE that caching is disabled when testing...
# or test with /login

linkedin_bp = Blueprint('linkedin_bp', __name__)
oauth = OAuth(linkedin_bp)

USER_PROFILE_FIELDS = "(id,first-name,last-name,headline,site-standard-profile-request,picture_url,positions)"

print 'FUCKING haNDshaKE'
linkedin = oauth.remote_app(
    'linkedin',
    consumer_key=LINKEDIN_API_KEY,
    consumer_secret=LINKEDIN_SECRET_KEY,
    request_token_params={
        'scope': 'r_fullprofile,r_network,w_messages',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)
print 'done with handshake...'

@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')

def get_linkedin_id():
    return session.get('linkedin_id')

def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query

# User Scraper helpers

def fetch_current_linkedin_id():
    me = linkedin.get('people/~:(id)').data
    return me['id']

def fetch_current_linkedin_user_data():
    return linkedin.get('people/~:' + USER_PROFILE_FIELDS).data

def fetch_current_linkedin_user_connections_data():
    return linkedin.get('people/~/connections:' + USER_PROFILE_FIELDS).data

# Login helpers

@linkedin_bp.route('/linkedin_home')
def linkedin_home():
    return render_template('linkedin_home.html', token=session.get('linkedin_token'))

@linkedin_bp.route('/linkedin_login')
def linkedin_login():
    return linkedin.authorize(callback=url_for('linkedin_bp.linkedin_authorized', _external=True))

@linkedin_bp.route('/linkedin_logout')
def linkedin_logout():
    session.pop('linkedin_token', None)
    session.pop('linkedin_id', None)
    return redirect(url_for('linkedin_bp.linkedin_home'))

@linkedin_bp.route('/linkedin_authorized')
def linkedin_authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        message = 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
        return render_template('error', message=message)
    session['linkedin_token'] = (resp['access_token'], '')
    session['linkedin_id'] = fetch_current_linkedin_id()
    return redirect(url_for('linkedin_bp.login_callback'))

@linkedin_bp.route('/login_callback')
def login_callback():
    return redirect(url_for('linkedin_bp.linkedin_home')) 

# UX helpers

def post_linkedin_message(message):
    return linkedin.post('people/~/mailbox', data=message, content_type='application/json')

# Debuggin helpers TODO remove in prod

@linkedin_bp.route('/_linkedin_me')
def linkedin_me():
    me = fetch_current_linkedin_user_data()
    return me

@linkedin_bp.route('/_linkedin_connections')
def linkedin_connections():
    me = fetch_current_linkedin_user_connections_data()
    return me
