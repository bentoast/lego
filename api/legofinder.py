#!/usr/bin/env python3

import datetime
import urllib.request
import http.client
import ssl
import os
from lxml import html
from decimal import Decimal

from configuration import Configuration
from models import LegoSet
from services import MessageService, DatabaseService, LegoSetService

config = Configuration(os.path.join(os.path.dirname(__file__), 'settings-local.ini'))
ms = MessageService(config)
db = DatabaseService(config)
ls = LegoSetService(db)

def FindSingleSet(setid):
  curSet = ScrapeSite(f'https://lego.com/en-us/product/{setid}', '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-2 etzprq"]')
  
  if len(curSet) > 0:
    return curSet[setid]
  return None

def ExtractSetInfo(element):
  currentSet = LegoSet()

  code = element.xpath('//span[@itemprop="sku"]/text()')
  #This will also contain product codes
  hrefString = element.xpath('.//a[@data-test="product-image-link"]/@href')
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
      currentSet.salePrice = modifiedPrice
    
    priceOld = element.xpath('.//span[@data-test="product-price-sale"]/text()')
    priceOld.extend(element.xpath('.//span[@data-test="product-leaf-discounted-sale"]/text()'))
    for currentOld in priceOld:
      modifiedOld = Decimal(currentOld[1:])
      currentSet.salePrice = modifiedOld
    
    discount = element.xpath('.//div[@data-test="sale-percentage"]/text()')
    discount.extend(element.xpath('.//span[@data-test="product-leaf-discounted-badge"]/text()'))
    for currentDiscount in discount:
      modifiedDiscount = Decimal(currentDiscount[:-5]) / 100
      currentSet.discount = modifiedDiscount
    
    return currentSet

def ScrapeSite(site, xpath):
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
      setInfo = ExtractSetInfo(current)
      if setInfo != None:
        results[setInfo.setid] = setInfo
  except urllib.error.HTTPError as err:
    ms.SendMessage('html', 'Error - The Lab', f'{site}\r\n{err.code}\r\n{err.reason}\r\nurllib error\r\n')
    return results
  except http.client.IncompleteRead:
    return ScrapeSite(site, xpath)
  return results
  
def SendSetEmail(setList):
  emailBody = '<table><tr><td colspan="2">Retiring</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  retiring = list(filter(lambda s: s.retiring and s.originalPrice != None, setList))
  for current in retiring:
    emailBody = f'{emailBody}<tr><td><a href="https://lego.com/en-us/product/{current.setid}">{current.name}</a></td><td>{current.salePrise or current.orginalPrice}</td></tr>\r\n'

  emailBody = f'{emailBody}<tr><td colspan="2">New Sets</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  newsets = list(filter(lambda s: s.new and s.originalPrice != None, setList))
  for current in newsets:
    emailBody = f'{emailBody}<tr><td><a href="https://lego.com/en-us/product/{current.setid}">{current.name}</a></td><td>{current.salePrice or current.originalPrice}</td></tr>\r\n'

  emailBody = f'{emailBody}<tr><td colspan="2">Price Changes</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  priceChange = list(filter(lambda s: not(s.new or s.retiring) and s.originalPrice != None, setList))
  for current in priceChange:
    emailBody = f'{emailBody}<tr><td><a href="https://lego.com/en-us/product/{current.setid}">{current.name}</a></td><td>{current.salePrice or current.originalPrice}</td></tr>\r\n'

  emailBody = f'{emailBody}</table>'

  ms.SendMessage('html', 'Changes - The Lab', emailBody)
  
if __name__ == '__main__':
  print('legofinder.py running')
  categoryList = ['sales-and-deals', 'retiring-soon', 'new-sets-and-products']
  date = datetime.datetime.now()
  
  for current in categoryList:
    pageNumber = 1

    while True:
      foundSets = ScrapeSite(f'https://lego.com/en-us/categories/{current}?page={pageNumber}', '//li[@data-test="product-item"]')
      foundSets.values()
      pageNumber = pageNumber + 1
      if len(foundSets) == 0:
        break
      [ls.saveSet(current) for current in foundSets.values()]

  sets = ls.getUncheckedSets(date)
  for current in sets:
    foundSets = ScrapeSite(f'https://lego.com/en-us/product/{current.setid}', '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-2 etzprq"]')
    if len(foundSets) == 0:
      ls.disableCheck(current[0])

  sets = ls.getUpdatedSets(date - datetime.timedelta(minutes=10))
  SendSetEmail(sets)