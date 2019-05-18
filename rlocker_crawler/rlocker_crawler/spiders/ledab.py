# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class LedabSpider(scrapy.Spider):
    name = 'ledab'
    allowed_domains = ['ledab.ca']
    start_urls = ['http://ledab.ca/']

    # def start_requests(self):
    #     uri = 'https://ledab.ca/gas-ptfe-tape/'
    #     yield Request(url=uri, callback=self.parse_details)

    def parse(self, response):
        links = response.xpath('//a[@class="navPage-subMenu-action navPages-action"]/@href').getall()
        for link in links:
            yield Request(url=link, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//h4[@class="card-title"]/a/@href').getall()
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

        # pagination-item pagination-item--next
        next_link = response.xpath('//li[@class="pagination-item pagination-item--next"]/a/@href')
        if next_link:
            next_url = next_link.get()
            yield Request(url=next_url, callback=self.parse_category)

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        try:
            item['item_id'] = response.xpath('//dd[@class="productView-info-value"]/text()').get().strip()
        except:
            pass

        try:
            title = response.xpath('//h1[@class="productView-title"]/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//a[@class="breadcrumb-label"]/text()').getall()
            for catalog in catalogs[:-1]:
                if 'Home' in catalog:
                    continue

                cats.append(catalog.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        try:
            item['price'] = response.xpath('normalize-space(//span[@class="price price--withoutTax"])').get()
        except:
            pass

        try:
            im_urls = []
            big_imgs = response.xpath('//li[@class="productView-images"]/figure/@data-image-gallery-zoom-image-url').getall()
            if big_imgs and len(big_imgs) > 0:
                for big_img in big_imgs:
                    im_urls.append(big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//div[@id="tab-description"]/p)').get()
            item['description'] = desc
        except:
            pass

        return item
