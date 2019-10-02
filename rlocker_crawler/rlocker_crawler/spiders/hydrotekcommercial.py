# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class HydrotekcommercialSpider(scrapy.Spider):
    name = 'hydrotekcommercial'
    __username = 'greenleafhydroponicscanada@gmail.com'
    __password = 'Familyfirst1.'
    __base_url = 'https://www.hydrotekcommercial.com'
    allowed_domains = ['hydrotekcommercial.com']
    start_urls = ['https://www.hydrotekcommercial.com/']

    # def start_requests(self):
    #     uri = 'https://www.hydrotekcommercial.com/hydroponic-lamps/hortilux-blue-mh-1000w-mt1000b-d-hor-htl-blue-102207'
    #     yield Request(url=uri, callback=self.parse_details)
    #     # uri = 'https://www.megawatthydro.com/en/lighting-electrical'
    #     # yield Request(url=uri, callback=self.parse_catalog)

    def parse(self, response):
        links = response.xpath('//a[@class="category-link"]/@href').getall()
        for link in links:
            url = self.__base_url + link
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            prod_urls = response.xpath('//a[@class="product-title"]/@href').getall()
            for prod_url in prod_urls:
                product_url = self.__base_url + prod_url
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


        next_link = response.xpath('//a[@id="cmdViewMore"]/@href')
        if next_link:
            next_url = self.__base_url + next_link.get()
            yield Request(url=next_url, callback=self.parse_category)

        cat_urls = response.xpath('//a[@class="category-link"]/@href').getall()
        for cat_url in cat_urls:
            url = self.__base_url + cat_url
            yield Request(url=url, callback=self.parse_category)

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        try:
            item['item_id'] = response.xpath('normalize-space(//p[@class="product-details-code"])').get().replace('Product Code:', '').strip()
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
            catalogs = response.xpath('//ul[@class="breadcrumb"]/li/a/@title').getall()
            for catalog in catalogs:
                if 'Home' in catalog:
                    continue

                cats.append(catalog.strip())
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
            desc = response.xpath('normalize-space(//div[@class="product-details-desc"])').get()
            desc = desc.replace(title, '').strip()
            item['description'] = desc
        except:
            pass

        # print(item)
        return item