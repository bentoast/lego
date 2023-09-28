from models import LegoSet

class LegoSetService:
  def __init__(self, databaseService) -> None:
    self.databaseService = databaseService

  def getSetById(self, setid) -> LegoSet:
    dbResults = self.databaseService.executeQuery('''SELECT * FROM LegoSet WHERE SetId = %s''', (setid,))
    if dbResults == None or len(dbResults) == 0:
      return None
    return LegoSet(dbResults[0])
  
  def hasSet(self, setid) -> bool:
    dbResults = self.databaseService.executeQuery('''SELECT COUNT(*) AS SetCount FROM LegoSet WHERE SetId = %s''', (setid,))
    if dbResults == None or len(dbResults) == 0:
      return False
    return dbResults[0]['setcount'] > 0

  def disableCheck(self, setid):
    return self.databaseService.executeNonQuery('UPDATE LegoSet SET CanCheck = \'f\' WHERE SetId = %s', (setid,))

  def saveSet(self, set):
    if not self.hasSet(set.setid):
      self.databaseService.executeNonQuery('''
        INSERT INTO LegoSet (Name, Price, OriginalPrice, Discount, Retiring, New, Modified, CanCheck, SetId)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)''', (set.name, set.salePrice, set.originalPrice, set.discount, set.retiring, set.new, set.cancheck, set.setid))
    else:
      self.databaseService.executeNonQuery('''
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
          SetId = %s''', (set.name, set.salePrice, set.originalPrice, set.discount, set.retiring, set.new, set.cancheck, set.setid))

  def getUncheckedSets(self, since):
    dbResults = self.databaseService.executeQuery('''SELECT 
        ls.Name,
        ls.Price,
        ls.OriginalPrice,
        ls.Discount,
        COALESCE(ls.Retiring, FALSE) AS Retiring,
        COALESCE(ls.New, FALSE) AS New,
        ls.Modified,
        ls.SetId,
        COALESCE(lt.Track, FALSE) AS Track,
        COALESCE(lt.Have, FALSE) AS Have
      FROM LegoSet ls
        LEFT OUTER JOIN LegoTrack lt ON ls.SetId = lt.SetId
      WHERE CanCheck = \'t\' AND Modified < %s''', (since,))
    results = [LegoSet(current) for current in dbResults]
    return results

  def getUpdatedSets(self, since):
    dbResults = self.databaseService.executeQuery('''SELECT 
        ls.Name,
        ls.Price,
        ls.OriginalPrice,
        ls.Discount,
        COALESCE(ls.Retiring, FALSE) AS Retiring,
        COALESCE(ls.New, FALSE) AS New,
        ls.Modified,
        ls.SetId,
        COALESCE(lt.Track, FALSE) AS Track,
        COALESCE(lt.Have, FALSE) AS Have
      FROM LegoSet ls
        LEFT OUTER JOIN LegoTrack lt ON ls.SetId = lt.SetId
      WHERE Modified > %s''', (since,))
    results = [LegoSet(current) for current in dbResults]
    return results

  def hasChanges(self, item):
    try:
      existing = self.getSetById(item.setid)
      if existing == None or item != existing:
        return True
    except:
      return False
    return False