import time
from datetime import datetime
from datetime import timedelta
from celery.result import allow_join_result

from app import celery
from models import db
from scrapers.company_scrapers import * 

EXPIRATION_DAYS = 7

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

@celery.task(base=SqlAlchemyTask)
def subtract_together(a, b):
    print 'executing task ' + str(a) + '-' + str(b)
    time.sleep(5)
    print 'done with task ' + str(a) + '-' + str(b)
    return int(a) + int(b)

@celery.task(base=SqlAlchemyTask)
def add_together(a, b):
    print 'executing task ' + str(a) + '+' + str(b)
    time.sleep(5)
    print 'done with task ' + str(a) + '+' + str(b)
    return int(a) + int(b)

@celery.task(base=SqlAlchemyTask)
def fetch_and_populate_company(name, linkedin_id):
    print 'TASK! fetch company ' + str(name) + ', ' + str(linkedin_id)
    crunchbase_result = None
    company_exists = False
    company = Company.from_linkedin_id(linkedin_id)
    if company:
        company_exists = True
        print '    ...linkedin id ' + str(linkedin_id) + ' already exists as ' + str(company.name)
        if not company.last_crunchbase_update or company.last_crunchbase_update < datetime.now() - timedelta(seconds=EXPIRATION_DAYS):
            print '       crunchbase not updated for 7 days => updating'
            crunchbase_result = fetch_company_from_crunchbase.delay(company)
        else:
            print '       crunchbase updated recently => no crunchbase update necessary'
    else:
        print '     ...' + str(name) + ', ' + str(linkedin_id) + ' does not exist => new company' 
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
    return 'Done?' # TODO return meaningful result 

