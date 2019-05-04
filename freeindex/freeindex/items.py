# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FreeindexItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    post_code = scrapy.Field()
    telephone = scrapy.Field()
    mobile = scrapy.Field()
    website = scrapy.Field()
    short_desc = scrapy.Field()
    long_desc = scrapy.Field()
    categories = scrapy.Field()
    email = scrapy.Field()
    opening_hours = scrapy.Field()
    member_since = scrapy.Field()
    manually_reviewed = scrapy.Field()
    last_updated = scrapy.Field()
    social_media_urls = scrapy.Field()
    key_services = scrapy.Field()
    url = scrapy.Field()
