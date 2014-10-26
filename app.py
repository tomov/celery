from tasks import make_celery
from flask import Flask

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://localhost//',
    CELERY_RESULT_BACKEND='amqp://localhost//'
)
celery = make_celery(app)


@celery.task()
def add_together(a, b):
    return a + b
