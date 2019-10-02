# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class BiofloralSpider(scrapy.Spider):
    name = 'biofloral'
    __base_url = 'http://www.biofloral.com'
    allowed_domains = ['biofloral.com']
    start_urls = ['http://www.biofloral.com/categories.aspx?ac=true']

    # def start_requests(self):
    #     uri = 'http://www.biofloral.com/ecom/productpage/3cb1906e-70fc-4f3f-9434-694491897d9b?category=c1093178-c1c4-4560-a67c-fc92fc5b4562'
    #     yield Request(url=uri, callback=self.parse_details)

    def parse(self, response):
        cat_urls = response.xpath('//a[@class="biofloral-categorie"]/@href').getall()
        for cat_url in cat_urls:
            url = self.__base_url + cat_url

            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            prod_urls = response.xpath('//a[@class="product-title"]/@href').getall()
            for prod_url in prod_urls:
                product_url = self.__base_url + prod_url #+ '&lang=en-US'
                query = {'url': product_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=product_url, meta={'uri': product_url}, callback=self.parse_details_default)
                else:
                    logger.debug('URL: {} already exists!'.format(product_url))
        except:
            pass

        finally:
            session.close()


        cat_urls = response.xpath('//a[@class="category-link"]/@href').getall()
        for cat_url in cat_urls:
            url = self.__base_url + cat_url
            yield Request(url=url, callback=self.parse_category)

        # next_link = response.xpath('//a[@id="cmdViewMore"]/@href')
        # if next_link:
        #     next_url = self.__base_url + next_link.get()
        #     yield Request(url=next_url, callback=self.parse_category)


    def parse_details_default(self, response):
        try:
            d_link = response.xpath('//a[@title="en"]/@href').get()
            yield Request(url=self.__base_url + d_link, meta={'uri': response.meta['uri']}, callback=self.parse_details)

        except:
            pass

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.meta['uri']

        try:
            # Product Code:
            item_id = response.xpath('//p[@class="product-details-code"]/text()').get()
            item_id = re.sub(r'[^\d]', '', item_id)
            item['item_id'] = item_id
        except:
            pass

        title = ''
        try:
            title_tags = response.xpath('normalize-space(//ul[@class="breadcrumb"]//li[@class="active"])').getall()
            item['title'] = title_tags[-1]
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//ul[@class="breadcrumb"]//li/a/@title').getall()
            for catalog in catalogs[2:]:
                cats.append(catalog)
            item['category'] = ' '.join(cats)
        except:
            pass

        try:
             price = response.xpath('normalize-space(//div[@class="unstyled single-price-display"])').get()
             price = re.sub(r'[^\d$.\,]', '', price)
             item['price'] = price
        except:
            pass

        try:
            im_urls = []
            big_img = response.xpath('//img[@id="product-detail-gallery-main-img"]/@data-zoom-image').get()
            if big_img:
                im_urls.append(self.__base_url + big_img)
            image_urls = response.xpath(
                '//img[contains(@id, "oucProductPictureViewer_rptProductPictureThumbnails_ctl")]')
            for im_url in image_urls:
                u = im_url.xpath('./@onmouseover').get()
                u = u.split(',')[1].strip('\'')
                i_url = self.__base_url + u
                if i_url not in im_urls:
                    im_urls.append(i_url)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//span[@id="lblProductDescription"])').get()
            desc = desc.replace(title, '').strip()
            item['description'] = desc
        except:
            pass

        return item
