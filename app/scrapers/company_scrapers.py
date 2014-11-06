from datetime import datetime

from app import celery
from app.models import Company
from app.api_helpers.crunchbase import crunchbase

def populate_company_from_glassdoor(company):
    return company


def populate_company_from_angellist(company):
    return company 

def populate_company_with_crunchbase_data(company, company_data):
    print '  populate company w/ crunchbase data ' + str(company.name)
    if company_data:
        company.name = company_data['name']
        company.crunchbase_url = company_data['crunchbase_url']
        company.logo_url = company_data.get('logo_url')
        company.headquarters = company_data.get('headquarters')
        company.description = company_data.get('description')
        company.summary = company_data.get('summary')
        company.website_url = company_data.get('website_url')
        company.headquarters_json = company_data.get('headquarters_json')
        company.offices_json = company_data.get('offices_json')
        company.total_funding = company_data.get('total_funding')
        company.latest_funding_series = company_data.get('latest_funding_series')
        company.latest_funding_amount = company_data.get('latest_funding_amount')
        company.valuation = company_data.get('valuation')
        company.funding_rounds_json = company_data.get('funding_rounds_json')
        company.team_json = company_data.get('team_json')
        company.team_size = company_data.get('team_size')
        company.employees_min = company_data.get('employees_min')
        company.employees_max = company_data.get('employees_max')
        company.industries_json = company_data.get('industries_json')
        company.linkedin_url = company_data.get('linkedin_url')
        company.twitter_url = company_data.get('twitter_url')
        company.facebook_url = company_data.get('facebook_url')
        company.crunchbase_data = company_data['crunchbase_data']
    company.last_crunchbase_update = datetime.now()
    print 'DONE! ' + str(company.name) + ' at ' + str(company.last_crunchbase_update)

# we cannot directly return a Company object from the task
# b/c it doesn't serialize well with Celery and it comes out as shit
# on the other end
@celery.task()
def fetch_company_from_crunchbase(company):
    print '   Task! scrape company from crunchbase ' + str(company.name.encode('utf8'))
    company_data = crunchbase.fetch_company_by_name(company.name)
    return company_data

