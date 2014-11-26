import json
import urllib
import urllib2
from app.api_helpers.dropbox_helper import wget_to_dropbox

from app import celery
from app.models import db, User

SUPPORTED_FIELDS = [
        'local_picture_url'
]

# TODO move in separate module...
class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

def serialize_and_send_company_to_callback_url(user, callback_url):
    user_info = user.serialize_fields(SUPPORTED_FIELDS)
    print '  sending to callback url ' + str(callback_url)
    data = urllib.urlencode({'data': json.dumps(user_info)})
    req = urllib2.Request(callback_url, data)
    resp = urllib2.urlopen(req)
    resp_html = resp.read()
    print '  response to callback: ' + str(resp_html)

@celery.task(base=SqlAlchemyTask)
def fetch_store_and_link_user_image(picture_url, user_id, linkedin_id, name, callback_url, reupload = False):
    print 'Tttaask --> download user photo ' + name.encode('utf8') + ' ' + str(user_id) + ' -> ' + picture_url
    if not picture_url:
        # TODO better response
        return 'Sorry no picture url provided'
    user = User.from_user_id_in_main_db(user_id)
    if not user:
        user = User(user_id, linkedin_id, name, picture_url)
        db.session.add(user)
    if user.local_picture_url and not reupload:
        print 'User photo already uploaded.'
    else:
        # TODO test with unicodes
        filename = str(id) + '-' + name + '-' + linkedin_id + '-profpic'
        user.local_picture_url = wget_to_dropbox(picture_url, filename)
        db.session.commit()
        print 'Uploaded to ' + user.local_picture_url.encode('utf8')
    if callback_url:
        serialize_and_send_company_to_callback_url(user, callback_url)
    return 'DoonNe' # TODO better response
