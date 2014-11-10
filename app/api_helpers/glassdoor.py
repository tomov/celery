import os
import urllib2
from flask import Flask, redirect, url_for, session, Blueprint

GLASSDOOR_PARTNER_ID = os.environ['GLASSDOOR_PARTNER_ID']
GLASSDOOR_PARTNER_KEY = os.environ['GLASSDOOR_PARTNER_KEY']

glassdoor_bp  = Blueprint('glassdoor_bp', __name__)

class GlassdoorAPI:
    url_template = 'http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p={0}&t.k={1}&action={2}{3}&userip=0.0.0.0&useragent='

    def __init__(self, partner_id, partner_key):
        self.partner_id = partner_id
        self.partner_key = partner_key

    def get(self, action, params=dict()):
        other = "".join(['&' + str(k) + '=' + str(v) for k, v in params.iteritems()])
        url = GlassdoorAPI.url_template.format(self.partner_id, self.partner_key, action, other, )
        print 'url = ' + url
        return urllib2.urlopen(url).read()


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

glassdoor = GlassdoorAPI(GLASSDOOR_PARTNER_ID, GLASSDOOR_PARTNER_KEY)

@glassdoor_bp.route('/glassdoor_company/<name>')
def glassdoor_company(name):
    me = glassdoor.get('employers', {'q': name})
    return str(me)

