#! -*- coding: utf-8 -*-

"""
Web Scraper Project
Scrape data from a regularly updated website livingsocial.com and
save to a database (postgres).
Database models part - defines table for storing scraped data.
Direct run will create the table.
"""

from sqlalchemy import create_engine, Column, Integer, UnicodeText
from sqlalchemy.ext.declarative import declarative_base

from freeindex import settings

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


class FreeIndex(DeclarativeBase):
    """Sqlalchemy deals model"""
    # __tablename__ = "free_index_data"
    __tablename__ = "free_index_data_updated"
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
    address = Column(UnicodeText)
    city = Column(UnicodeText)
    post_code = Column(UnicodeText)
    telephone = Column(UnicodeText)
    mobile = Column(UnicodeText)
    website = Column(UnicodeText)
    short_desc = Column(UnicodeText)
    long_desc = Column(UnicodeText)
    categories = Column(UnicodeText)
    email = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    member_since = Column(UnicodeText)
    manually_reviewed = Column(UnicodeText)
    last_updated = Column(UnicodeText)
    social_media_urls = Column(UnicodeText)
    key_services = Column(UnicodeText)
    top_category = Column(UnicodeText)
    url = Column(UnicodeText)
