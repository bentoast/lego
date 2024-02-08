import urllib.request
import http.client
import ssl
from lxml import html
from decimal import Decimal

from models import LegoSet

class ScrapingService:
  def __init__(self, configuration):
    self.configuration = configuration

  def ScrapeSite(self, site, xpath):
    results = {}

    sslcontext = ssl.create_default_context()
    try:
      #This is to get around the 403 error
      request = urllib.request.Request(site, headers={'User-Agent': 'Mozilla/5.0'})
      orig = urllib.request.urlopen(request, context=sslcontext)
      info = orig.read()
      
      parser = html.fromstring(info.decode('ascii', errors='ignore'))
      setList = parser.xpath(xpath)
      
      for current in setList:
        setInfo = self.ExtractSetInfo(current)
        if setInfo != None:
          results[setInfo.setid] = setInfo
    except http.client.IncompleteRead:
      return self.ScrapeSite(site, xpath)
    except urllib.error.HTTPError as err:
      return results
    return results
  
  def ExtractSetInfo(self, element):
    currentSet = LegoSet()

    code = element.xpath('//span[@itemprop="mpn"]/text()')
    code.extend(element.xpath('//article/@data-test-key/text()'))
    #This will also contain product codes
    hrefString = element.xpath('.//a[@data-test="product-leaf-image-link"]/@href')
    if hrefString != None and len(hrefString) > 0:
      #The URL will look like en-us/product/blah-blah-12345 or en-us/product/12345
      #So we need the last part of the URL, and the last part of that
      code.append(hrefString[0].split('/')[-1].split('-')[-1])
    for currentCode in code:
      currentSet.setid = int(currentCode) 
      
    if currentSet.setid != None:
      name = element.xpath('.//h1[@data-test="product-overview-name"]/span/text()')
      name.extend(element.xpath('.//a[@data-test="product-leaf-title"]/span/text()'))
      for currentName in name:
        currentSet.name = currentName.encode('ascii', errors='ignore').decode()
      
      flags = element.xpath('.//span[@data-test="product-flag"]/text()')
      flags.extend(element.xpath('.//span[@data-test="product-leaf-badge"]/text()'))
      currentSet.categories = flags
      currentSet.retiring = ('Retiring soon' in currentSet.categories)
      currentSet.new = ('New' in currentSet.categories)
    
      price = element.xpath('.//span[@data-test="product-price"]/text()')
      price.extend(element.xpath('.//span[@data-test="product-leaf-price"]/text()'))
      for currentPrice in price:
        modifiedPrice = Decimal(currentPrice[1:])
        currentSet.originalPrice = modifiedPrice
        currentSet.price = modifiedPrice
      
      priceOld = element.xpath('.//span[@data-test="product-price-sale"]/text()')
      priceOld.extend(element.xpath('.//span[@data-test="product-leaf-discounted-price"]/text()'))
      for currentOld in priceOld:
        modifiedOld = Decimal(currentOld[1:])
        currentSet.price = modifiedOld
      
      discount = element.xpath('.//div[@data-test="sale-percentage"]/text()')
      discount.extend(element.xpath('.//span[@data-test="product-leaf-discount-badge"]/text()'))
      for currentDiscount in discount:
        modifiedDiscount = Decimal(currentDiscount[:-5]) / 100
        currentSet.discount = modifiedDiscount
      
      return currentSet