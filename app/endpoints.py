import json
from flask import request

from app import app
from scrapers.company_scrapers import fetch_and_populate_company
from models import Company
from models import create_db

@app.route('/')
def index():
    return 'Hello'

@app.route('/init_stuff')
def init_stuff():
    create_db()
    return 'Database created!'

@app.route('/scrape_company/<name>/<linkedin_id>')
def scrape_company(name, linkedin_id):
    result = fetch_and_populate_company.delay(name, linkedin_id)
    return 'Fetching company {0}, {1}...'.format(name, linkedin_id)

@app.route('/scrape_companies', methods = ['POST'])
def scrape_companies():
    companies_data = json.loads(request.values.get('data'))
    print 'received request to scrape ' + str(len(companies_data)) + ' companies'
    for company_data in companies_data:
        name = company_data['name']
        linkedin_id = company_data['linkedin_id']
        callback_url = company_data['callback_url']
        print 'Fetching company {0}, {1}...'.format(name.encode('utf8'), linkedin_id)
        fetch_and_populate_company.delay(name, linkedin_id, callback_url)
    print '  finished scraping ' + str(len(companies_data)) + ' companies'
    return 'Yolobro' # TODO return meaningful response

@app.route('/get_company/<name>')
def get_company(name):
    company = Company.query.filter(Company.name.like('%' + name + '%')).one()
    if company:
        return company.crunchbase_data
    return 'No such company found...'

@app.route('/dedupe_company/<name>')
def dedupe_company(name):
    companies = Company.query.filter(Company.name.ilike(name)).all()
    for company in companies:
        print 'Found %s, id = %s' % (company.name.encode('utf8'), company.linkedin_id)
    return 'Bla'

