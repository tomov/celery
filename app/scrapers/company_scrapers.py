from datetime import datetime

from app import celery
from app.models import Company
from app.api_helpers.crunchbase import crunchbase

def populate_company_from_glassdoor(company):
    return company


def populate_company_from_angellist(company):
    return company 

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
    print '  populate company w/ crunchbase data ' + str(company.name)
    updated_count = 0
    if company_data:
        updated_count += company.deserialize_fields(supported_fields, company_data)
    company.last_crunchbase_update = datetime.now()
    print 'DONE! ' + str(company.name) + ' at ' + str(company.last_crunchbase_update) + ' ; total fields updated = ' + str(updated_count) + ' out of ' + str(len(supported_fields)) + ' fields'

# we cannot directly return a Company object from the task
# b/c it doesn't serialize well with Celery and it comes out as shit
# on the other end
@celery.task()
def fetch_company_from_crunchbase(company):
    print '   Task! scrape company from crunchbase ' + str(company.name.encode('utf8'))
    company_data = crunchbase.fetch_company_by_name(company.name)
    return company_data

