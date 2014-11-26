import json
import urllib
import urllib2
from datetime import datetime, timedelta
from celery.result import allow_join_result

from app import celery
from app.models import db, User

# TODO move in separate module...
class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

@celery.task(base=SqlAlchemyTask)
def fetch_store_and_link_user_image(picture_url, user_id, linkedin_id, name, callback_url):
    print 'Tttaask --> download user photo ' + name.encode('utf8') + ' ' + str(user_id) + ' -> ' + picture_url
    if not picture_url:
        # TODO better response
        return 'Sorry no picture url provided'
    user = User.from_user_id_in_main_db(user_id)
    if not user:
        user = User(user_id, linkedin_id, name, picture_url)
        db.session.add(user)

