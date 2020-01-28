# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class WhedCrawlerItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    header = Field()
    street = Field()
    city = Field()
    post_code = Field()
    tel = Field()
    fax = Field()
    web = Field()
    ins_funding = Field()
    history = Field()
    academic_year = Field()
    admission_requirements = Field()
    language = Field()
    student_body = Field()
    head = Field()
    head_job_title = Field()
    senior_admin_officer = Field()
    senior_admin_officer_jt = Field()
    student_services = Field()
    staff_sta_year = Field()
    staff_full_time_total = Field()
    staff_with_doctorate = Field()
    stu_sta_year = Field()
    stu_total = Field()
    url = Field()

