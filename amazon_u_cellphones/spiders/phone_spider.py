import scrapy
import urllib
import logging
from scrapy.utils.log import configure_logging

from amazon_u_cellphones.items import *

class PhoneSpider(scrapy.Spider):
    #setup spider name and domain
    name = "phones"
    allowed_domains = [ "amazon.com" ]
    
    #configure logging to scrape.log
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='scrape.log',
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )
    
    #url info
    base_url = "https://www.amazon.com/unlocked-cell-phones/s?"
    querystring = {
        'ie': 'UTF8',
        'page': 1,
        'rh': 'n%3A2407749011%2Ck%3Aunlocked%20cell%20phones'
    }
    
    #start from this url
    #urlencode encodes '%' from querystring['rh'] as %25, so i had to do this little workaround to get it back
    start_urls = [ base_url + urllib.parse.urlencode(querystring).replace('%25', '%') ]
    
    #don't scrape products where titles contains these keywords
    blacklist = {'watch', 'case', 'pendant', 'adapter', 'headset', 'tracker'}


    #default parser, parses phone list page
    def parse(self, response):
        
        #list of result selectors
        resultList = response.xpath('//li[contains(@id, "result_")]')
        
        for result in resultList:
            
            #if list contains price, return it as a float. if not, return None
            def findPriceInList(l):
                if(l):
                    #price as the list's last item is a common pattern
                    if (l[-1][0] == '$'):
                        #remove '$' and ',' and return it as a float 
                        return float(l[-1][1:].replace(',', ''))
                    else:
                        return None
                else:
                    return None
            
            #product title
            title = result.xpath('.//h2[contains(@class, "s-access-title")]/text()').extract_first().lower()
            
            #if title doesn't contain any keyword from blacklist, proceed
            if(not(any(x in title for x in iter(self.blacklist)))):
                
                #create item
                item = AmazonUCellphonesItem()
                
                #get asin
                asin = result.xpath('@data-asin').extract_first()
                #as design choice: if not found, use None (which will be converted to NULL in postgres)
                item['asin'] = asin
                
                #get brand
                brand = result.xpath('.//span/text()[contains(., "by")]/../following-sibling::*[1]/text()').extract_first()
                if(brand):
                    #make it lowercase for database-consistence
                    brand = brand.lower()
                #as design choice: if not found, use None (which will be converted to NULL in postgres)
                item['brand'] = brand
                
                #get priceOthers
                priceOthers = result.xpath('.//span[contains(@class, "a-size-base a-color-base")]/text()').extract()
                priceOthers = findPriceInList(priceOthers)
                #as design choice: if not found, use None (which will be converted to NULL in postgres)
                item['priceOthers'] = priceOthers
                
                #get priceAmz
                priceAmz = result.xpath('.//span[contains(@class, "sx-price sx-price-large")]/parent::*/@aria-label').extract()
                priceAmz = findPriceInList(priceAmz)
                #as design choice: if not found, use None (which will be converted to NULL in postgres)
                item['priceAmz'] = priceAmz
                
                #get reviewCount
                reviewCount = result.xpath('.//span[@name="'+asin+'"]/following-sibling::*[1]/text()').extract_first()
                if(reviewCount):
                    #remove commas from number
                    reviewCount = int(reviewCount.replace(',', ''))
                    item['reviewCount'] = reviewCount
                else:
                    #as design choice: if not found, use 0
                    item['reviewCount'] = 0
                
                
                starMean = result.xpath('.//span/text()[contains(., "out of 5 stars")]').extract_first()
                if(starMean):
                    #get string content except ' out of 5 stars' (which contains 15 characters) and convert it to float
                    starMean = float(starMean[:-15])
                    item['starMean'] = starMean
                    
                    #get phone product page url
                    phoneUrl = result.xpath('.//a[contains(@class, s-access-detail-page)]/@href').extract_first()
                    
                    #create request
                    request = scrapy.Request(phoneUrl, callback=self.parsePhone, errback=self.errback)
                    
                    #pass item as argument to parsePhone()
                    request.meta['item'] = item
                    
                    #make request and yield the return from parsePhone() (which will be the item)
                    yield request
                else:
                    #as design choice: if not found, use None (which will be converted to NULL in postgres)
                    item['starMean'] = None
                    item['star1'] = None
                    item['star2'] = None
                    item['star3'] = None
                    item['star4'] = None
                    item['star5'] = None
                    #as a request to the phone page will not be made, yield item
                    yield item
                    
        #if there is a next page, parse next page
        if(response.xpath('//a[@id="pagnNextLink"]')):
            self.querystring['page'] += 1
            yield scrapy.Request(url=self.base_url + urllib.parse.urlencode(self.querystring).replace('%25', '%'), callback=self.parse, errback=self.errback)
        
        return
    
    
    #secondary parser, parses phone product page
    def parsePhone(self, response):
        #get item passed from parse()
        item = response.meta['item']
        
        #list of reviews' histogram rows selectors
        histRows = response.xpath('//tr[contains(@class, "a-histogram-row")]')
        
        #iterate over histRows in a reverse order (1-5, normally 5-1) and enumerated starting from 1
        for i, row in enumerate(reversed(histRows), 1):
            # get ith-star percentage
            pctg = row.xpath('.//a[contains(@class, "histogram-review-count")]/text()').extract_first()
            if(pctg):
                #ith star receives percentage converted to int except '%' character
                item['star'+str(i)] = int(pctg[:-1])
            else:
                #as design choice: if not found, use 0
                item['star'+str(i)] = 0
        
        #return item to be yielded
        return item
        
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))