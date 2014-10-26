import os
from flask import Flask

from queue import make_celery
from models import db
from models import DATABASE_URI

app = Flask(__name__)

# celery task queue
app.config.update(
    CELERY_BROKER_URL='amqp://localhost//',
    CELERY_RESULT_BACKEND='amqp://localhost//'
)
celery = make_celery(app)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db.init_app(app)

# for API's
app.secret_key = os.environ['APP_OAUTH_SECRET_KEY']

# the API endpoints
import endpoints
