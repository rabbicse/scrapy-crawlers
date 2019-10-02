# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CloudsceneItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    operator = scrapy.Field()
    address = scrapy.Field()
    market = scrapy.Field()
    country = scrapy.Field()
    website = scrapy.Field()
    telephone = scrapy.Field()
    email = scrapy.Field()
    url = scrapy.Field()


class EuropagesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    supplier = scrapy.Field()
    website = scrapy.Field()
    desc = scrapy.Field()
    url = scrapy.Field()


class CesItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    brands = scrapy.Field()
    categories = scrapy.Field()
    contacts = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    phone = scrapy.Field()
    url = scrapy.Field()