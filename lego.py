#!/usr/bin/env python3

import os
import sys
import json
import cgi
import cgitb
import MySQLdb
import legoSettings as ls
import legofinder as lf
from legoset import LegoSet

cgitb.enable(1, '/home/pi/Lego', 5, 'text')

def getSets(newsets, retiringsets, maxdiscount, mindiscount):
  statement = '''SELECT 
      ls.Name,
      ls.Price,
      ls.OriginalPrice,
      ls.Discount,
      ls.Retiring,
      ls.New,
      ls.Modified,
      ls.SetId,
      IFNULL(lt.Track, 0),
      IFNULL(lt.Have, 0)
    FROM LegoSet ls
      LEFT OUTER JOIN LegoTrack lt ON ls.SetId = lt.SetId
    WHERE
      Price IS NOT NULL
      AND OriginalPrice IS NOT NULL
      AND Discount < %s
      AND Discount >= %s'''
  params = (maxdiscount, mindiscount)
  
  if newsets != None:
    statement = '{} AND ls.New = %s'.format(statement)
    params = params + (newsets,)
    
  if retiringsets != None:
    statement = '{} AND ls.Retiring = %s'.format(statement)
    params = params + (retiringsets,)
    
  results = ls.getAll(statement, params)
  final = []
  for current in results:	
    f = '''{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": {}, "have": {} }}'''.format(current[0].replace('"', '\\"'), current[1], current[2], current[3], current[4], current[5], current[6], current[7], current[8], current[9])
    final.append(f)
    
  return final
  
def RunGetRequest(formdata):
  nset = None
  if 'new' in formdata:
    nset = formdata['new'].value == 'yes'
  rset = None
  if 'retiring' in formdata:
    rset = formdata['retiring'].value == 'yes'
  mind = 0.00
  maxd = 1.00
  if 'discount' in formdata:
    if formdata['discount'].value == 'yes':
      mind = 0.01
    elif formdata['discount'].value == 'no':
      maxd = 0.01
  allLines = getSets(nset, rset, maxd, mind)
  
  print('Content-type: application/javascript')
  print()
  print('[{}]'.format(','.join(allLines)))
  
def RunSingleRequest(formdata):
  curSet = None
  setcount = lf.runCheck('https://lego.com/en-us/product/{}'.format(formdata['setid'].value), '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-0 jkfnqG"]')
  
  if len(lf.sameSets) > 0:
    curSet = list(lf.sameSets.values())[0]
  elif len(lf.changedSets) > 0:
    setcount = 8
    curSet = list(lf.changedSets.values())[0]
    
  print('Content-type: application/javascript')
  print()
  if curSet != None:
    curSet.save()
    r = 0
    if curSet.retiring:
      r = 1
    n = 0
    if curSet.new:
      n = 1
    print('''[{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": 0, "have": 0 }}]'''.format(curSet.name.replace('"', '\\"'), curSet.salePrice, curSet.originalPrice, curSet.discount, r, n, curSet.modified, curSet.setid))
  else:
    print('[{{"status": "failure", "setcount": {} }}]'.format(setcount))
  
def RunPostRequest(jsondata):
  countResult = ls.getOne('SELECT COUNT(*) FROM LegoTrack WHERE SetId = %s AND UserId = %s', (jsondata['setid'], 1))
  
  statement = 'UPDATE LegoTrack SET Track = %s, Have = %s WHERE SetId = %s AND UserId = %s;'
  if countResult != None and countResult[0] == 0:
    statement = 'INSERT INTO LegoTrack (Track, Have, SetId, UserId) VALUES (%s, %s, %s, %s);'
    
  ls.updaterow(statement, (jsondata['tracked'], jsondata['have'], jsondata['setid'], 1))
  
  print('Content-type: application/javascript')
  print()
  print('["success"]')

if __name__ == '__main__':  
  if 'REQUEST_METHOD' in os.environ:
    if os.environ['REQUEST_METHOD'] == 'GET':
      formdata = cgi.FieldStorage()
      if 'action' in formdata and formdata['action'].value == 'check':
        RunSingleRequest(formdata)
      else:
        RunGetRequest(formdata)
    elif os.environ['REQUEST_METHOD'] == 'POST':
      RunPostRequest(json.load(sys.stdin))