# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class GrowlightsSpider(scrapy.Spider):
    name = 'growlights'
    allowed_domains = ['growlights.ca']
    start_urls = ['http://growlights.ca/']

    def parse(self, response):
        # uri = 'https://www.growlights.ca/led-grow-lights/4ft-t5-xtreme-led-grow-light-336-watt.html'
        # yield Request(url=uri, callback=self.parse_details)
        links = response.xpath('//li[@class="level1"]/a/@href').getall()
        for link in links:
            url = link + '?limit=all'
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//h2[@class="product-name"]/a/@href').getall()
            for product in products:
                product_url = product
                query = {'url': product_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=product_url, callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(product_url))
        except:
            pass

        finally:
            session.close()

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        # try:
        #     item['item_id'] = response.xpath('//dd[@class="productView-info-value"]/text()').get().strip()
        # except:
        #     pass

        try:
            title = response.xpath('//h1[@itemprop="name"]/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//nav[@class="breadcrumbs"]/ul/li/a/span[@itemprop="title"]/text()').getall()
            for catalog in catalogs:
                if 'Home' in catalog:
                    continue

                cats.append(catalog.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        try:
            item['price'] = response.xpath('normalize-space(//span[@class="regular-price"])').get()
        except:
            pass

        try:
            im_urls = []
            big_imgs = response.xpath('//a[@class="cloud-zoom-gallery"]/@href').getall()
            if big_imgs and len(big_imgs) > 0:
                for big_img in big_imgs:
                    im_urls.append(big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//div[@class="box-collateral"])').get()
            item['description'] = desc
        except:
            pass

        return item