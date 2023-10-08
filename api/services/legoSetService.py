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
    
  def getFilteredSets(self, filter, order, asc, count, page):
    statement = '''SELECT 
        ls.Name,
        ls.Price,
        ls.OriginalPrice,
        ls.Discount,
        COALESCE(ls.Retiring, FALSE),
        COALESCE(ls.New, FALSE),
        ls.Modified,
        ls.SetId,
        COALESCE(lt.Track, FALSE),
        COALESCE(lt.Have, FALSE)'''
    bottomClause = '''
      FROM LegoSet ls
        LEFT OUTER JOIN LegoTrack lt ON ls.SetId = lt.SetId
      WHERE '''
    clauses = [
      'ls.Price IS NOT NULL',
      'ls.OriginalPrice IS NOT NULL',
      'ls.Discount < %(mindiscount)s',
      'ls.Discount >= %(maxdiscount)s']
    params = { 'maxdiscount': 0, 'mindiscount':1 }
    
    if 'new' in filter:
      clauses.append('ls.New = %(new)s')
      params['new'] = filter['new']
      
    if 'retiring' in filter:
      clauses.append('ls.Retiring = %(retiring)s')
      params['retiring'] = filter['retiring']

    if 'have' in filter:
      clauses.append('lt.Have = %(have)s')
      params['have'] = filter['have']
    
    if 'track' in filter:
      clauses.append('lt.Track = %(track)s')
      params['track'] = filter['track']

    if 'discount' in filter and filter['discount']:
      clauses.append('COALESCE(ls.Discount, 0) > 0')

    #This is math. We want to see if the SetId starts with the same digits as what we're passing
    #If we pass 41, we want 41234, 4140, 418954, etc.
    #We can express all numbers as n * 10^x. 41 is 4.1 * 10^1, 41234 is 4.1234 * 10^4, etc.
    #The difference of exponents tells us the magnitude we need to change the number by
    #We can find the exponents by taking the log(base 10) of the numbers.
    #4 - 1 is 3. 10^3 is 1000. So we divide the SetId by 1000 and floor it to get 41, then we can compare
    if 'setid' in filter:
      clauses.append('floor(ls.SetId / (10 ^ (floor(log(ls.SetId)) - floor(log(%(setid)s))))) = %(setid)s')
      params['setid'] = filter['setid']

    if 'name' in filter:
      clauses.append('LOWER(ls.Name) LIKE LOWER(%(name)s)')
      params['name'] = '%{}%'.format(filter['name'])

    bottomClause = bottomClause + ' AND '.join(clauses)

    countStatement = f'SELECT COUNT(*) {bottomClause}'
    countResult = self.databaseService.executeQuery(countStatement, params)[0]

    direction = 'DESC'
    if asc:
      direction = 'ASC'

    if count > 0:
      statement = f'''{statement} {bottomClause} ORDER BY {order} {direction} LIMIT {count} OFFSET {(page - 1) * count}'''
    else:
      statement = f'''{statement} {bottomClause}'''
      
    results = self.databaseService.executeQuery(statement, params)
    return (countResult, [LegoSet(current) for current in results])