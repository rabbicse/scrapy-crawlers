# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class EddiswholesaleSpider(scrapy.Spider):
    name = 'eddiswholesale'
    __base_url = 'http://eddiswholesale.com'
    __img_base_uri = 'https://eddiswholesale-2.azureedge.net'
    allowed_domains = ['eddiswholesale.com']
    start_urls = ['http://eddiswholesale.com/']

    # def start_requests(self):
    #     uri = 'https://www.eddiswholesale.com/homebox-spring-clearance/hb-vista-triangle-plus-120x75x200cm-hbx-vista-trplus'
    #     yield Request(url=uri, callback=self.parse_details)

    def parse(self, response):
        links = response.xpath('//div[@class="span4"]/ul/li/a/@href').getall()
        for link in links:
            cat_url = self.__base_url + link
            yield Request(url=cat_url, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//a[@class="product-title"]/@href').getall()
            for product in products:
                product_url = self.__base_url + product
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

        try:
            item['item_id'] = response.xpath('//p[@class="product-details-code"]/text()').get().replace('Product Code:', '').strip()
        except:
            pass

        title = ''
        try:
            title = response.xpath('//title/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//ul[@class="breadcrumb"]/li/a')
            for catalog in catalogs:
                t = catalog.xpath('./@title').get()
                if 'Home' in t or 'Catalog' in t:
                    continue

                cats.append(t.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        # try:
        #     item['price'] = response.xpath('//span[@id="lblPriceRetailNoPriceValue"]/text()').get()
        # except:
        #     pass

        try:
            im_urls = []
            big_img = response.xpath('//img[@id="product-detail-gallery-main-img"]/@data-zoom-image').get()
            if big_img:
                im_urls.append(self.__img_base_uri + big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//div[@class="product-details-desc"])').get()
            desc = desc.replace(title, '').strip()
            item['description'] = desc
        except:
            pass

        # print(item)
        return item