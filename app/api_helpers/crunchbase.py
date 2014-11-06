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

    def fetch_company_by_name(self, name):
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
            if 'properties' in result['data']:
                # description
                company_info['description'] = result['data']['properties'].get('description')
                # summary
                company_info['summary'] = result['data']['properties'].get('short_description')
                # team size
                company_info['team_size'] = result['data']['properties'].get('number_of_employees')
                company_info['employees_min'] = result['data']['properties'].get('num_employees_min')
                company_info['employees_max'] = result['data']['properties'].get('num_employees_max')
                # total funding
                company_info['total_funding'] = result['data']['properties'].get('total_funding_usd')

            if 'relationships' in result['data']:
                # logo
                if 'primary_image' in result['data']['relationships'] and len(result['data']['relationships']['primary_image']['items']) > 0:
                    company_info['logo_url'] = image_prefix + result['data']['relationships']['primary_image']['items'][0]['path']
                # headquarters
                if 'headquarters' in result['data']['relationships'] and len(result['data']['relationships']['headquarters']['items']) > 0:
                    company_info['headquarters_json'] = json.dumps({
                        'city': result['data']['relationships']['headquarters']['items'][0].get('city'),
                        'region': result['data']['relationships']['headquarters']['items'][0].get('region'),
                        'country': result['data']['relationships']['headquarters']['items'][0].get('country_code')
                    })
                # industries
                industries = []
                if 'categories' in result['data']['relationships']:
                    for category_data in result['data']['relationships']['categories']['items']:
                        industries.append(category_data.get('name'))
                company_info['industries_json'] = json.dumps(industries)
                # offices
                offices = []
                if 'offices' in result['data']['relationships']:
                    for office_data in result['data']['relationships']['offices']['items']:
                        offices.append({
                            'city': office_data.get('city'),
                            'region': office_data.get('region'),
                            'country': office_data.get('country_code')
                        })
                company_info['offices_json'] = json.dumps(offices)
                # funding rounds
                funding_rounds = []
                company_info['latest_funding_amount'] = None
                company_info['latest_funding_series'] = None
                company_info['valuation'] = None
                if 'funding_rounds' in result['data']['relationships']:
                    for funding_round_info in result['data']['relationships']['funding_rounds']['items']:
                        funding_round_data = json.loads(crunchbase.get(funding_round_info['path']))
                        if 'data' in funding_round_data and 'properties' in funding_round_data['data']:
                            funding_round = {
                                'series':  funding_round_data['data']['properties'].get('series'),
                                'money_raised':  funding_round_data['data']['properties'].get('money_raised'),
                                'money_raised_currency_code': funding_round_data['data']['properties'].get('money_raised_currency_code'),
                                'money_raised_usd':  funding_round_data['data']['properties'].get('money_raised_usd'),
                                'post_money_valuation': funding_round_data['data']['properties'].get('post_money_valuation'),
                                'post_money_valuation_currency_code': funding_round_data['data']['properties'].get('post_money_valuation_currency_code'),
                                'announced_on_year': funding_round_data['data']['properties'].get('announced_on_year'),
                                'announced_on': funding_round_data['data']['properties'].get('announced_on')
                            }
                            if funding_round['series']:
                                funding_round['series'] = funding_round['series'].upper()
                            if funding_round['post_money_valuation'] and (funding_round['post_money_valuation'] > company_info['valuation'] or company_info['valuation'] is None):
                                company_info['valuation'] = funding_round['post_money_valuation']
                            if funding_round['money_raised_usd'] and (funding_round['money_raised_usd'] > company_info['latest_funding_amount'] or company_info['latest_funding_amount'] is None):
                                company_info['latest_funding_amount'] = funding_round['money_raised_usd']
                            if funding_round['series'] and (funding_round['series'] > company_info['latest_funding_series'] or company_info['latest_funding_series'] is None):
                                company_info['latest_funding_series'] = funding_round['series']
                        else:
                            funding_round = dict()
                        investments = []
                        if 'data' in funding_round_data and 'relationships' in funding_round_data['data'] and 'investments' in funding_round_data['data']['relationships']:
                            for investment_data in funding_round_data['data']['relationships']['investments']['items']:
                                investment = {
                                    'money_invested': investment_data.get('money_invested'),
                                    'money_invested_currency_code': investment_data.get('money_invested_currency_code'),
                                    'money_invested_usd': investment_data.get('money_invested_usd')
                                }
                                if 'investor' in investment_data:
                                    investment['investor_type'] = investment_data['investor'].get('type')
                                    if 'first_name' in investment_data['investor'] and 'last_name' in investment_data['investor']:
                                        investment['investor'] = str(investment_data['investor']['first_name']) + ' ' + investment_data['investor']['last_name']
                                    else:
                                        investment['investor'] = investment_data['investor'].get('name')
                                investments.append(investment)
                        funding_round['investments'] = investments 
                        funding_rounds.append(funding_round)
                    company_info['funding_rounds_json'] = json.dumps(funding_rounds)
                # team
                if 'current_team' in result['data']['relationships']:
                    team = []
                    for team_member_info in result['data']['relationships']['current_team']['items']:
                        team_member = {
                            'first_name': team_member_info.get('first_name'),
                            'last_name': team_member_info.get('last_name'),
                            'title': team_member_info.get('title')
                        }
                        team_member_data = json.loads(crunchbase.get(team_member_info['path']))
                        if 'data' in team_member_data and 'properties' in team_member_data['data']:
                            team_member['bio'] = team_member_data['data']['properties'].get('bio')
                        if 'data' in team_member_data and 'relationships' in team_member_data['data']:
                            if 'primary_image' in team_member_data['data']['relationships'] and len(team_member_data['data']['relationships']['primary_image']['items']) > 0:
                                team_member['photo_url'] = image_prefix + team_member_data['data']['relationships']['primary_image']['items'][0]['path']
                            if 'experience' in team_member_data['data']['relationships']:
                                experience = []
                                for position_data in team_member_data['data']['relationships']['experience']['items']:
                                    position = {
                                        'company': position_data.get('organization_name'),
                                        'title': position_data.get('title'),
                                        'date_started': position_data.get('started_on'),
                                        'date_ended': position_data.get('ended_on')
                                    }
                                    experience.append(position)
                                team_member['experience'] = experience
                        team.append(team_member)
                    company_info['team_json'] = json.dumps(team)
                # websites
                if 'websites' in result['data']['relationships']:
                    for website_data in result['data']['relationships']['websites']['items']:
                        url = website_data['url']
                        type = website_data['title'].lower()
                        if type == 'homepage':
                            company_info['website_url'] = url
                        elif type == 'twitter':
                            company_info['twitter_url'] = url
                        elif type == 'facebook':
                            company_info['facebook_url'] = url
                        elif type == 'linkedin':
                            company_info['linkedin_url'] = url

          # TODO go through all of them and make sure
                  # 1) all of the stuff you insert / append is added to company_info
                  # 2) you use .get() and will not fail if stuff is missing

            # raw crucnhbase data 
            #print 'COMPANY INFO ---> ' + str(company_info)
            company_info['crunchbase_data'] = result_raw
            print 'done with ' + str(name)
        except:
            company_info = None
            raise
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

