# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
from scrapy.log import logger
import urllib.parse

from whed_crawler.items import WhedCrawlerItem
from whed_crawler import db_handler
from whed_crawler.models import Model


class WhedSpider(scrapy.Spider):
    name = 'whed'
    allowed_domains = ['whed.net']
    start_urls = ['http://whed.net/']
    start_page = 'https://www.whed.net/results_institutions.php'
    base_uri = 'https://www.whed.net'

    # country_list = ['China - Hong Kong SAR']
    country_list = ['Brazil', 'Argentina', 'Canada', 'China', 'China - Hong Kong SAR', 'China - Macao SAR', 'China - Taiwan',
                    'France', 'Germany', 'Italy', 'Japan', 'Korea (Democratic People\'s Republic of)', 'Mexico', 'Poland',
                    'Russian Federation', 'Spain', 'United Kingdom', 'United States of America']

    def start_requests(self):
        for country in self.country_list:
            post_data = {'Chp1': country,
                         'afftri': 'yes',
                         'stat': 'Country',
                         'sort': 'IAUMember DESC,Country,InstNameEnglish,iBranchName',
                         'nbr_ref_pge': '10000'}

            yield FormRequest(url=self.start_page, formdata=post_data, dont_filter=True,
                              callback=self.parse)

        # yield Request(url='https://www.whed.net/detail_institution.php?Jzo2MF0tMyxVLDBgYApgCg==',
        #               callback=self.parse_details)
        # meta = {'page': 0}
        # yield FormRequest(url=self.start_page, meta=meta, formdata={'Chp1': 'Brazil', 'Chp0': '', 'Chp10': '', 'membre': '0'},
        #                   callback=self.parse)

    def parse(self, response):
        session = None
        try:
            session = db_handler.Session()
            li_list = response.xpath('//ul[@id="results"]/li')
            logger.info('Total links: {}'.format(len(li_list)))
            for li in li_list:
                a = li.xpath('.//a[@class="fancybox fancybox.iframe"]/@href')
                href = a.extract_first()
                link = urllib.parse.urljoin(self.base_uri, href)

                query = {'url': link}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=link, callback=self.parse_details)
                else:
                    logger.info('URL: {} already exists!'.format(link))
                yield Request(url=link,
                              callback=self.parse_details)
        except Exception as x:
            logger.error(x)
        finally:
            if session:
                session.close()

        # print('Total: {}'.format(len(li_list)))
        # # print(response.body)
        #
        # meta = response.meta
        # print(meta)
        # page = meta['page']

        # post_data = {#'where': """"(Country LIKE '{}')""".format('Brazil'),
        #              #'requete': """"(Country={})""".format('Brazil'),
        #              # total: 1039
        #              # ret: home.php
        #              # quick: 0
        #              # 'membre': '0',
        #              # 'Chp0': '',
        #              'Chp1': 'Brazil',
        #              # 'debut': '100',
        #              # 'use': '',
        #              'afftri': 'yes',
        #              'stat': 'Country',
        #              'sort': 'IAUMember DESC,Country,InstNameEnglish,iBranchName',
        #              'nbr_ref_pge': str(page + 10000)}
        #
        # if page == 0:
        #     yield FormRequest(url=self.start_page, meta={'page': page + 10}, formdata=post_data, dont_filter=True,
        #                       callback=self.parse)

    def parse_details(self, response):
        item = WhedCrawlerItem()
        item['url'] = response.url
        item['name'] = response.xpath('//section[@role="main"]/h2/text()').extract_first().strip()
        item['header'] = response.xpath('string(//p[@class="tools fleft"]/span)').extract_first().strip()

        dl_list = response.xpath('//div[@class="main"]//div[@class="dl"]')
        for dl in dl_list:
            dt = dl.xpath('./span[@class="dt"]')
            dt_text = dt.xpath('./text()').extract_first().strip()
            if 'Address' in dt_text:
                dd = dt.xpath('./following-sibling::div[@class="dd"]')
                if dd:
                    labels = dd.xpath('.//span[@class="libelle"]')
                    for label in labels:
                        lbl = label.xpath('./text()').extract_first()
                        txt = label.xpath('string(./following-sibling::span[@class="contenu"])').extract_first()

                        if 'Street:' in lbl:
                            item['street'] = txt.strip()
                        if 'City:' in lbl:
                            item['city'] = txt.strip()
                        if 'Post Code:' in lbl:
                            item['post_code'] = txt.strip()
                        if 'Tel.:' in lbl:
                            item['tel'] = txt.strip()
                        if 'Fax:' in lbl:
                            item['fax'] = txt.strip()
                        if 'WWW:' in lbl:
                            item['web'] = txt.strip()

            if 'Institution Funding' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['ins_funding'] = dd_text

            if 'History' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['history'] = dd_text

            if 'Academic Year' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['academic_year'] = dd_text

            if 'Admission Requirements' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['admission_requirements'] = dd_text

            if 'Language(s)' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['language'] = dd_text

            if 'Student Body' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['student_body'] = dd_text

            if 'Student Services' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['student_services'] = dd_text

            if 'Staff'.lower() == dt_text.lower():
                dd_list = dt.xpath('./following-sibling::div[@class="dd"]')
                for dd in dd_list:
                    if dd:
                        labels = dd.xpath('.//span[@class="libelle"]')
                        for label in labels:
                            lbl = label.xpath('./text()').extract_first()
                            txt = label.xpath('string(./following-sibling::span[@class="contenu"])').extract_first().strip()

                            if 'Statistics Year:' in lbl:
                                item['staff_sta_year'] = txt

                            if 'Full Time Total:' in lbl:
                                item['staff_full_time_total'] = txt

            if 'Staff with Doctorate' in dt_text:
                dd_text = dt.xpath('normalize-space(./following-sibling::div[@class="dd"])').extract_first().strip()
                item['staff_with_doctorate'] = dd_text

            if 'Students' in dt_text:
                dd_list = dt.xpath('./following-sibling::div[@class="dd"]')
                for dd in dd_list:
                    if dd:
                        labels = dd.xpath('.//span[@class="libelle"]')
                        for label in labels:
                            lbl = label.xpath('./text()').extract_first()
                            txt = label.xpath('string(./following-sibling::span[@class="contenu"])').extract_first().strip()

                            if 'Statistics Year:' in lbl:
                                item['stu_sta_year'] = txt

                            if 'Total:' in lbl:
                                item['stu_total'] = txt

            if dt_text.strip() == '':
                dd_list = dt.xpath('./following-sibling::div[@class="dd"]')
                for dd in dd_list:
                    p_list = dd.xpath('./p[@class="principal"]')
                    if p_list and len(p_list) > 0:
                        i = 0
                        for p in p_list:
                            if i >= 2:
                                break

                            p_text = p.xpath('./text()').extract_first()
                            if 'Head :' in p_text:
                                i += 1
                                item['head'] = p.xpath('./text()').extract_first().replace('Head :', '').strip()
                                p_jt = p.xpath('./following-sibling::p')
                                if p_jt:
                                    lbl = p_jt.xpath('string(./span[@class="libelle"])').extract_first()
                                    if 'Job title:' in lbl:
                                        item['head_job_title'] = p_jt.xpath(
                                            'string(./span[@class="contenu"])').extract_first()

                            if 'Senior Administrative Officer :' in p_text:
                                item['senior_admin_officer'] = p.xpath('./text()').extract_first().replace(
                                    'Senior Administrative Officer :', '').strip()
                                i += 1
                                p_jt = p.xpath('./following-sibling::p')
                                if p_jt:
                                    lbl = p_jt.xpath('string(./span[@class="libelle"])').extract_first()
                                    if 'Job title:' in lbl:
                                        item['senior_admin_officer_jt'] = p_jt.xpath(
                                            'string(./span[@class="contenu"])').extract_first().strip()

        return item
