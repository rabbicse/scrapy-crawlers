# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class MegawatSpider(scrapy.Spider):
    name = 'megawat'
    __base_url = 'https://www.megawatthydro.com'
    allowed_domains = ['megawatthydro.com']
    start_urls = ['https://www.megawatthydro.com/ProductCatalog.aspx?lang=en-US']

    # def start_requests(self):
    #     uri = 'https://www.megawatthydro.com/en/lighting-electrical/components/capacitor-hps-1000w-62064'
    #     yield Request(url=uri, callback=self.parse_details)
    #     # uri = 'https://www.megawatthydro.com/en/lighting-electrical'
    #     # yield Request(url=uri, callback=self.parse_catalog)

    def parse(self, response):
        links = response.xpath('//a[@class="categoryLink"]/@href').getall()
        for link in links:
            yield Request(url=link, callback=self.parse_catalog)

    def parse_catalog(self, response):
        try:
            session = db_handler.Session()
            product_urls = response.xpath('//a[@class="productListTitleLink"]/@href').getall()
            for details_url in product_urls:
                query = {'url': details_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=details_url, callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(details_url))
        except:
            pass
        finally:
            session.close()

        next_link = response.xpath('//a[@id="repProduct:linkNextBottom"]/@href')
        if next_link:
            print(next_link)
            next_url = next_link.get()
            yield Request(url=next_url, callback=self.parse_catalog)

        links = response.xpath('//a[@class="categoryLink"]/@href').getall()
        for link in links:
            yield Request(url=link, callback=self.parse_catalog)

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        try:
            item['item_id'] = response.xpath('//span[@id="lblCodeValue"]/text()').get()
        except:
            pass

        title = ''
        try:
            title = response.xpath('//span[@id="lblTitle"]/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//a[@class="contentNavigationLink"]')
            for catalog in catalogs:
                t = catalog.xpath('./@title').get()
                if 'Home' in t or 'Catalog' in t:
                    continue

                cats.append(t.strip())
            item['category'] = ' '.join(cats)
        except:
            pass

        try:
            item['price'] = response.xpath('//span[@id="lblPriceRetailNoPriceValue"]/text()').get()
        except:
            pass

        try:
            im_urls = []
            big_img = response.xpath('//img[@class="bigImageSettings"]/@src').get()
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
