import json
import urllib
import urllib2
from datetime import datetime, timedelta
from celery.result import allow_join_result

from app import celery
from app.models import db, Company
from app.api_helpers.crunchbase import crunchbase

EXPIRATION_DAYS = 30

supported_fields = [
        'name',
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
        'linkedin_url',
        'twitter_url',
        'facebook_url',
        'crunchbase_data'
]

def update_company_with_crunchbase_data(company, company_data):
    print '  populate company w/ crunchbase data ' + str(company.name.encode('utf8'))
    updated_count = 0
    if company_data:
        updated_count += company.deserialize_fields(supported_fields, company_data)
    company.last_crunchbase_update = datetime.now()
    print 'DONE! ' + company.name.encode('utf8') + ' at ' + str(company.last_crunchbase_update) + ' ; total fields updated = ' + str(updated_count) + ' out of ' + str(len(supported_fields)) + ' fields'

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

# we cannot directly return a Company object from the task
# b/c it doesn't serialize well with Celery and it comes out as shit
# on the other end
@celery.task()
def fetch_company_from_crunchbase(company):
    print '   Task! scrape company from crunchbase ' + company.name.encode('utf8')
    company_data = crunchbase.fetch_company_by_name(company.name)
    return company_data

# Given a company name and linkedin id,
# 1) check if it exists in the db, first by linkedin id then by name
# 2) if it doesn't exist or exists but hasn't been updated in a while,
#    fetch and update it with crucnhbase/angellist/etc data
# 3) return the company to the callback url, if one is provided
#
@celery.task(base=SqlAlchemyTask)
def fetch_and_populate_company(name, linkedin_id, callback_url=None):
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
    company_exists = False
    crunchbase_result = None
    if company:
        company_exists = True
        print '    ...company already exists as ' + str(company.name.encode('utf8')) + ', ' + str(company.linkedin_id)
        if not company.last_crunchbase_update or company.last_crunchbase_update < datetime.now() - timedelta(days=EXPIRATION_DAYS):
            print '       crunchbase not updated for 7 days => updating'
            crunchbase_result = fetch_company_from_crunchbase.delay(company)
        else:
            print '       crunchbase updated recently => no crunchbase update necessary'
    else:
        print '     ...' + str(name.encode('utf8')) + ', ' + str(linkedin_id) + ' does not exist => new company' 
        company = Company(name, linkedin_id)
        crunchbase_result = fetch_company_from_crunchbase.delay(company)

    with allow_join_result():
        if crunchbase_result:
            print '     waiting for crunchbase result'
            company_data = crunchbase_result.wait()
            update_company_with_crunchbase_data(company, company_data)
        if not company_exists:
            db.session.add(company)
        db.session.commit()
  
    # 3) send back company to the mother ship
    print 'callback url = ' + str(callback_url)
    if callback_url:
        company_data = company.serialize_fields(supported_fields)
        company_data['remote_id'] = company.id
        print '  sending to callback url ' + str(callback_url)
        data = urllib.urlencode({'data': json.dumps(company_data)})
        req = urllib2.Request(callback_url, data)
        resp = urllib2.urlopen(req)
        resp_html = resp.read()
        print '  response to callback: ' + str(resp_html)
    return 'Done?' # TODO return meaningful result 

