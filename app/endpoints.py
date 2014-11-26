import json
from flask import request

from app import app
from scrapers.company import fetch_and_populate_company, \
        soft_repopulate_company
from scrapers.user import fetch_store_and_link_user_image
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

# fetch them from crunchbase by name, if they don't exist
# if they do, rescrape them if haven't been rescraped recently
# store the newly rescraped data in company in db
# and return serialized company from db, regardless if we rescraped or no
@app.route('/scrape_companies', methods = ['POST'])
def scrape_companies():
    companies_info = json.loads(request.values.get('data'))
    print 'received request to scrape ' + str(len(companies_info)) + ' companies'
    for company_info in companies_info:
        name = company_info['name']
        linkedin_id = company_info['linkedin_id']
        callback_url = company_info['callback_url']
        print 'Fetching company {0}, {1}...'.format(name.encode('utf8'), linkedin_id)
        soft = company_info.get('soft')
        if soft:
            company_id = company_info['remote_id']
            print '           SOFT = ' + str(company_id)
            soft_repopulate_company.delay(company_id, callback_url)
        else:
            fetch_and_populate_company.delay(name, linkedin_id, callback_url)
    print '  finished scraping ' + str(len(companies_info)) + ' companies'
    return 'Yolobro' # TODO return meaningful response

# fetch them from crunchbase by name, if they don't exist
# if they do, rescrape them if haven't been rescraped recently
# store the newly rescraped data in company in db
# and return serialized company from db, regardless if we rescraped or no
@app.route('/scrape_user_images', methods = ['POST'])
def scrape_user_images():
    users_info = json.loads(request.values.get('data'))
    print 'received request to scrape ' + str(len(users_info)) + ' user images'
    for user_info in users_info:
        name = user_info['name']
        user_id = user_info['user_id']
        picture_url = user_info['picture_url']
        linkedin_id = user_info['linkedin_id']
        callback_url = user_info['callback_url']
        print 'Fetching user image {0}, {1}...'.format(name.encode('utf8'), picture_url)
        fetch_store_and_link_user_image.delay(picture_url, user_id, name, linkedin_id, callback_url)
    print '  finished scraping ' + str(len(users_info)) + ' users'
    return 'Yolo13RO' # TODO return meaningful response

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

