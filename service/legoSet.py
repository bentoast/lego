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
    self.setid = jsondata['setid'] if 'setid' in jsondata else None
    self.originalPrice = jsondata['originalprice'] if 'originalprice' in jsondata else None
    self.salePrice = jsondata['saleprice'] if 'saleprice' in jsondata else None
    self.discount = jsondata['discount'] if 'discount' in jsondata else 0
    self.name = jsondata['name'] if 'name' in jsondata else None
    self.new = jsondata['new'] if 'new' in jsondata else False
    self.retiring in jsondata['retiring'] if 'retiring' in jsondata else False
    self.cancheck = jsondata['cancheck'] if 'cancheck' in jsondata else False
    self.modified = jsondata['modified'] if 'modified' in jsondata else None
    self.categories = []
      
  def exportJson(self):
    jsonString = '{{ "name": "{}", "price": {}, "originalprice": {}, "retiring": {}, "new": {}, "discount": {}, "modified": "{}", "cancheck": {}, "setid": {} }}'.format(self.name, self.salePrice, self.originalPrice, self.retiring, self.new, self.discount, self.modified, self.cancheck, self.setid)
    return jsonString