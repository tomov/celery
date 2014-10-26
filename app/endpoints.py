from app import app
from tasks import add_together, fetch_and_populate_company, subtract_together
from models import db
from models import create_db

@app.route('/')
def index():
    return 'Hello'

@app.route('/init_stuff')
def init_stuff():
    create_db()
    return 'Database created!'

# TODO remove in prod
@app.route('/sub/<a>/<b>')
def sub(a, b):
    result = subtract_together.delay(a, b)
    #ans = result.wait()
    return str('sub waiting..')

# TODO remove in prod
@app.route('/add/<a>/<b>')
def add(a, b):
    result = add_together.delay(a, b)
    #ans = result.wait()
    return str('add waiting..')

@app.route('/scrape_company/<name>/<linkedin_id>')
def scrape_company(name, linkedin_id):
    result = fetch_and_populate_company.delay(name, linkedin_id)
    return 'Fetching company {0}, {1}...'.format(name, linkedin_id)

@app.route('/scrape_companies', methods = ['POST'])
def scrape_companies():
    data = json.loads(request.values.get('data'))
    print 'received request : ' + str(data)
    for company_data in data:
        name = company_data['name']
        linkedin_id = company_data['linkedin_id']
        print 'Fetching company {0}, {1}...'.format(name, linkedin_id)
        fetch_and_populate_company(name, linkedin_id)
    return 'Yolobro' # TODO return meaningful response
