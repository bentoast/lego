#!/usr/bin/env python3

import datetime
import os

from configuration import Configuration
from models import LegoSet
from services import MessageService, DatabaseService, LegoSetService, ScrapingService

config = Configuration(os.path.join(os.path.dirname(__file__), 'settings-local.ini'))
ms = MessageService(config)
db = DatabaseService(config)
ls = LegoSetService(db)
ss = ScrapingService(config)

def FindSingleSet(setid):
  curSet = ss.ScrapeSite(f'https://lego.com/en-us/product/{setid}', '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-2 etzprq"]')
  
  if len(curSet) > 0:
    return curSet[setid]
  return None

def SendSetEmail(setList):
  emailBody = '<table><tr><td colspan="2">Retiring</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  retiring = list(filter(lambda s: s.retiring and s.originalPrice != None, setList))
  for current in retiring:
    emailBody = f'{emailBody}<tr><td><a href="https://lego.com/en-us/product/{current.setid}">{current.name}</a></td><td>{current.salePrise or current.orginalPrice}</td></tr>\r\n'

  emailBody = f'{emailBody}<tr><td colspan="2">New Sets</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  newsets = list(filter(lambda s: s.new and s.originalPrice != None, setList))
  for current in newsets:
    emailBody = f'{emailBody}<tr><td><a href="https://lego.com/en-us/product/{current.setid}">{current.name}</a></td><td>{current.price or current.originalPrice}</td></tr>\r\n'

  emailBody = f'{emailBody}<tr><td colspan="2">Price Changes</td></tr><tr><td>Set</td><td>Price</td></tr>\r\n'
  priceChange = list(filter(lambda s: not(s.new or s.retiring) and s.originalPrice != None, setList))
  for current in priceChange:
    emailBody = f'{emailBody}<tr><td><a href="https://lego.com/en-us/product/{current.setid}">{current.name}</a></td><td>{current.price or current.originalPrice}</td></tr>\r\n'

  emailBody = f'{emailBody}</table>'

  ms.SendMessage('html', 'Changes - The Lab', emailBody)
  
if __name__ == '__main__':
  print('legofinder.py running')
  categoryList = ['sales-and-deals', 'last-chance-to-buy', 'new-sets-and-products']
  date = datetime.datetime.now()
  
  for current in categoryList:
    pageNumber = 1

    while True:
      foundSets = ss.ScrapeSite(f'https://lego.com/en-us/categories/{current}?page={pageNumber}', '//li[@data-test="product-item"]')
      foundSets.values()
      pageNumber = pageNumber + 1
      if len(foundSets) == 0:
        break
      [ls.saveSet(current) for current in foundSets.values() if ls.hasChanges(current)]

  sets = ls.getUncheckedSets(date)
  for current in sets:
    foundSets = ss.ScrapeSite(f'https://lego.com/en-us/product/{current.setid}', '//div[starts-with(@class, "ProductOverviewstyles__Container"]')
    if len(foundSets) == 0:
      ls.disableCheck(current.setid)

  sets = ls.getUpdatedSets(date - datetime.timedelta(minutes=10))
  SendSetEmail(sets)