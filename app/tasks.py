from app import celery

@celery.task()
def add_together(a, b):
    print 'executing task!'
    return int(a) + int(b)
