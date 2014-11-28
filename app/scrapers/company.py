import json
import urllib
import urllib2
from datetime import datetime, timedelta
from celery.result import allow_join_result

from app import celery
from app.models import db, Company
from helpers import *
from app.api_helpers.crunchbase import crunchbase

# some nomenclature:
# 1) data vs. info
# company_data = raw unprocessed data about the company, e.g. from crunchbase
# company_info = interpreted data, parsed from _data; information == data with meaning
# 2) get vs. fetch
# get_company_url = get it from a db, or from a session var, or some other local resource
# fetch_company_url = make a sync or async call to a remote resource, either an API (e.g. crunchbase's API) or a remote startuplinx server
# 3) get/fetch vs. fill/update
# get/fetch return the answer
# fill/update fill it in place (i.e. you pass the thing to be updated as an argument)

EXPIRATION_DAYS = 60

# note that we do not update the company name
# you can use it to check if that was the real company you were supposed to fetch
# by comparing with the name in the data
SUPPORTED_FIELDS = [
        'crunchbase_url',
        'logo_url',
        'description',
        'summary',
        'website_url',
        'headquarters_json',
        'offices_json',
        'total_funding',
        'latest_funding_series',
        'latest_funding_amount',
        'valuation',
        'funding_rounds_json',
        'team_json',
        'team_size',
        'employees_min',
        'employees_max',
        'industries_json',
        'articles_json',
        'linkedin_url',
        'twitter_url',
        'facebook_url',
        'crunchbase_data'
]

DEFAULT_RESCRAPE_MODE = 'search'
SOFT_RESCRAPE_MODE = 'soft'
FROM_URL_RESCRAPE_MODE = 'from_url'

# TODO move in separate module...
class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

def get_crunchbase_path_from_crunchbase_url(url):
    parts = url.split('/')
    path = '/'.join(parts[3:])
    return path

def fetch_crunchbase_path_by_company_name(name):
    # do a search by the name and get the first result
    print 'looking up company ' + name
    name = urllib.quote_plus(name.encode('utf-8'))
    results = json.loads(crunchbase.get('organizations', {'name': name}))
    if len(results['data']['items']) == 0:
        return None
    result = results['data']['items'][0]
    return result['path'] 

def fetch_company_info_by_crunchbase_path(crunchbase_path):
    print '         fetch info from crunchbase path ' + crunchbase_path.encode('utf8')
    result_raw = crunchbase.get(crunchbase_path)
    result = json.loads(result_raw)
    web_prefix = result['metadata']['www_path_prefix']
    company_info = dict()
    company_info['crunchbase_url'] = web_prefix + crunchbase_path
    company_info['crunchbase_path'] = crunchbase_path
    fill_company_basics_from_crunchbase_data(company_info, result)
    fill_company_logo_from_crunchbase_data(company_info, result)
    fill_company_industries_from_crunchbase_data(company_info, result)
    fill_company_offices_from_crunchbase_data(company_info, result)
    fetch_and_fill_company_funding_rounds_from_crunchbase_data(company_info, result)
    fetch_and_fill_company_team_from_crunchbase_data(company_info, result)
    fill_company_websites_from_crunchbase_data(company_info, result)
    fill_company_articles_from_crunchbase_data(company_info, result)
    company_info['crunchbase_data'] = result_raw
    print 'done with ' + crunchbase_path.encode('utf8')
    return company_info

def update_company_with_crunchbase_info(company, company_info):
    print '  populate company w/ crunchbase data ' + str(company.name.encode('utf8'))
    updated_count = 0
    if company_info:
        updated_count += company.deserialize_fields(SUPPORTED_FIELDS, company_info)
    company.last_crunchbase_update = datetime.now()
    print 'DONE! ' + company.name.encode('utf8') + ' at ' + str(company.last_crunchbase_update) + ' ; total fields updated = ' + str(updated_count) + ' out of ' + str(len(SUPPORTED_FIELDS)) + ' fields'

# we cannot directly return a Company object from the task
# b/c it doesn't serialize well with Celery and it comes out as shit
# on the other end
@celery.task()
def fetch_company_info_from_crunchbase(company):
    print '   Task! scrape company from crunchbase ' + company.name.encode('utf8')
    if company.crunchbase_url:
        print '            try with crunchbase url = ' + company.crunchbase_url.encode('utf8')
        crunchbase_path = get_crunchbase_path_from_crunchbase_url(company.crunchbase_url)
    else:
        print '            try by name'
        crunchbase_path = fetch_crunchbase_path_by_company_name(company.name)
    if not crunchbase_path:
        print '            no crunchbase path found... returning None'
        return None
    company_info = fetch_company_info_by_crunchbase_path(crunchbase_path)
    return company_info

