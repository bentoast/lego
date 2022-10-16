#!/usr/bin/env python3

import urllib.request
import http.client
import ssl
import smtplib
from email.mime.text import MIMEText
from lxml import html
from decimal import Decimal
from legoset import LegoSet
import legoSettings as ls

changedSets = {}
sameSets = {}

def getSetInfo(element):
  currentSet = LegoSet()
    
  code = element.xpath('//span[@itemprop="productID"]/text()')
  hrefString = element.xpath('.//a[@data-test="product-leaf-title-link"]/@href')
  if hrefString != None and len(hrefString) > 0:
    code.append(hrefString[0].split('-')[-1])
  for currentCode in code:
    currentSet.setid = int(currentCode) 
    
  if currentSet.setid != None:
    name = element.xpath('.//h1[@data-test="product-overview-name"]/span/text()')
    name.extend(element.xpath('.//h2[@data-test="product-leaf-title"]/span/text()'))
    for currentName in name:
      currentSet.name = currentName.encode('ascii', errors='ignore').decode()
    
    flags = element.xpath('.//span[@data-test="product-flag"]/text()')
    currentSet.categories = flags
    currentSet.retiring = ('Retiring soon' in currentSet.categories)
    currentSet.new = ('New' in currentSet.categories)
  
    price = element.xpath('.//span[@data-test="product-price"]/text()')
    for currentPrice in price:
      modifiedPrice = Decimal(currentPrice[1:])
      currentSet.originalPrice = modifiedPrice
      currentSet.salePrice = modifiedPrice
    
    priceOld = element.xpath('.//span[@data-test="product-price-sale"]/text()')
    for currentOld in priceOld:
      modifiedOld = Decimal(currentOld[1:])
      currentSet.salePrice = modifiedOld
    
    discount = element.xpath('.//div[@data-test="sale-percentage"]/text()')
    for currentDiscount in discount:
      modifiedDiscount = Decimal(currentDiscount[:-5]) / 100
      currentSet.discount = modifiedDiscount
    
    return currentSet

def runCheck(site, xpath):
  count = 0
  sslcontext = ssl.create_default_context()
  try:
    orig = urllib.request.urlopen(site, context=sslcontext)
    info = orig.read()
    parser = html.fromstring(info.decode('ascii', errors='ignore'))
    setList = parser.xpath(xpath)
    for current in setList:
      setInfo = getSetInfo(current)
      if setInfo != None and setInfo.isDifferent():
        changedSets[setInfo.setid] = setInfo
      elif setInfo != None:
        sameSets[setInfo.setid] = setInfo
      count = count + 1
  except urllib.error.HTTPError as err:
    print(site)
    print(err.code)
    print('url lib error')
    return count
  except http.client.IncompleteRead:
    return runCheck(site, xpath)
  return count
  
def sendNewSets(setList):
  emailBody = '<table><tr><td colspan="2">Retiring</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  retiring = dict(filter(lambda s: s[1].retiring and s[1].originalPrice != None, setList.items()))
  for current in retiring.values():
    emailBody = '{}<tr><td><a href="https://lego.com/en-us/product/{}">{}</a></td><td>{}</td></tr>\r\n'.format(emailBody, current.setid, current.name, current.salePrice)
      
  emailBody = '{}<tr><td colspan="2">New Sets</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'.format(emailBody)
  newsets = dict(filter(lambda s: s[1].new and s[1].originalPrice != None, setList.items()))
  for current in newsets.values():
    emailBody = '{}<tr><td><a href="https://lego.com/en-us/product/{}">{}</a></td><td>{}</td></tr>\r\n'.format(emailBody, current.setid, current.name, current.salePrice)
    
  emailBody = '{}<tr><td colspan="2">Price Changes</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'.format(emailBody)
  priceChange = dict(filter(lambda s: not(s[1].new or s[1].retiring) and s[1].originalPrice != None, setList.items()))
  for current in priceChange.values():
    emailBody = '{}<tr><td><a href="https://lego.com/en-us/product/{}">{}</a></td><td>{}</td></tr>\r\n'.format(emailBody, current.setid, current.name, current.salePrice)
  emailBody = '{}</table>'.format(emailBody)
    
  message =  MIMEText(emailBody, 'html')
  message['subject'] = 'Changes'
  message['from'] = ls.settings['email']
  message['to'] = ls.settings['email']
  session = smtplib.SMTP(ls.settings['emailhost'], ls.settings['emailport'])
  context = ssl.create_default_context()
  session.starttls(context=context)
  session.login(ls.settings['email'], ls.settings['emailpassword'])
  session.sendmail(ls.settings['email'], ls.settings['email'], message.as_string())
  session.quit()
  
def getUncheckedSets(checkedList):
  end = ''
  if len(checkedList) > 0:
    end = 'WHERE SetId NOT IN ({})'.format(','.join(['%s'] * len(checkedList)))
  results = ls.getAll('SELECT SetId FROM LegoSet {}'.format(end), tuple(checkedList))
  
  for current in results:
    runCheck('https://lego.com/en-us/product/{}'.format(current[0]), '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-0 jkfnqG"]')
  
if __name__ == '__main__':
  
  categoryList = ['sales-and-deals', 'retiring-soon', 'new-sets-and-products']
  
  for current in categoryList:
    pageNumber = 1
    while runCheck('https://lego.com/en-us/categories/{}?page={}'.format(current, pageNumber), '//li[@data-test="product-item"]') > 0:
      pageNumber = pageNumber + 1
        
  sets = list(sameSets)
  getUncheckedSets(sets)
  sendNewSets(changedSets)
  for current in changedSets.values():
    current.save()