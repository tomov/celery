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
    return company 


def fetch_and_populate_company(db, linkedin_id, name):
    company = Company(linkedin_id, name)
    company = populate_company_from_crunchbase(company)
    db.session.add(company)
    return company
