# -*- coding: utf-8 -*-
import re
import time

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from sina.items import SinaItem


class NewsSpider(CrawlSpider):
    name = 'news'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://news.sina.com.cn']
    # http://finance.sina.com.cn/review/hgds/2017-08-25/doc-ifykkfas7684775.shtml
    # http://news.sina.com.cn/o/2018-09-05/doc-ihiixyeu3326017.shtml
    # http://news.sina.com.cn/s/2018-09-05/doc-ihiixzkm4557161.shtml
    today_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    url_pattern = r'(http://(?:\w+\.)*news\.sina\.com\.cn)/.*/({})/doc-(.*)\.shtml'.format(today_date)

    rules = [
        Rule(LinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):

        if response.xpath("//h1/text()"):
            title = response.xpath("//h1/text()").extract_first()
            pattern = re.match(self.url_pattern, str(response.url))
            source = 'sina'
            date = pattern.group(2).replace('-', '/')

            time_ = response.xpath('//div[@class="date-source"]/span/text()').extract_first() or 'unknown'

            newsId = pattern.group(3)
            url = response.url
            contents = response.css('.article p').extract()
            comment_elements = response.xpath("//meta[@name='sudameta']/@content").extract_first()
            comment_channel = comment_elements.split(';')[0].split(':')[1] if comment_elements else ""
            comment_id = comment_elements.split(';')[1].split(':')[1] if comment_elements else ""

            comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={}&newsid={}'.format(
                comment_channel, comment_id)

            yield scrapy.Request(comment_url, self.parse_comment, meta={'source': source,
                                                                        'date': date,
                                                                        'newsId': newsId,
                                                                        'url': url,
                                                                        'title': title,
                                                                        'contents': contents,
                                                                        'time': time_
                                                                        })

    def parse_comment(self, response):
        if re.findall(r'"total": (\d*)\,', response.text):
            comments = re.findall(r'"total": (\d*)\,', response.text)[0]
        else:
            comments = 0
        item = SinaItem()
        item['comments'] = comments
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = response.meta['contents']
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        yield item
