class LegoSet:
  def __init__(self, dataDict = None):
    if dataDict != None:
      self.importData(dataDict)
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
    desc = f'{self.setid} - {self.name}: {self.salePrice}'
    if self.discount != 0:
      desc = f'{desc} ({self.discount:%} {self.originalPrice})'
    if self.retiring:
      desc = f'{desc} (Retiring)'
    if self.new:
      desc = f'{desc} (New)'
    return desc

  def importData(self, dataDict):
    self.setid = dataDict['setid'] if 'setid' in dataDict else None
    self.originalPrice = dataDict['originalprice'] if 'originalprice' in dataDict else None
    self.salePrice = dataDict['saleprice'] if 'saleprice' in dataDict else None
    self.discount = dataDict['discount'] if 'discount' in dataDict else 0
    self.name = dataDict['name'] if 'name' in dataDict else None
    self.new = dataDict['new'] if 'new' in dataDict else False
    self.retiring = dataDict['retiring'] if 'retiring' in dataDict else False
    self.cancheck = dataDict['cancheck'] if 'cancheck' in dataDict else False
    self.modified = dataDict['modified'] if 'modified' in dataDict else None
    self.categories = []
      
  def toJson(self):
    return f'{{ "name": "{self.name}", "price": {self.salePrice}, "originalprice": {self.originalPrice}, "retiring": {self.retiring}, "new": {self.name}, "discount": {self.discount}, "modified": "{self.modified}", "cancheck": {self.cancheck}, "setid": {self.setid} }}'