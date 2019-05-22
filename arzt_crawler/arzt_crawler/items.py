# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArztCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    full_address = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    post_code = scrapy.Field()
    telephone = scrapy.Field()
    fax = scrapy.Field()
    website = scrapy.Field()
    opening_hours = scrapy.Field()
    area_of_expertise = scrapy.Field()
    therapy_areas_of_focus = scrapy.Field()
    patient_satisfaction = scrapy.Field()
    patient_service = scrapy.Field()
    email = scrapy.Field()
    facebook = scrapy.Field()
    twitter = scrapy.Field()
    instagram = scrapy.Field()
    linkedin = scrapy.Field()
    google_plus = scrapy.Field()
    youtube = scrapy.Field()
    url = scrapy.Field()
    spider = scrapy.Field()
