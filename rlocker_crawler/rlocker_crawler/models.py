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

from rlocker_crawler import settings

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
    __tablename__ = "rlocker_data"
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])

    id = Column(Integer, primary_key=True)
    item_id = Column(Unicode(255))
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    weight = Column(Unicode(255))
    amount = Column(Unicode(255))
    price = Column(Unicode(255))
    category = Column(UnicodeText)
    brand = Column(UnicodeText)
    variations = Column(UnicodeText)
    images_url = Column(UnicodeText)
    spider = Column(Unicode(255))
    url = Column(UnicodeText)


class UrlModel(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "url_data"
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])

    id = Column(Integer, primary_key=True)
    spider = Column(Unicode(255))
    url = Column(UnicodeText)
