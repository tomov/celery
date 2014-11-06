from datetime import datetime

from app import celery
from app.models import Company
from app.api_helpers.crunchbase import crunchbase

def populate_company_from_glassdoor(company):
    return company


def populate_company_from_angellist(company):
    return company 

def update_company_with_crunchbase_data(company, company_data):
    print '  populate company w/ crunchbase data ' + str(company.name)
    updated_count = 0
    if company_data:
        # TODO (de)serialize object properly once this is working smoothly
        updated_count += company.update('name', company_data['name'])
        updated_count += company.update('crunchbase_url', company_data.get('crunchbase_url'))
        updated_count += company.update('logo_url', company_data.get('logo_url'))
        updated_count += company.update('headquarters', company_data.get('headquarters'))
        updated_count += company.update('description', company_data.get('description'))
        updated_count += company.update('summary', company_data.get('summary'))
        updated_count += company.update('website_url', company_data.get('website_url'))
        updated_count += company.update('headquarters_json', company_data.get('headquarters_json'))
        updated_count += company.update('offices_json', company_data.get('offices_json'))
        updated_count += company.update('total_funding', company_data.get('total_funding'))
        updated_count += company.update('latest_funding_series', company_data.get('latest_funding_series'))
        updated_count += company.update('latest_funding_amount', company_data.get('latest_funding_amount'))
        updated_count += company.update('valuation', company_data.get('valuation'))
        updated_count += company.update('funding_rounds_json', company_data.get('funding_rounds_json'))
        updated_count += company.update('team_json', company_data.get('team_json'))
        updated_count += company.update('team_size', company_data.get('team_size'))
        updated_count += company.update('employees_min', company_data.get('employees_min'))
        updated_count += company.update('employees_max', company_data.get('employees_max'))
        updated_count += company.update('industries_json', company_data.get('industries_json'))
        updated_count += company.update('linkedin_url', company_data.get('linkedin_url'))
        updated_count += company.update('twitter_url', company_data.get('twitter_url'))
        updated_count += company.update('facebook_url', company_data.get('facebook_url'))
        updated_count += company.update('crunchbase_data', company_data['crunchbase_data'])
    company.last_crunchbase_update = datetime.now()
    print 'DONE! ' + str(company.name) + ' at ' + str(company.last_crunchbase_update) + ' ; total fields updated = ' + str(updated_count)

# we cannot directly return a Company object from the task
# b/c it doesn't serialize well with Celery and it comes out as shit
# on the other end
@celery.task()
def fetch_company_from_crunchbase(company):
    print '   Task! scrape company from crunchbase ' + str(company.name.encode('utf8'))
    company_data = crunchbase.fetch_company_by_name(company.name)
    return company_data

