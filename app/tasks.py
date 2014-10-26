from app import celery
from models import db
from scrapers.company_scrapers import * 

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print 'terminate DB session...'
        db.session.remove()

@celery.task(base=SqlAlchemyTask)
def add_together(a, b):
    print 'executing task!'
    return int(a) + int(b)

@celery.task(base=SqlAlchemyTask)
def fetch_and_populate_company(name, linkedin_id):
    print 'TASK! fetch company ' + str(name) + ', ' + str(linkedin_id)
    company = Company(name, linkedin_id)
    company = populate_company_from_crunchbase(company)
    db.session.add(company)
    db.session.commit()
    return company

