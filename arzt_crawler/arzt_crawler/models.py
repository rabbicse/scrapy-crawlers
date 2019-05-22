#! -*- coding: utf-8 -*-

"""
Web Scraper Project
Scrape data from a regularly updated website livingsocial.com and
save to a database (postgres).
Database models part - defines table for storing scraped data.
Direct run will create the table.
"""

from sqlalchemy import create_engine, Column, Integer, UnicodeText, Unicode
from sqlalchemy.ext.declarative import declarative_base

from arzt_crawler import settings

DeclarativeBase = declarative_base()


def db_connect():
    """Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance.
    """
    connection_str = 'mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8&use_unicode=1' % (
        settings.DATABASE['username'], settings.DATABASE['password'], settings.DATABASE['host'],
        settings.DATABASE['database'])
    return create_engine(connection_str)


def create_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class Model(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "azrt_data"
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    full_address = Column(UnicodeText)
    address = Column(UnicodeText)
    city = Column(UnicodeText)
    post_code = Column(Unicode(255))
    telephone = Column(UnicodeText)
    fax = Column(UnicodeText)
    website = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    area_of_expertise = Column(UnicodeText)
    therapy_areas_of_focus = Column(UnicodeText)
    patient_satisfaction = Column(UnicodeText)
    patient_service = Column(UnicodeText)
    email = Column(UnicodeText)
    facebook = Column(UnicodeText)
    twitter = Column(UnicodeText)
    instagram = Column(UnicodeText)
    linkedin = Column(UnicodeText)
    google_plus = Column(UnicodeText)
    youtube = Column(UnicodeText)
    url = Column(UnicodeText)
    spider = Column(Unicode(255))
