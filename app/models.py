from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, date
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
    name = db.Column(db.Unicode(100, collation='utf8_general_ci'), index = True)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    headquarters_json = db.Column(db.Text(collation='utf8_general_ci'))
    founded_on = db.Column(db.Date)
    founded_on_year = db.Column(db.Integer)
    offices_json = db.Column(db.Text(collation='utf8_general_ci'))
    total_funding = db.Column(db.BigInteger)
    latest_funding_series = db.Column(db.String(length = 50))
    latest_funding_amount = db.Column(db.BigInteger)
    valuation = db.Column(db.Integer)
    funding_rounds_json = db.Column(db.Text(collation='utf8_general_ci'))
    team_json = db.Column(db.Text(collation='utf8_general_ci'))
    team_size = db.Column(db.Integer)
    employees_min = db.Column(db.Integer)
    employees_max = db.Column(db.Integer)
    summary = db.Column(db.Text(collation='utf8_general_ci'))
    description = db.Column(db.Text(collation='utf8_general_ci'))
    industries_json = db.Column(db.Text(collation='utf8_general_ci'))
    articles_json = db.Column(db.Text(collation='utf8_general_ci'))
    rating_glassdoor = db.Column(db.Float(precision = 32))
    glassdoor_url = db.Column(db.Text)
    crunchbase_url = db.Column(db.Text)
    crunchbase_path = db.Column(db.Text)
    angellist_url = db.Column(db.Text)
    linkedin_url = db.Column(db.Text)
    twitter_url = db.Column(db.Text)
    facebook_url = db.Column(db.Text)
    crunchbase_data = db.Column(db.Text(collation='utf8_general_ci'))
    crunchbase_funding_rounds_data = db.Column(db.Text(collation='utf8_general_ci'))
    crunchbase_team_data = db.Column(db.Text(collation='utf8_general_ci'))
    angellist_data = db.Column(db.Text(collation='utf8_general_ci'))
    glassdoor_data = db.Column(db.Text(collation='utf8_general_ci'))
    last_glassdoor_update = db.Column(db.DateTime)
    last_crunchbase_update = db.Column(db.DateTime)
    last_angellist_update = db.Column(db.DateTime)

    def __init__(self, name, linkedin_id):
        self.linkedin_id = linkedin_id
        self.name = name 

    # NOTE this is crucial! we do not update the value if it is NULL
    # this is b/ we often will only update a subset of the fields
    def update(self, field, value):
        if value is not None:
            setattr(self, field, value)
            return True
        return False

    def deserialize_fields(self, fields, company_info):
        updated_count = 0
        for field in fields:
            updated_count += self.update(field, company_info.get(field))
        return updated_count

    def serialize_fields(self, fields):
        company_info = dict()
        for field in fields:
            value = getattr(self, field)
            if type(value) is datetime or type(value) is date:
                try:
                    value = value.strftime('%Y-%m-%d')
                except:
                    value = None
            company_info[field] = value
        return company_info

    def __repr__(self):
        return '<Company %r %r>' % (self.linkedin_id, self.name)

    @staticmethod
    def from_linkedin_id(linkedin_id):
        return Company.query.filter_by(linkedin_id=str(linkedin_id)).first()

    @staticmethod
    def from_name(name):
        return Company.query.filter(Company.name.ilike(name)).first()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    user_id_in_main_db = db.Column(db.Integer, unique = True)
    linkedin_id = db.Column(db.String(length = 50), unique = True, index = True)
    email = db.Column(db.Unicode(100, collation='utf8_general_ci'), unique = True)
    name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    picture_url = db.Column(db.Text)
    local_picture_url = db.Column(db.Text)

    def __init__(self, user_id_in_main_db, linkedin_id, name, picture_url):
        self.user_id_in_main_db = user_id_in_main_db
        self.linkedin_id = linkedin_id
        self.name = name
        self.picture_url = picture_url

    def __repr__(self):
        return '<User %r %r>' % (self.linkedin_id, self.name)
    
    def serialize_fields(self, fields):
        user_info = dict()
        for field in fields:
            user_info[field] = getattr(self, field)
        return user_info 

    @staticmethod
    def from_linkedin_id(linkedin_id):
        return User.query.filter_by(linkedin_id=str(linkedin_id)).first()

    @staticmethod
    def from_user_id_in_main_db(user_id_in_main_db):
        return User.query.filter_by(user_id_in_main_db=str(user_id_in_main_db)).first()

def create_db():
    db.create_all()
