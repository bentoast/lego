#!/usr/bin/env python3
import legoSettings as ls

class LegoSet:
  def __init__(self):
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

  def isDifferent(self):
    try:
      dbset = ls.getOne('''
      SELECT
        Name,
        Price,
        OriginalPrice,
        Discount,
        Retiring,
        New,
        Modified,
        SetId
      FROM LegoSet
      WHERE
        SetId = %s''', (self.setid,))
      if dbset == None or dbset[0] != self.name or dbset[1] != self.salePrice or dbset[2] != self.originalPrice or \
        dbset[3] != self.discount or dbset[4] != self.retiring or dbset[5] != self.new:
        return True
    except:
      return False
    return False

  def save(self):
    #Check for existing set
    setcount = ls.getOne('SELECT COUNT(*) FROM LegoSet WHERE SetId = %s', (self.setid,))

    if setcount[0] == 0:
      ls.insertrow('''
        INSERT INTO LegoSet (Name, Price, OriginalPrice, Discount, Retiring, New, Modified, CanCheck, SetId)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)''', (self.name, self.salePrice, self.originalPrice, self.discount, self.retiring, self.new, self.cancheck, self.setid))
    else:
      ls.updaterow('''
      UPDATE LegoSet SET
        Name = %s,
        Price = %s,
        OriginalPrice = %s,
        Discount = %s,
        Retiring = %s,
        New = %s,
        Modified = NOW(),
        CanCheck = %s
      WHERE
        SetId = %s''', (self.name, self.salePrice, self.originalPrice, self.discount, self.retiring, self.new, self.cancheck, self.setid))