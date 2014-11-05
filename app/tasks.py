import time
from datetime import datetime
from datetime import timedelta
import json
import urllib
import urllib2
from celery.result import allow_join_result

from app import celery
from models import db
from scrapers.company_scrapers import * 

EXPIRATION_DAYS = 30

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

@celery.task(base=SqlAlchemyTask)
def fetch_and_populate_company(name, linkedin_id, callback_url=None):
    print 'TASK! fetch company ' + str(name.encode('utf8')) + ', ' + str(linkedin_id)
    crunchbase_result = None
    company_exists = False
    if not linkedin_id:
        # TODO make intelligent disambiguiation based on name
        return 'Sorry no linkedin id'
    company = Company.from_linkedin_id(linkedin_id)
    if company:
        company_exists = True
        print '    ...linkedin id ' + str(linkedin_id) + ' already exists as ' + str(company.name.encode('utf8'))
        if not company.last_crunchbase_update or company.last_crunchbase_update < datetime.now() - timedelta(days=EXPIRATION_DAYS):
            print '       crunchbase not updated for 7 days => updating'
            crunchbase_result = fetch_company_from_crunchbase.delay(company)
        else:
            print '       crunchbase updated recently => no crunchbase update necessary'
    else:
        print '     ...' + str(name.encode('utf8')) + ', ' + str(linkedin_id) + ' does not exist => new company' 
        company = Company(name, linkedin_id)
        crunchbase_result = fetch_company_from_crunchbase.delay(company)

    with allow_join_result():
        if crunchbase_result:
            print '     waiting for crunchbase result'
            company_data = crunchbase_result.wait()
            populate_company_with_crunchbase_data(company, company_data)
        if not company_exists:
            db.session.add(company)
        db.session.commit()

    print 'callback url = ' + str(callback_url)
    if callback_url:
        company_data = {
                'name': company.name,
                'remote_id': company.id,
                'crunchbase_url': company.crunchbase_url,
                'logo_url': company.logo_url,
                'headquarters': company.headquarters,
                'description': company.description,
                'summary': company.summary
        }
        print '  sending to callback url ' + str(callback_url)
        data = urllib.urlencode({'data': json.dumps(company_data)})
        req = urllib2.Request(callback_url, data)
        resp = urllib2.urlopen(req)
        resp_html = resp.read()
        print '  response to callback: ' + str(resp_html)
    return 'Done?' # TODO return meaningful result 

