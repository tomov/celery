import os
from flask import Flask

from queue import make_celery
from models import db
from models import DATABASE_URI
from api_helpers.linkedin import linkedin_bp
from api_helpers.glassdoor import glassdoor_bp
from api_helpers.angellist import angellist_bp 

app = Flask(__name__)

# celery task queue
app.config.update(
    CELERY_BROKER_URL='amqp://localhost//',
    CELERY_RESULT_BACKEND='amqp://localhost//',
    CELERY_ROUTES = {
        'app.scrapers.company_scrapers.fetch_and_populate_company': {'queue': 'company'},
        'app.scrapers.company_scrapers.fetch_company_from_crunchbase' : {'queue': 'crunchbase'}
    },
)
celery = make_celery(app)

# blueprints
app.register_blueprint(linkedin_bp)
app.register_blueprint(glassdoor_bp)
app.register_blueprint(angellist_bp)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db.init_app(app)

# for API's
app.secret_key = os.environ['APP_OAUTH_SECRET_KEY']

# the API endpoints
import endpoints
