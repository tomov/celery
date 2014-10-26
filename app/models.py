from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import backref
from sqlalchemy import desc
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import UniqueConstraint
import os
import json

DATABASE_USER = os.environ['DATABASE_USER']
DATABASE_PASS = os.environ['DATABASE_PASS']
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_NAME = 'startuplinx' 
DATABASE_URI_TEMPLATE = "mysql://{0}:{1}@{2}/{3}?charset=utf8&init_command=set%20character%20set%20utf8"
DATABASE_URI = DATABASE_URI_TEMPLATE.format(DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_NAME)

db = SQLAlchemy()

def _get_datetime():
    return datetime.utcnow()

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=_get_datetime)
    modified = db.Column(db.DateTime, onupdate=_get_datetime)
    linkedin_id = db.Column(db.String(length = 50), index = True, unique = True)
    name = db.Column(db.String(length = 50), index = True)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    funding_amount = db.Column(db.String(length = 50))
    funding_series = db.Column(db.String(length = 50))
    offices = db.Column(db.Text)
    headquarters = db.Column(db.String(length = 50))
    funding_year = db.Column(db.Integer)
    investors = db.Column(db.Text)
    leadership = db.Column(db.Text)
    employees_min = db.Column(db.Integer)
    employees_max = db.Column(db.Integer)
    summary = db.Column(db.Text)
    description = db.Column(db.Text)
    industry = db.Column(db.String(length = 50))
    rating_glassdoor = db.Column(db.Float(precision = 32))
    glassdoor_url = db.Column(db.Text)
    crunchbase_url = db.Column(db.Text)
    angellist_url = db.Column(db.Text)
    linkedin_url = db.Column(db.Text)
    twitter_url = db.Column(db.Text)
    glassdoor_data = db.Column(db.Text)
    crunchbase_data = db.Column(db.Text)
    angellist_data = db.Column(db.Text)
    last_glassdoor_update = db.Column(db.DateTime)
    last_crunchbase_update = db.Column(db.DateTime)
    last_angellist_update = db.Column(db.DateTime)

    def __init__(self, name, linkedin_id):
        self.linkedin_id = linkedin_id
        self.name = name 

    def __repr__(self):
        return '<Company %r %r>' % (self.linkedin_id, self.name)

    @staticmethod
    def from_linkedin_id(linkedin_id):
        return Company.query.filter_by(linkedin_id=str(linkedin_id)).first()


def create_db():
    db.create_all()
