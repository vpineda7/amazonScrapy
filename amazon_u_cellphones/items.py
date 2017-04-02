# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AmazonUCellphonesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    #amazon product identifier
    asin = scrapy.Field()
    
    #product brand
    brand = scrapy.Field()
    
    #product amazon price
    priceAmz = scrapy.Field()
    
    #product other stores (amazon partners) price
    priceOthers = scrapy.Field()
    
    #product number of reviews
    reviewCount = scrapy.Field()
    
    #product review stars mean
    starMean = scrapy.Field()
    
    #product 1-star reviews percentage
    star1 = scrapy.Field()
    
    #product 2-star reviews percentage
    star2 = scrapy.Field()
    
    #product 3-star reviews percentage
    star3 = scrapy.Field()
    
    #product 4-star reviews percentage
    star4 = scrapy.Field()
    
    #product 5-star reviews percentage
    star5 = scrapy.Field()
    
    pass
