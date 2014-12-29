import json
import urllib
import urllib2
from datetime import datetime, timedelta

from app.api_helpers.crunchbase import crunchbase
 
def fill_company_basics_from_crunchbase_data(company_info, result):
    if 'properties' in result['data']:
        # name
        # keep in mind we don't update it but only use it to
        # ensure it's the right one with the linkedin name
        company_info['name'] = result['data']['properties'].get('name')
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
        # founded on
        company_info['founded_on'] = result['data']['properties'].get('founded_on')
        company_info['founded_on_year'] = result['data']['properties'].get('founded_on_year')

def fill_company_basics_from_linkedin_data(company_info, result):
    # name
    # unlike with crunchbase, here we are positive that the name is correct
    # b/c this is where it came from in the first place in the linkedin position
    company_info['name'] = result.get('name')
    # description
    company_info['description'] = result.get('description')
    # summary
    # ...linkedin doesn't have a short summary. Shame
    # founded on
    company_info['founded_on_year'] = result.get('foundedYear')
    # website
    company_info['website_url'] = result.get('websiteUrl')
    # logo -- it's REALLY shitty
    company_info['logo_url'] = result.get('logoUrl')

def fill_company_team_size_from_linkedin_data(company_info, result):
    if 'employeeCountRange' in result and 'name' in result['employeeCountRange'] and 'code' in result['employeeCountRange']:
        code = result['employeeCountRange']['code']
        if code == 'A':
            company_info['employees_min'] = 1
            company_info['employees_max'] = 1
            company_info['team_size'] = 1
        else:
            limits = result['employeeCountRange']['name'].split('-')
            if len(limits) > 1:
                company_info['employees_min'] = int(limits[0])
                company_info['employees_max'] = int(limits[1])

def fill_company_email_domains_from_linkedin_data(company_info, result):
    if 'emailDomains' in result and 'values' in result['emailDomains'] and len(result['emailDomains']['values']) > 0:
        company_info['email_domains_json'] = json.dumps(result['emailDomains']['values'])

def fill_company_logo_from_crunchbase_data(company_info, result):
    image_prefix = result['metadata']['image_path_prefix']
    if 'relationships' in result['data']:
        # logo
        if 'primary_image' in result['data']['relationships'] and len(result['data']['relationships']['primary_image']['items']) > 0:
            company_info['logo_url'] = image_prefix + result['data']['relationships']['primary_image']['items'][0]['path']

def fill_company_headquarters_from_crunchbase_data(company_info, result):
    if 'properties' in result['data']:
        # headquarters
        if 'headquarters' in result['data']['relationships'] and len(result['data']['relationships']['headquarters']['items']) > 0:
            company_info['headquarters_json'] = json.dumps({
                'city': result['data']['relationships']['headquarters']['items'][0].get('city'),
                'region': result['data']['relationships']['headquarters']['items'][0].get('region'),
                'country': result['data']['relationships']['headquarters']['items'][0].get('country')
            })

def fill_company_industries_from_crunchbase_data(company_info, result):
    industries = []
    if 'categories' in result['data']['relationships']:
        for category_data in result['data']['relationships']['categories']['items']:
            industries.append(category_data.get('name'))
    company_info['industries_json'] = json.dumps(industries)

def fill_company_industries_from_linkedin_data(company_info, result):
    industries = []
    if 'industries' in result and 'values' in result['industries'] and len(result['industries']['values']) > 0:
        for industry_data in result['industries']['values']:
            industries.append(industry_data.get('name'))
    company_info['industries_json'] = json.dumps(industries)

def fill_company_offices_from_crunchbase_data(company_info, result):
    offices = []
    if 'offices' in result['data']['relationships']:
        for office_data in result['data']['relationships']['offices']['items']:
            offices.append({
                'city': office_data.get('city'),
                'region': office_data.get('region'),
                'country': office_data.get('country')
            })
    company_info['offices_json'] = json.dumps(offices)

def fill_company_offices_from_linkedin_data(company_info, result):
    offices = []
    if 'locations' in result:
        for location_data in result['locations']:
            if 'address' in location_data:
                offices.append({
                    'city': location_data['address'].get('city'),
                    'state': location_data['address'].get('state'),
                    'region_code': location_data['address'].get('regionCode'),
                    'country_code': location_data['address'].get('countryCode')
                })
    company_info['offices_json'] = json.dumps(offices)

def fetch_and_fill_company_funding_rounds_from_crunchbase_data(company_info, result):
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
                            investment['investor'] = investment_data['investor']['first_name'] + ' ' + investment_data['investor']['last_name']
                        else:
                            investment['investor'] = investment_data['investor'].get('name')
                    investments.append(investment)
            funding_round['investments'] = investments 
            funding_rounds.append(funding_round)
        company_info['funding_rounds_json'] = json.dumps(funding_rounds)

def fetch_and_fill_company_team_from_crunchbase_data(company_info, result):
    image_prefix = result['metadata']['image_path_prefix']
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

def fill_company_websites_from_crunchbase_data(company_info, result):
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

def fill_company_articles_from_crunchbase_data(company_info, result):
    if 'news' in result['data']['relationships']:
        articles = []
        for news_data in result['data']['relationships']['news']['items']:
            articles.append({
                'url': news_data.get('url'),
                'title': news_data.get('title'),
                'author': news_data.get('author'),
                'posted_on': news_data.get('posted_on')
            })
        company_info['articles_json'] = json.dumps(articles)
