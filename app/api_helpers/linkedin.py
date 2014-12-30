from flask_oauthlib.client import OAuth
from flask import url_for, Blueprint, session, redirect, request, render_template
import os
import json
from random import randint
from time import sleep

LINKEDIN_API_AND_SECRET_KEYS = [
    ('75cnrrov2108nt', 'ZOEzGxbyWYK33kp6'),
    ('75j8afjklkn1sg', 'ZIrbkkOEcP09GilL'),
    ('75mc0klssy9xa2', '9cH2HsWcjAVeoUVX'),
    ('75bjywlaawl50p', '0yxmOPsbbP9985N9'),
    ('75xzqjitlonw8j', 'BSm2D3RVe4DkCsQN'),
    ('751yv91hvwziyo', '5bsbxP5YCpLQcZWf'),
    ('75jpspf66ik6u8', 'QdfKBSv4U4TokabW'),
    ('75jrfiid84fhzs', 'UQgU0cZFFg6mTMyn'),
    ('755vf70f21zvd4', 'Ea5iGc6dsHKSNARH'),
    ('752138hwyfc3p7', 'IGtStQ5VIliQc086')
]

LINKEDIN_ACCESS_TOKENS = [
    (u'AQXE5NRz92I8DMtkmDBiqpOML2K1_uHRB8zTGS6Y1vv2TFDgeowJu9FS9EpxLiN_Ydgv0j1G871X220jnJRCmXjejf99L6fkwMBFKtf3ekU6oHUx86BQFJuNtvY3rhdJc3gJKAkjMMamRqYlUBWNWL4ye2nORlzIGtwT7GKoTd5EDdvUj6c', ''),
    (u'AQVHB4cHz_19-RHRArbD1Cvzoqzd2db4imqN6Ec-G93GVbz5ZSN4_mKKR2UQ46cwjgh_1XKMHoIQNd6lR6MDQCkZgkVsPB4d91LpL0PUgLKdTHjoDBKw2QGgLURlDdhu4xSW3JXL4dwH4fAWo6IlEDyY8QWrBLiw92iBcpMFlo-E9z7XG-0', ''),
    (u'AQVNvl3PTmblMSGIbYXno6oaN0u7qYIzNZsJIF0eRQIaowWhO8X8N2Ye19JvAxgSnNzQIvggbtLZ2IVob-AL0FVMMz2b838zfTTNUzitPQo9KyehkkfDZmdHIGQS5L4qdI5nxuovOF335h0po1oQ58LwdyBUR05O4Lr_0IrZaOgCy-AWKVg', ''),
    (u'AQW1HILxT1GUEwvTjOwXUfg0Pjq6tGvUQg2Uyv6N0pJmoKm-3wSwC1leCXK4CUMz7ooNFvfXM2feOOfHozUyNspFlnSSn_AmaZlyJjJzm3tQnOPByQM8KfCMugZTb3378iGzwzpAqs8ap38r6ZGVwYbcCfdRGbeT395LEn3lGIsNk41N60g', ''),
    (u'AQUIJMp7XgFE5Mqw-81W9f_qPg2myBinGppB3Ymuahgi1lZHIH3690t8a98haSQ_r9ueGZsrvbd_GEp2uq7nIreeHxgmwme58vo5pgt5h9jkceF6eofJl6QVT56YtUBmqw9K1aoVbAhPdnlEKFrqcVn57QiasQG5-1Vz4uuw0zjn-r_nDC0', ''),
    (u'AQViy47KGKMT3eq4491Gyn3Z60PbzocM6DEdADFKPzuR4dLXHEBRxDPXPnqCOLiuMjM9pXqlzBHNj_SGnl7O763O8wselFwdHSm1goHRLDO3V6FZhCJk1AEZK0IdLwvajg1OuUVahYmA3zZrciMSSXYZc_O55X52rsbSpgWMgQtO5h5-330', ''),
    (u'AQXkemRd3Xu55BEelG06mVYj3kvDO9q1JHVa0NV3QPNK6eh2MJrKcQYSzA4zbBRoOMXcbzlVi9GZd8AozgT0fYUXgxohA_x7gmU4CZ9LLLhKGLyKamQgZoowMutIP7a5ma7omw2EyXGwvCmOV1iOHt4bXyHLIFzHHonk85XrjW5XRnmOXh4', ''),
    (u'AQWbktlkjeh04NGEl1CUkwPQ4EBDfjtyS_kajVi-lzzf0kJNvNJ8gVnmt8OLP41tDC7W8RXwLfVwvnVAjA5WFF013N16p9M1X8tQNoAnE7bEhekM3q8fVE8WF0ibt4R0XY5nskp66P5L0EWm0QMh5FmtXSpvw_sDOpWqJ8Z7c4Nhpzjm7cc', ''),
    (u'AQW6Zi4fZD1FB8SNQV-eECabrfUprEbhCP314COSP_ZJKVPVIkjwGRx_QMD-wycViwSJUag6DQZiqSVfziFlcuQW15OEifaEg406EMVKjQFrQjKfHEhs77DsrO9FNCNjkqw-8g31dI9yADTRRW1TJrdMDSI6J9dnC-zqt7-O2OrEfHqFmrg', ''),
    (u'AQUjaGNX8Gix6zxP_4xNdwH2VJsvZRb-KyES6x6yd906J0JlnKJ8NaBYi1evSP8aX3-vA5PnGurhTDowwXvYqKSQedm3MCogC2O10MuPAWYXF3f_6fnoxjHmRh97EWMi_Vep9BwCppnFHfqjNbWywqKsYoWNipY_vP1kmsVkDwpuanvdtAE', '')
]

