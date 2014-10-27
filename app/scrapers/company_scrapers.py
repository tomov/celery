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
        company.crunchbase_data = company_data['crunchbase_data']
    company.last_crunchbase_update = datetime.now()
    print 'DONE! ' + str(company.name) + ' at ' + str(company.last_crunchbase_update)

@celery.task()
def fetch_company_from_crunchbase(company):
    print '   Task! scrape company from crunchbase ' + str(company.name)
    company_data = crunchbase.fetch_company_by_name(company.name)
    return company_data

