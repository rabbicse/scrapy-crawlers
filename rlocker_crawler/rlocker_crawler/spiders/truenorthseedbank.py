# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class TruenorthseedbankSpider(scrapy.Spider):
    name = 'truenorthseedbank'
    allowed_domains = ['truenorthseedbank.com']
    start_urls = ['http://truenorthseedbank.com/']
    __start_page = 'https://truenorthseedbank.com/cannabis-seeds?limit=48&p={}'

    def start_requests(self):
        # uri = 'https://truenorthseedbank.com/strawberry-jam-autoflowering-regular-seeds-flash-seeds'
        # yield Request(url=uri, callback=self.parse_details)
        for i in range(1, 67):
            url = self.__start_page.format(i)
            yield Request(url=url, callback=self.parse)
            # break

    def parse(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//h3[@class="title"]/a/@href').getall()
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

        try:
            item['item_id'] = response.xpath('//span[@class="sku"]/text()').get().strip()
        except:
            pass

        try:
            title = response.xpath('//div[@class="box-content product_name"]/h1/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//div[@class="breadcrumbs"]/ul/li/a/text()').getall()
            for catalog in catalogs[1:]:
                cats.append(catalog.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        try:
            prices = []
            price = response.xpath(
                '//div[@class="box-content product_name"]/div[@class="price-box"]/span[@class="regular-price"]/span[@class="price"]/text()').get()
            if price:
                prices.append(price)

            pcs = response.xpath(
                '//td[@class="a-right"]/div[@class="price-box"]/span[@class="regular-price"]/span[@class="price"]/text()').getall()
            if pcs and len(pcs) > 0:
                for pc in pcs:
                    prices.append(pc)
            item['price'] = ', '.join(prices)
        except:
            pass

        try:
            im_urls = []
            big_imgs = response.xpath('//img[@id="mainImageJs"]/@src').getall()
            if big_imgs and len(big_imgs) > 0:
                for big_img in big_imgs:
                    im_urls.append(big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath(
                'normalize-space(//div[@class="box-collateral box-description"]/div[@class="std"])').get()
            item['description'] = desc
        except:
            pass

        # print(item)
        return item
