# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AlleCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    price = scrapy.Field()
    surface = scrapy.Field()
    rooms = scrapy.Field()
    listing_url = scrapy.Field()
