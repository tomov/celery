from app.models import Company
from app.api_helpers.crunchbase import crunchbase

def populate_company_from_glassdoor(company):
    return company


def populate_company_from_angellist(company):
    return company 

def populate_company_from_crunchbase(company):
    company_info = crunchbase.get_company_by_name(company.name)
    if company_info:
        company.name = company_info['name']
        company.crunchbase_url = company_info['crunchbase_url']
        company.logo_url = company_info.get('logo_url')
        company.headquarters = company_info.get('headquarters')
        company.description = company_info.get('description')
        company.summary = company_info.get('summary')
        company.crunchbase_data = company_info['crunchbase_data']
        print 'summary = ' + str(company.summary)
        print 'hq = ' + str(company.headquarters)
        print 'DONE! ' + str(company.crunchbase_data)
    print 'returning...'
    return company 

