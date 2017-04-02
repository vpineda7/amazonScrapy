# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from datetime import datetime

class AmazonUCellphonesPipeline(object):
    def __init__(self):
        #connect to database
        self.connection = psycopg2.connect(host='localhost', database='teste', user='ubuntu', password='123456')
        
        #set cursor
        self.cursor = self.connection.cursor()
    
    def process_item(self, item, spider):
        
        '''
        Table creating command:
            CREATE TABLE phoneData (id serial PRIMARY KEY, asin varchar, brand varchar, priceAmz float, priceOthers float, reviewCount integer, starMean float, star1 integer, star2 integer, star3 integer, star4 integer, star5 integer, createdAt varchar);
        '''
        
        #add item to table
        self.cursor.execute("INSERT INTO phoneData ( asin, brand, priceAmz, priceOthers, reviewCount, starMean, star1, star2, star3, star4, star5, createdAt ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", [
                item['asin'],
                item['brand'],
                item['priceAmz'],
                item['priceOthers'],
                item['reviewCount'],
                item['starMean'],
                item['star1'],
                item['star2'],
                item['star3'],
                item['star4'],
                item['star5'],
                str(datetime.now())])
        
        #commit changes
        self.connection.commit()
        
        return item
