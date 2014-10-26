import os
from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # this is a hack to make it work without SSL
# don't know how the other api's work without that...

ANGELLIST_APP_ID = os.environ['ANGELLIST_APP_ID']
ANGELLIST_APP_SECRET = os.environ['ANGELLIST_APP_SECRET'] 


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

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


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for('angellist_authorized', _external=True)
    return angellist.authorize(callback=callback)


@app.route('/login/authorized')
def angellist_authorized():
    resp = angellist.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = angellist.get('startups/6702')
    return jsonify(me.data)


@angellist.tokengetter
def get_angellist_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()

