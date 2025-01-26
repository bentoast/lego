class LegoSet:
    def __init__(self, dataDict=None):
        if dataDict is not None:
            self.importData(dataDict)
        else:
            self.name = None
            self.categories = []
            self.originalPrice = None
            self.price = None
            self.discount = 0
            self.setid = None
            self.retiring = False
            self.new = False
            self.modified = None
            self.cancheck = True

    def __repr__(self):
        desc = f'{self.setid} - {self.name}: {self.price}'
        if self.discount != 0:
            desc = f'{desc} ({self.discount:%} {self.originalPrice})'
        if self.retiring:
            desc = f'{desc} (Retiring)'
        if self.new:
            desc = f'{desc} (New)'
        return desc

    def __eq__(self, other):
        if (other is None):
            return False
        return (
            self.name == other.name
            and self.price == other.price
            and self.originalPrice == other.originalPrice
            and self.discount == other.discount
            and self.setid == other.setid
            and self.new == other.new
            and self.retiring == other.retiring
        )

    def importData(self, dataDict):
        self.setid = dataDict['setid'] if 'setid' in dataDict else None
        self.originalPrice = dataDict['originalprice'] \
            if 'originalprice' in dataDict else None
        self.price = dataDict['price'] if 'price' in dataDict else None
        self.discount = dataDict['discount'] if 'discount' in dataDict else 0
        self.name = dataDict['name'] if 'name' in dataDict else None
        self.new = dataDict['new'] if 'new' in dataDict else False
        self.retiring = dataDict['retiring'] \
            if 'retiring' in dataDict else False
        self.cancheck = dataDict['cancheck'] \
            if 'cancheck' in dataDict else False
        self.modified = dataDict['modified'] \
            if 'modified' in dataDict else None
        self.categories = []

    def toJson(self):
        return f'{{ "name": "{self.name}",' \
            f'"price": {self.price or self.originalPrice},' \
            f'"originalprice": {self.originalPrice},' \
            f'"retiring": {"true" if self.retiring else "false"},' \
            f'"new": {"true" if self.new else "false"},' \
            f'"discount": {self.discount},' \
            f'"modified": "{self.modified}",' \
            f'"cancheck": {"true" if self.cancheck else "false"},' \
            f'"setid": {self.setid} }}'
