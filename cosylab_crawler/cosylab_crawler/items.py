# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class CosylabItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    name = Field()
    category = Field()
    synonyms = Field()
    entity_name = Field()
    entity_category = Field()
    num_of_sharedFlavor = Field()
    wiki_page = Field()
