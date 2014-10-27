import json
from flask import request

from app import app
from tasks import fetch_and_populate_company
from models import db
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
