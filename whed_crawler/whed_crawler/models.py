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

from whed_crawler import settings

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
    __tablename__ = "whed_data"
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
    header = Column(UnicodeText)
    street = Column(UnicodeText)
    city = Column(UnicodeText)
    post_code = Column(Unicode(50))
    tel = Column(Unicode(50))
    fax = Column(Unicode(50))
    web = Column(Unicode(255))
    ins_funding = Column(UnicodeText)
    history = Column(UnicodeText)
    academic_year = Column(UnicodeText)
    admission_requirements = Column(UnicodeText)
    language = Column(Unicode(255))
    student_body = Column(UnicodeText)
    head = Column(UnicodeText)
    head_job_title = Column(UnicodeText)
    senior_admin_officer = Column(UnicodeText)
    senior_admin_officer_jt = Column(UnicodeText)
    student_services = Column(UnicodeText)
    staff_sta_year = Column(Unicode(100))
    staff_full_time_total = Column(Unicode(50))
    staff_with_doctorate = Column(UnicodeText)
    stu_sta_year = Column(Unicode(100))
    stu_total = Column(Unicode(50))
    url = Column(UnicodeText)