LINKEDIN_API_KEY = LINKEDIN_API_AND_SECRET_KEYS[9][0]
LINKEDIN_SECRET_KEY = LINKEDIN_API_AND_SECRET_KEYS[9][1]

# NOTE: locally, always open as localhost:5000
# MAKE SURE that caching is disabled when testing...
# or test with /login

linkedin_bp = Blueprint('linkedin_bp', __name__)
oauth = OAuth(linkedin_bp)

USER_PROFILE_FIELDS = "(id,first-name,last-name,email-address,headline,site-standard-profile-request,picture_url,positions)"
COMPANY_PROFILE_FIELDS = "(id,name,universal-name,email-domains,company-type,ticker,website-url,industries,status,logo-url,square-logo-url,blog-rss-url,twitter-id,employee-count-range,specialties,locations,description,stock-exchange,founded-year,end-year,num-followers)"

linkedin = oauth.remote_app(
    'linkedin',
    consumer_key=LINKEDIN_API_KEY,
    consumer_secret=LINKEDIN_SECRET_KEY,
    request_token_params={
        'scope': 'r_fullprofile,r_network,w_messages,r_emailaddress',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

@linkedin.tokengetter
def get_linkedin_oauth_token():
    # TODO FIXME this is a super retarded hack
    # temporary fix b/c there is no way I can log in via the celery queue...
    # this was made in late December, expires in 60 days
    # to make a new one, use .../linkedin_home
    return LINKEDIN_ACCESS_TOKENS[global_fucking_linkedin_access_token_idx]
   # return session.get('linkedin_token')

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

# Company scraper helpers

global_fucking_linkedin_access_token_idx = 0

def _next_token():
    global global_fucking_linkedin_access_token_idx
    global_fucking_linkedin_access_token_idx += 1
    if global_fucking_linkedin_access_token_idx >= len(LINKEDIN_ACCESS_TOKENS):
        global_fucking_linkedin_access_token_idx = 0

def _init_token_manually():
    global global_fucking_linkedin_access_token_idx
    global_fucking_linkedin_access_token_idx = 0

def fetch_linkedin_company_data(company_id):
    return linkedin.get('companies/' + company_id + ':' + COMPANY_PROFILE_FIELDS).data

def politely_fetch_linkedin_company_data(company_id):
    print '                                      id = ' + str(company_id)
    for attempt in range(len(LINKEDIN_ACCESS_TOKENS) * 3):
        print '      attempt #' + str(attempt)
        wait_secs = randint(1, 3)
        result = None
        while not result and wait_secs < 300:
            try:
                print '                                     waiting for ' + str(wait_secs) + ' sconds..'
                sleep(wait_secs)
                result = linkedin.get('companies/' + company_id + ':' + COMPANY_PROFILE_FIELDS).data
                if not result or not isinstance(result, dict) or 'errorCode' in result:
                    wait_secs *= 2
                    print '                         result = ' + str(result) + '; waiting for ' + str(wait_secs)
                    print '                     response from linkedin server: ' + str(result)
                    if result and 'status' in result and result['status'] == 403:
                        # 403 = throttle limit exceeded = failure for sure
                        # else, could be something like "Company with ID { 114956 is not active }"
                        result = None
                        if wait_secs > 10:
                            # if we know we're being throtteled, move on to next key faster
                            break
            except:
                wait_secs *= 2
                print '                            fail; waiting for ' + str(wait_secs)

        # if we failed with the current access token, move to different one
        if not result:
            _next_token()
            print '        .....this FUCKING token won\'t work; moving on to next one: ' + str(global_fucking_linkedin_access_token_idx) + ' -> ' + str(LINKEDIN_ACCESS_TOKENS[global_fucking_linkedin_access_token_idx])
        else:
            break

    if not result:
        print 'FUUUUUUUUUUCKKKKKKKK it didn\'t fucking work... fuck LInkedin'
    return result

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
    return json.dumps(me)

@linkedin_bp.route('/_linkedin_connections')
def linkedin_connections():
    me = fetch_current_linkedin_user_connections_data()
    return me

@linkedin_bp.route('/_linkedin_company/<company_id>')
def linkedin_company(company_id):
    data = fetch_linkedin_company_data(company_id)
    return json.dumps(data)
