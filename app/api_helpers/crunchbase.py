# -*- coding: utf-8 -*-
import os
import urllib
import urllib2
import json
from time import sleep

CRUNCHBASE_USER_KEY = os.environ['CRUNCHBASE_USER_KEY'] 

class CrunchBaseAPI:
    url_template = 'http://api.crunchbase.com/v/2/{0}?user_key={1}{2}'
    orders = [
        'created_at+DESC',
        'created_at+ASC',
        'updated_at+DESC',
        'updated_at+ASC'
    ]

    def __init__(self, user_key):
        self.user_key = user_key

    def get(self, operation, params=dict()):
        other = "".join(['&' + str(k) + '=' + str(v) for k, v in params.iteritems()])
        url = CrunchBaseAPI.url_template.format(operation, self.user_key, other, )
        print '                            url = ' + url
        wait_secs = 1
        result = None
        while not result and wait_secs < 60:
            try:
                sleep(wait_secs)
                result = urllib2.urlopen(url).read()
            except:
                wait_secs += randint(1, 10)
                print '                    FAILED; waiting ' + str(wait_secs) + ' seconds and trying again...'
        return result

    def get_company_by_name(self, name):
        try:
            # do a search by the name and get the first result
            print 'looking up company ' + name
            name = urllib.quote_plus(name.encode('utf-8'))
            results = json.loads(crunchbase.get('organizations', {'name': name}))
            if len(results['data']['items']) == 0:
                return None
            image_prefix = results['metadata']['image_path_prefix']
            web_prefix = results['metadata']['www_path_prefix']
            result = results['data']['items'][0]
            company_info = dict()
            company_info['name'] = result['name']
            company_info['crunchbase_url'] = web_prefix + result['path']
            # fetch the page of the first result and get all the details
            result_raw = crunchbase.get(result['path'])
            result = json.loads(result_raw)
            if 'relationships' in result['data']:
                if 'primary_image' in result['data']['relationships'] and len(result['data']['relationships']['primary_image']['items']) > 0:
                    company_info['logo_url'] = image_prefix + result['data']['relationships']['primary_image']['items'][0]['path']
                if 'headquarters' in result['data']['relationships'] and len(result['data']['relationships']['headquarters']['items']) > 0:
                    city = str(result['data']['relationships']['headquarters']['items'][0].get('city'))
                    country = str(result['data']['relationships']['headquarters']['items'][0].get('country_code'))
                    if city:
                        company_info['headquarters'] = city
                    elif country:
                        company_info['headquarters'] = country
            if 'properties' in result['data']:
                if 'description' in result['data']['properties']:
                    company_info['description'] = result['data']['properties']['description']
                if 'short_description' in result['data']['properties']:
                    company_info['summary'] = result['data']['properties']['short_description']
            company_info['crunchbase_data'] = result_raw
        except:
            company_info = None
        return company_info


crunchbase = CrunchBaseAPI(CRUNCHBASE_USER_KEY)

"""
app = Flask(__name__)
app.debug = True
app.secret_key = 'development'


@app.route('/')
def index():
    company_info = crunchbase.get_company_by_name('406 Ventures')
    return json.dumps(company_info)


if __name__ == '__main__':
    app.run()
    """