def serialize_and_send_company_to_callback_url(company, callback_url):
    company_info = company.serialize_fields(SUPPORTED_FIELDS)
    company_info['remote_id'] = company.id
    print '  sending to callback url ' + str(callback_url)
    data = urllib.urlencode({'data': json.dumps(company_info)})
    req = urllib2.Request(callback_url, data)
    resp = urllib2.urlopen(req)
    resp_html = resp.read()
    print '  response to callback: ' + str(resp_html)

# Given a company name and linkedin id,
# 1) check if it exists in the db, first by linkedin id then by name
# 2) if it doesn't exist or exists but hasn't been updated in a while,
#    fetch and update it with crucnhbase/angellist/etc data
# 3) return the company to the callback url, if one is provided
#    note that this will still send back results even if nothing was fetched from crunchbase
#     i.e. it will update from the "cache" = the MySQL db 
#
# note that if crunchbase_url is provided, it is assumed that we will use that, and not
# the name, to find the company in crunchbase
#
@celery.task(base=SqlAlchemyTask)
def fetch_and_populate_company(name, linkedin_id, callback_url=None, crunchbase_url=None):
    print 'TASK! fetch company ' + str(name.encode('utf8')) + ', ' + str(linkedin_id)

    # 1) Try to find company in database by linkedin id or by name
    if not linkedin_id:
        # TODO make intelligent disambiguiation based on name
        return 'Sorry no linkedin id'
    company = Company.from_linkedin_id(linkedin_id)
    if not company:
        print '                     linkedin id not found; fetching by name...'
        company = Company.from_name(name)

    # 2) fetch it from crunchbase if it doesn't exist or is outdated
    company_info = None
    if company:
        print '    ...company already exists as ' + str(company.name.encode('utf8')) + ', ' + str(company.linkedin_id)
        if not company.last_crunchbase_update or company.last_crunchbase_update < datetime.now() - timedelta(days=EXPIRATION_DAYS):
            print '       crunchbase not updated for ' + str(EXPIRATION_DAYS) + ' days => updating'
            company_info = fetch_company_info_from_crunchbase.delay(company)
        elif crunchbase_url and company.crunchbase_url != crunchbase_url:
            print '       new crunchbase url ' + crunchbase_url.encode('utf8') + ' (old was ' + company.crunchbase_url.encode('utf8') + ')'
            company.crunchbase_url = crunchbase_url
            company_info = fetch_company_info_from_crunchbase.delay(company)
        else:
            print '       crunchbase updated recently => no crunchbase update necessary'
    else:
        print '     ...' + str(name.encode('utf8')) + ', ' + str(linkedin_id) + ' does not exist => new company' 
        company = Company(name, linkedin_id)
        company.crunchbase_url = crunchbase_url
        db.session.add(company)
        company_info = fetch_company_info_from_crunchbase.delay(company)

    with allow_join_result():
        if company_info:
            print '     waiting for crunchbase result'
            company_info = company_info.wait()
            update_company_with_crunchbase_info(company, company_info)
        db.session.commit()
  
    # 3) send back company to the mother ship
    print 'callback url = ' + str(callback_url)
    if callback_url:
        serialize_and_send_company_to_callback_url(company, callback_url)
    return 'Done?' # TODO return meaningful result 

# rescrape fields using locally stored data
# i.e. don't fetch from crunchbase -- it's expensive
# note that only some fields are refreshed -- the team and funding rounds are not
@celery.task(base=SqlAlchemyTask)
def soft_repopulate_company(company_id, callback_url=None):
    company = Company.query.get(company_id)
    if not company:
        # TODO better response
        return 'Sorry coundn\'t find company by id ' + str(company_id)
    if not company.crunchbase_data:
        # TODO better response
        return 'Sorry no crunchbase data'
    print 'SOFT! repopulate ' + company.name.encode('utf8') + ', ' + str(company.id)

    # reparse it
    result_raw = company.crunchbase_data
    result = json.loads(result_raw)
    company_info = dict()
    fill_company_basics_from_crunchbase_data(company_info, result)
    fill_company_logo_from_crunchbase_data(company_info, result)
    fill_company_industries_from_crunchbase_data(company_info, result)
    fill_company_offices_from_crunchbase_data(company_info, result)
    fill_company_websites_from_crunchbase_data(company_info, result)
    fill_company_articles_from_crunchbase_data(company_info, result)

    # store it
    update_company_with_crunchbase_info(company, company_info)
    db.session.commit()
  
    # send it back
    print 'callback url = ' + str(callback_url)
    if callback_url:
        serialize_and_send_company_to_callback_url(company, callback_url)
    return 'Done?' # TODO return meaningful result 
