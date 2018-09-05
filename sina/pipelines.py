# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class SinaPipeline(object):
    def open_spider(self, spider):
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = client.news
        self.news = db.news

    def process_item(self, item, spider):
        print(item)
        self.news.insert(dict(item))
        return item
