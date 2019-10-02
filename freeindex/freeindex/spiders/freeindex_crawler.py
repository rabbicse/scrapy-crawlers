# -*- coding: utf-8 -*-
import json
import random
import re
import time

import requests
import scrapy
from scrapy import Request, Selector
from scrapy.log import logger

from freeindex import db_handler, settings
from freeindex.items import FreeindexItem
from freeindex.models import FreeIndex

'''
1) professionalgardening.com 
2) megawatthydro.com 
3)Biofloral.com 
4)hydrotekhydroponics.com 
5)mygreenplanet.com 
6)hawthornegc.ca 
7) eddiswholesale.com 
8) ledab.ca 
9) naturalinsectcontrol.com 
10) growlights.ca 
11) https://truenorthseedbank.com/ '''


class FreeindexCrawlerSpider(scrapy.Spider):
    # http://83.149.70.159:13010
    index = 50
    name = 'freeindex_crawler'
    rotate_user_agent = True
    allowed_domains = ['freeindex.co.uk']
    __sitemap = 'https://www.freeindex.co.uk/sitemap({}).htm'
    __sitemap_uri = 'https://www.freeindex.co.uk/sitemap.htm'
    start_urls = [
        "https://www.freeindex.co.uk/categories/entertainment_and_lifestyle/healthcare/complementary_therapy({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/arts_and_lifestyle/lifestyle_management/counselling({})/".format(index),
        "https://www.freeindex.co.uk/categories/arts_and_lifestyle/kids({})/".format(index),
        "https://www.freeindex.co.uk/categories/business_services/advertising/design_and_print({})/".format(index),
        "https://www.freeindex.co.uk/categories/arts_and_lifestyle/education({})/".format(index),
        "https://www.freeindex.co.uk/categories/industry/industrial_services({})/".format(index),
        "https://www.freeindex.co.uk/categories/entertainment_and_lifestyle/healthcare/nursing_and_care_services({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/entertainment_and_lifestyle/beauty/hair_and_beauty_salons({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/arts_and_lifestyle/beauty/hairdressers({})/".format(index),
        "https://www.freeindex.co.uk/categories/human_resources/recruitment_agency({})/".format(index),
        "https://www.freeindex.co.uk/categories/business_management/management_consulting({})/".format(index),
        "https://www.freeindex.co.uk/categories/entertainment_and_lifestyle/healthcare/massage_therapists({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/advertising_and_marketing/advertising_production_services({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/financial_and_legal/legal/lawyers({})/".format(index),
        "https://www.freeindex.co.uk/categories/financial_and_accounting/commercial_law({})/".format(index),
        "https://www.freeindex.co.uk/categories/business_management/small_office_home_office/secretarial_services({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/business_services/general_office_services/virtual_assistant({})/".format(
            index),
        "https://www.freeindex.co.uk/categories/computers_and_internet/web_services({})/".format(index),
    ]
    __base_url = 'https://www.freeindex.co.uk'
    __api_url = 'https://www.freeindex.co.uk/customscripts/ajax_view_tel.asp?id={}&wherefrom=PROFILE'
    TXT_OUTPUT = 'freeindex_urls.txt'

    # def start_requests(self):
    #     session = db_handler.Session()
    #     try:
    #         with open('url_updated.txt', 'r+') as f:
    #             # i = 0
    #             for details_url in f.readlines():
    #                 details_url = details_url.strip()
    #                 query = {'url': details_url}
    #                 q_data = session.query(FreeIndex).filter_by(**query).first()
    #                 if not q_data:
    #                     headers = {
    #                         'User-Agent': random.choice(settings.USER_AGENT_CHOICES),
    #                         'Upgrade-Insecure-Requests': '1',
    #                         'Connection': 'keep-alive',
    #                         'Host': 'www.freeindex.co.uk',
    #                         'Accept-Language': 'en-US,en;q=0.5',
    #                         'Accept-Encoding': 'gzip, deflate, br',
    #                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    #                     yield Request(url=details_url, callback=self.parse_details, headers=headers)
    #                 else:
    #                     logger.debug('URL: {} already exists!'.format(details_url))
    #     except Exception as x:
    #         logger.error('Error when parse: {}'.format(x))
    #     finally:
    #         session.close()

    def start_requests(self):
        session = db_handler.Session()
        try:
            for i in range(ord('a'), ord('z') + 1):
                uri = self.__sitemap.format(chr(i))
                yield Request(url=uri, callback=self.parse_category)
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))
        finally:
            session.close()

    def parse_category(self, response):
        try:
            urls = response.xpath('//a[@class="sitemap-menu-item"]/@href').getall()
            for url in urls:
                cat_url = self.__base_url + url
                yield Request(url=cat_url, callback=self.parse)
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))

    def parse(self, response):
        session = db_handler.Session()
        try:
            with open(self.TXT_OUTPUT, 'a+') as f:
                urls = response.xpath('//div[@class="listing_name"]/a/@href').getall()
                for url in urls:
                    details_url = self.__base_url + url

                    query = {'url': details_url}
                    q_data = session.query(FreeIndex).filter_by(**query).first()
                    if not q_data:
                        f.write(details_url + '\n')
                    else:
                        logger.debug('URL: {} already exists!'.format(details_url))
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))
        finally:
            session.close()

        next_link = response.xpath('//a[@class="boxlink"]/@href').getall()
        if next_link:
            headers = {
                'User-Agent': random.choice(settings.USER_AGENT_CHOICES),
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
                'Host': 'www.freeindex.co.uk',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
            yield Request(url=self.__base_url + next_link[-1], headers=headers, callback=self.parse)

    def parse_details(self, response):
        item = FreeindexItem()
        id = re.search(r'.*?\_(\d+)\.htm$', response.url).group(1)
        item['url'] = response.url
        item['categories'] = response.xpath('//div[@class="container breadcrumb"]/a/text()').getall()[-1]
        item['name'] = response.xpath('//meta[@property="og:title"]/@content').get()
        item['short_desc'] = response.xpath('//meta[@property="og:description"]/@content').get()
        com_div = response.xpath('//div[@class="psummary_company"]/div[@style="display:flow-root;"]//a')
        if com_div:
            # print(com_div[0])
            item['website'] = com_div[0].xpath('./@title').get()

            if len(com_div) > 1:
                socials = []
                for a in com_div[1:]:
                    try:
                        social_url = self.__base_url + a.xpath('./@href').get()
                        # socials.append(social_url)
                    # if not social_url:
                    #     continue
                    #
                    # try:
                    #     res = requests.head(self.__base_url + social_url, proxies={'https': response.meta['proxy']},
                    #                         timeout=20, allow_redirects=True)
                    #     if res:
                    #         socials.append(res.url)
                    except:
                        pass
                item['social_media_urls'] = ', '.join(socials)

        right_rows = response.xpath('//div[@class="psummary_verified"]/table/tr')
        for right_row in right_rows:
            tds = right_row.xpath('.//td')
            if not tds or len(tds) < 2:
                continue

            label = tds[0].xpath('./text()').get()

            try:
                if 'Member since' in label:
                    item['member_since'] = tds[1].xpath('./text()').get().strip()
            except:
                pass

            try:
                if 'Manually reviewed' in label:
                    item['manually_reviewed'] = tds[1].xpath('./text()').get().strip()
            except:
                pass

            try:
                if 'Last updated' in label:
                    item['last_updated'] = tds[1].xpath('./text()').get().strip()
            except:
                pass

        ks_item_tags = response.xpath('//h4[@class="DescItemTitle"]')
        for ks_item_tag in ks_item_tags:
            if 'Key Services' in ks_item_tag.xpath('./text()').get():
                key_services = ks_item_tag.xpath(
                    './../following-sibling::div//div[@class="DescItem"]/a/text()').getall()
                item['key_services'] = ', '.join(key_services)
                break

        long_desc_tag = response.xpath('//div[@class="contentbox boxwhite"]')
        if long_desc_tag:
            texts = long_desc_tag.xpath('./hr/following-sibling::text()').getall()
            more_texts = long_desc_tag.xpath('./hr/following-sibling::span/text()').getall()
            item['long_desc'] = ''.join([txt.strip('\n').strip() for txt in texts]) + ''.join(more_texts)

        try:
            scripts = response.xpath('//script/text()').getall()
            for script in scripts:
                if '{"@context":' in script:
                    json_data = json.loads(script)
                    # print(json_data)
                    if 'openingHoursSpecification' in json_data:
                        opening_hours = []
                        j_opening_hours = json_data['openingHoursSpecification']
                        for j_opening_hour in j_opening_hours:
                            opening_hours.append(
                                '{}: {} - {}'.format(j_opening_hour['dayOfWeek'], j_opening_hour['opens'],
                                                     j_opening_hour['closes']))

                        item['opening_hours'] = ', '.join(opening_hours)

                    if 'address' in json_data:
                        addresses = []
                        j_addr = json_data['address']
                        if 'streetAddress' in j_addr:
                            addresses.append(j_addr['streetAddress'])
                        if 'addressLocality' in j_addr:
                            addresses.append(j_addr['addressLocality'])
                        if 'addressRegion' in j_addr:
                            item['city'] = j_addr['addressRegion']
                        if 'postalCode' in j_addr:
                            item['post_code'] = j_addr['postalCode']
                        item['address'] = ' '.join(addresses)
        except:
            pass

        # headers = {'X-Requested-With': 'XMLHttpRequest',
        #            'Referer': response.url,
        #            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        # yield Request(url=self.__api_url.format(id), headers=headers, meta={'item': item}, callback=self.parse_phone)

        # try:
        #     res = requests.get(self.__api_url.format(id), headers=headers, proxies={'https': response.meta['proxy']},
        #                        timeout=20, allow_redirects=True)
        #     if res:
        #         sel = Selector(text=res.text)
        #         divs = sel.xpath('//div[@class="clearfix"]')
        #         for div in divs:
        #             text = div.xpath('string(./div)').get()
        #             if 'Tel:' in text:
        #                 tel = div.xpath('.//a/@href').get()
        #                 if tel:
        #                     item['telephone'] = tel.replace('tel:', '').strip()
        #
        #             if 'Mobile:' in text:
        #                 tel = div.xpath('.//a/@href').get()
        #                 if tel:
        #                     item['mobile'] = tel.replace('tel:', '').strip()
        # except:
        #     pass

        return item

    def parse_phone(self, response):
        item = FreeindexItem(**response.meta['item'])

        divs = response.xpath('//div[@class="clearfix"]')
        for div in divs:
            text = div.xpath('string(./div)').get()
            if 'Tel:' in text:
                tel = div.xpath('.//a/@href').get()
                if tel:
                    item['telephone'] = tel.replace('tel:', '').strip()

            if 'Mobile:' in text:
                tel = div.xpath('.//a/@href').get()
                if tel:
                    item['mobile'] = tel.replace('tel:', '').strip()

        return item


class FreeindexCrawlerUSpider(scrapy.Spider):
    # http://83.149.70.159:13010
    index = 50
    name = 'freeindex_crawleru'
    rotate_user_agent = True
    allowed_domains = ['freeindex.co.uk']
    __sitemap = 'https://www.freeindex.co.uk/sitemap({}).htm'
    __sitemap_uri = 'https://www.freeindex.co.uk/sitemap.htm'
    start_urls = [
        # "https://www.freeindex.co.uk/sitemap(business-services).htm",
        # "https://www.freeindex.co.uk/sitemap(legal).htm",
        # "https://www.freeindex.co.uk/sitemap(property).htm",
        # "https://www.freeindex.co.uk/sitemap(public-and-social-services).htm",
        'https://www.freeindex.co.uk/sitemap(computers-and-internet).htm',
        'https://www.freeindex.co.uk/sitemap(entertainment-and-media).htm',
        'https://www.freeindex.co.uk/sitemap(events-and-conferences).htm',
        'https://www.freeindex.co.uk/sitemap(finance).htm',
        'https://www.freeindex.co.uk/sitemap(food-and-drink).htm',
        'https://www.freeindex.co.uk/sitemap(health-and-beauty).htm',
        'https://www.freeindex.co.uk/sitemap(manufacturing-and-industry).htm',
        'https://www.freeindex.co.uk/sitemap(shopping).htm',
        'https://www.freeindex.co.uk/sitemap(tourism-and-accommodation).htm',
        'https://www.freeindex.co.uk/sitemap(tradesmen-and-construction).htm',
        'https://www.freeindex.co.uk/sitemap(transport-and-motoring).htm'
    ]
    __base_url = 'https://www.freeindex.co.uk'
    __api_url = 'https://www.freeindex.co.uk/customscripts/ajax_view_tel.asp?id={}&wherefrom=PROFILE'
    TXT_OUTPUT = 'freeindex_urls.txt'

    # def start_requests(self):
    #     session = db_handler.Session()
    #     try:
    #         with open('url_updated.txt', 'r+') as f:
    #             # i = 0
    #             for details_url in f.readlines():
    #                 details_url = details_url.strip()
    #                 query = {'url': details_url}
    #                 q_data = session.query(FreeIndex).filter_by(**query).first()
    #                 if not q_data:
    #                     headers = {
    #                         'User-Agent': random.choice(settings.USER_AGENT_CHOICES),
    #                         'Upgrade-Insecure-Requests': '1',
    #                         'Connection': 'keep-alive',
    #                         'Host': 'www.freeindex.co.uk',
    #                         'Accept-Language': 'en-US,en;q=0.5',
    #                         'Accept-Encoding': 'gzip, deflate, br',
    #                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    #                     yield Request(url=details_url, callback=self.parse_details, headers=headers)
    #                 else:
    #                     logger.debug('URL: {} already exists!'.format(details_url))
    #     except Exception as x:
    #         logger.error('Error when parse: {}'.format(x))
    #     finally:
    #         session.close()

    # def start_requests(self):
    #     session = db_handler.Session()
    #     try:
    #         for i in range(ord('a'), ord('z') + 1):
    #             uri = self.__sitemap.format(chr(i))
    #             yield Request(url=uri, callback=self.parse_category)
    #     except Exception as x:
    #         logger.error('Error when parse: {}'.format(x))
    #     finally:
    #         session.close()

    def start_requests(self):
        try:
            for start_url in self.start_urls:
                yield Request(url=start_url, callback=self.parse_category)
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))

    def parse_category(self, response):
        try:

            cats = response.xpath('//div[@class="container breadcrumb"]/a/text()').getall()
            urls = response.xpath('//a[@class="sitemap-menu-item"]')
            for url in urls:
                cat_url = self.__base_url + url.xpath('./@href').get()
                div = url.xpath('following-sibling::div')
                if not div:
                    continue

                cnt = div.xpath('./text()').get()
                if not cnt:
                    continue

                cnt = re.sub(r'[^0-9]', '', cnt).strip()
                if not re.match(r'^\d+$', cnt):
                    continue
                count = int(cnt)
                if count < 50:
                    continue

                yield Request(url=cat_url, meta={'top_category': cats[-1]}, callback=self.parse)
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))

    def parse(self, response):
        session = db_handler.Session()
        try:
            urls = response.xpath('//div[@class="listing_name"]/a/@href').getall()
            for url in urls[:11]:
                details_url = self.__base_url + url

                query = {'url': details_url}
                q_data = session.query(FreeIndex).filter_by(**query).first()
                if not q_data:
                    yield Request(url=details_url, meta={'top_category': response.meta['top_category']},
                                  callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(details_url))
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))
        finally:
            session.close()

        # session = db_handler.Session()
        # try:
        #     with open(self.TXT_OUTPUT, 'a+') as f:
        #         urls = response.xpath('//div[@class="listing_name"]/a/@href').getall()
        #         for url in urls:
        #             details_url = self.__base_url + url
        #
        #             query = {'url': details_url}
        #             q_data = session.query(FreeIndex).filter_by(**query).first()
        #             if not q_data:
        #                 f.write(details_url + '\n')
        #             else:
        #                 logger.debug('URL: {} already exists!'.format(details_url))
        # except Exception as x:
        #     logger.error('Error when parse: {}'.format(x))
        # finally:
        #     session.close()

        # next_link = response.xpath('//a[@class="boxlink"]/@href').getall()
        # if next_link:
        #     headers = {
        #         'User-Agent': random.choice(settings.USER_AGENT_CHOICES),
        #         'Upgrade-Insecure-Requests': '1',
        #         'Connection': 'keep-alive',
        #         'Host': 'www.freeindex.co.uk',
        #         'Accept-Language': 'en-US,en;q=0.5',
        #         'Accept-Encoding': 'gzip, deflate, br',
        #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        #     yield Request(url=self.__base_url + next_link[-1], headers=headers, callback=self.parse)

    def parse_details(self, response):
        item = FreeindexItem()
        id = re.search(r'.*?\_(\d+)\.htm$', response.url).group(1)
        item['top_category'] = response.meta['top_category']
        item['url'] = response.url
        item['categories'] = response.xpath('//div[@class="container breadcrumb"]/a/text()').getall()[-1]
        item['name'] = response.xpath('//meta[@property="og:title"]/@content').get()
        item['short_desc'] = response.xpath('//meta[@property="og:description"]/@content').get()
        com_div = response.xpath('//div[@class="psummary_company"]/div[@style="display:flow-root;"]//a')
        if com_div:
            # print(com_div[0])
            item['website'] = com_div[0].xpath('./@title').get()

            # if len(com_div) > 1:
            #     socials = []
            #     for a in com_div[1:]:
            #         try:
            #             social_url = self.__base_url + a.xpath('./@href').get()
            #             # socials.append(social_url)
            #             if not social_url:
            #                 continue
            #
            #             # try:
            #             logger.info('Proxy: {}'.format(response.meta['proxy']))
            #             logger.info('Social URL: {}'.format(social_url))
            #             res = requests.head(self.__base_url + social_url, proxies={'http': response.meta['proxy']},
            #                                 timeout=20, allow_redirects=True)
            #             if res:
            #                 socials.append(res.url)
            #         except Exception as ex:
            #             logger.error('Error when get social urls. Error details: {}'.format(ex))
            #     item['social_media_urls'] = ', '.join(socials)

        right_rows = response.xpath('//div[@class="psummary_verified"]/table/tr')
        for right_row in right_rows:
            tds = right_row.xpath('.//td')
            if not tds or len(tds) < 2:
                continue

            label = tds[0].xpath('./text()').get()

            try:
                if 'Member since' in label:
                    item['member_since'] = tds[1].xpath('./text()').get().strip()
            except:
                pass

            try:
                if 'Manually reviewed' in label:
                    item['manually_reviewed'] = tds[1].xpath('./text()').get().strip()
            except:
                pass

            try:
                if 'Last updated' in label:
                    item['last_updated'] = tds[1].xpath('./text()').get().strip()
            except:
                pass

        ks_item_tags = response.xpath('//h4[@class="DescItemTitle"]')
        for ks_item_tag in ks_item_tags:
            if 'Key Services' in ks_item_tag.xpath('./text()').get():
                key_services = ks_item_tag.xpath(
                    './../following-sibling::div//div[@class="DescItem"]/a/text()').getall()
                item['key_services'] = ', '.join(key_services)
                break

        long_desc_tag = response.xpath('//div[@class="contentbox boxwhite"]')
        if long_desc_tag:
            texts = long_desc_tag.xpath('./hr/following-sibling::text()').getall()
            more_texts = long_desc_tag.xpath('./hr/following-sibling::span/text()').getall()
            item['long_desc'] = ''.join([txt.strip('\n').strip() for txt in texts]) + ''.join(more_texts)

        try:
            scripts = response.xpath('//script/text()').getall()
            for script in scripts:
                if '{"@context":' in script:
                    json_data = json.loads(script)
                    # print(json_data)
                    if 'openingHoursSpecification' in json_data:
                        opening_hours = []
                        j_opening_hours = json_data['openingHoursSpecification']
                        for j_opening_hour in j_opening_hours:
                            opening_hours.append(
                                '{}: {} - {}'.format(j_opening_hour['dayOfWeek'], j_opening_hour['opens'],
                                                     j_opening_hour['closes']))

                        item['opening_hours'] = ', '.join(opening_hours)

                    if 'address' in json_data:
                        addresses = []
                        j_addr = json_data['address']
                        if 'streetAddress' in j_addr:
                            addresses.append(j_addr['streetAddress'])
                        if 'addressLocality' in j_addr:
                            addresses.append(j_addr['addressLocality'])
                        if 'addressRegion' in j_addr:
                            item['city'] = j_addr['addressRegion']
                        if 'postalCode' in j_addr:
                            item['post_code'] = j_addr['postalCode']
                        item['address'] = ' '.join(addresses)
        except:
            pass

        headers = {'X-Requested-With': 'XMLHttpRequest',
                   'Referer': response.url,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        # yield Request(url=self.__api_url.format(id), headers=headers, meta={'item': item}, callback=self.parse_phone)

        # try:
        #     res = requests.get(self.__api_url.format(id), headers=headers, proxies={'https': response.meta['proxy']},
        #                        timeout=20, allow_redirects=True)
        #     if res:
        #         sel = Selector(text=res.text)
        #         divs = sel.xpath('//div[@class="clearfix"]')
        #         for div in divs:
        #             text = div.xpath('string(./div)').get()
        #             if 'Tel:' in text:
        #                 tel = div.xpath('.//a/@href').get()
        #                 if tel:
        #                     item['telephone'] = tel.replace('tel:', '').strip()
        #
        #             if 'Mobile:' in text:
        #                 tel = div.xpath('.//a/@href').get()
        #                 if tel:
        #                     item['mobile'] = tel.replace('tel:', '').strip()
        # except:
        #     pass

        return item

    def parse_phone(self, response):
        item = FreeindexItem(**response.meta['item'])

        divs = response.xpath('//div[@class="clearfix"]')
        for div in divs:
            text = div.xpath('string(./div)').get()
            if 'Tel:' in text:
                tel = div.xpath('.//a/@href').get()
                if tel:
                    item['telephone'] = tel.replace('tel:', '').strip()

            if 'Mobile:' in text:
                tel = div.xpath('.//a/@href').get()
                if tel:
                    item['mobile'] = tel.replace('tel:', '').strip()

        return item
