from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta
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

DATETIME_TO_MYSQL_FORMAT = '%Y-%m-%d %H:%M:%S'

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    linkedin_id = db.Column(db.String(length = 50), index = True, unique = True)
    name = db.Column(db.String(length = 50), index = True)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    headquarters_json = db.Column(db.Text)
    offices_json = db.Column(db.Text)
    total_funding = db.Column(db.BigInteger)
    latest_funding_series = db.Column(db.String(length = 50))
    latest_funding_amount = db.Column(db.BigInteger) 
    valuation = db.Column(db.Integer)
    funding_rounds_json = db.Column(db.Text)
    team_json = db.Column(db.Text)
    team_size = db.Column(db.Integer)
    employees_min = db.Column(db.Integer)
    employees_max = db.Column(db.Integer)
    summary = db.Column(db.Text)
    description = db.Column(db.Text)
    industries_json = db.Column(db.Text)
    rating_glassdoor = db.Column(db.Float(precision = 32))
    glassdoor_url = db.Column(db.Text)
    crunchbase_url = db.Column(db.Text)
    angellist_url = db.Column(db.Text)
    linkedin_url = db.Column(db.Text)
    twitter_url = db.Column(db.Text)
    facebook_url = db.Column(db.Text)
    glassdoor_data = db.Column(db.Text)
    crunchbase_data = db.Column(db.Text)
    crunchbase_funding_rounds_data = db.Column(db.Text)
    crunchbase_team_members_data = db.Column(db.Text)
    angellist_data = db.Column(db.Text)
    last_glassdoor_update = db.Column(db.DateTime)
    last_crunchbase_update = db.Column(db.DateTime)
    last_angellist_update = db.Column(db.DateTime)

    def __init__(self, name, linkedin_id):
        self.linkedin_id = linkedin_id
        self.name = name 

    def update(self, field, value):
        if value is not None:
            setattr(self, field, value)
            return True
        return False

    def deserialize_fields(self, fields, company_data):
        updated_count = 0
        for field in fields:
            updated_count += self.update(field, company_data.get(field))
        return updated_count

    def serialize_fields(self, fields):
        company_data = dict()
        for field in fields:
            company_data[field] = getattr(self, field)
        return company_data

    def __repr__(self):
        return '<Company %r %r>' % (self.linkedin_id, self.name)

    @staticmethod
    def from_linkedin_id(linkedin_id):
        return Company.query.filter_by(linkedin_id=str(linkedin_id)).first()

def create_db():
    db.create_all()
