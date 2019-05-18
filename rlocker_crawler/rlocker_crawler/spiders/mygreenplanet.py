# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class MygreenplanetSpider(scrapy.Spider):
    name = 'mygreenplanet'
    allowed_domains = ['mygreenplanet.com']
    start_urls = ['http://mygreenplanet.com/']
    __start_page = 'https://mygreenplanet.com/shop/page/{}/'

    def start_requests(self):
        # uri = 'https://mygreenplanet.com/product/autopot-2pot-system/'
        # yield Request(url=uri, callback=self.parse_details)
        for i in range(1, 37):
            url = self.__start_page.format(i)
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link"]/@href').getall()
            for product in products:
                product_url = product
                print(product_url)
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
            item['item_id'] = response.xpath('//span[@class="sku"]/text()').get().strip()
        except:
            pass

        try:
            title = response.xpath('//h1[@class="product_title entry-title"]/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//a[@rel="tag"]/text()').getall()
            for catalog in catalogs:
                cats.append(catalog.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        try:
            item['price'] = response.xpath('normalize-space(//span[@class="electro-price"])').get()
        except:
            pass

        try:
            im_urls = []
            big_imgs = response.xpath('//img[@class="wp-post-image"]/@data-large_image').getall()
            if big_imgs and len(big_imgs) > 0:
                for big_img in big_imgs:
                    im_urls.append(big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//div[@class="electro-description"]/p)').get()
            item['description'] = desc
        except:
            pass

        return item
