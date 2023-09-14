#!/usr/bin/env python3

class LegoSet:
  def __init__(self, dbdata = None, format='db'):
    print(dbdata)
    if (dbdata != None and format == 'db'):
      self.name = dbdata.get('Name')
      self.categories = []
      self.originalPrice = dbdata.get('OriginalPrice')
      self.salePrice = dbdata.get('Price')
      self.discount = dbdata.get('Discount')
      self.setid = dbdata.get('SetId')
      self.retiring = dbdata.get('Retiring')
      self.new = dbdata.get('New')
      self.modified = dbdata.get('Modified')
      self.cancheck = dbdata.get('CanCheck')
    elif (dbdata != None and format == 'json'):
      self.importJson(dbdata)
    else:
      self.name = None
      self.categories = []
      self.originalPrice = None
      self.salePrice = None
      self.discount = 0
      self.setid = None
      self.retiring = False
      self.new = False
      self.modified = None
      self.cancheck = False

  def __repr__(self):
    desc = '{} - {}: {}'.format(self.setid, self.name, self.salePrice)
    if self.discount != 0:
      desc = '{} ({:%} {})'.format(desc, self.discount, self.originalPrice)
    if self.retiring:
      desc = '{} (Retiring)'.format(desc)
    if self.new:
      desc = '{} (New)'.format(desc)
    return desc

  def importJson(self, jsondata):
    if 'setid' in jsondata:
      self.setid = jsondata['setid']
    if 'originalprice' in jsondata:
      self.originalPrice = jsondata['originalprice']
    if 'saleprice' in jsondata:
      self.salePrice = jsondata['saleprice']
    if 'discount' in jsondata:
      self.discount = jsondata['discount']
    if 'name' in jsondata:
      self.name = jsondata['name']
    if 'new' in jsondata:
      self.new = jsondata['new']
    if 'retiring' in jsondata:
      self.retiring in jsondata['retiring']
    if 'cancheck' in jsondata:
      self.cancheck = jsondata['cancheck']
      
  def exportJson(self):
    jsonString = '{{ "name": "{}", "price": {}, "originalprice": {}, "retiring": {}, "new": {}, "discount": {}, "modified": "{}", "cancheck": {}, "setid": {} }}'.format(self.name, self.salePrice, self.originalPrice, self.retiring, self.new, self.discount, self.modified, self.cancheck, self.setid)
    return jsonString