#!/usr/bin/env python3

import os
import sys
import json
import cgi
import cgitb
import legoSettings as ls
import legofinder as lf
from legoset import LegoSet

cgitb.enable(1, '/home/toast/Projects/lego', 5, 'text')

def getSets(newsets, retiringsets, maxdiscount, mindiscount, count, page):
  statement = '''SELECT 
      ls.Name,
      ls.Price,
      ls.OriginalPrice,
      ls.Discount,
      CASE WHEN ls.Retiring THEN 1 ELSE 0 END,
      CASE WHEN ls.New THEN 1 ELSE 0 END,
      ls.Modified,
      ls.SetId,
      CASE WHEN lt.Track THEN 1 ELSE 0 END,
      CASE WHEN lt.Have THEN 1 ELSE 0 END'''
  bottomClause = '''
    FROM LegoSet ls
      LEFT OUTER JOIN LegoTrack lt ON ls.SetId = lt.SetId
    WHERE
      Price IS NOT NULL
      AND OriginalPrice IS NOT NULL
      AND Discount < %s
      AND Discount >= %s'''
  params = (maxdiscount, mindiscount)
  
  if newsets != None:
    bottomClause = '{} AND ls.New = %s'.format(bottomClause)
    params = params + (newsets,)
    
  if retiringsets != None:
    bottomClause = '{} AND ls.Retiring = %s'.format(bottomClause)
    params = params + (retiringsets,)

  countStatement = 'SELECT COUNT(*) {}'.format(bottomClause)
  countResult = ls.getOne(countStatement, params)

  if count > 0:
    statement = '''{} {} LIMIT {} OFFSET {}'''.format(statement, bottomClause, count, (page - 1) * count)
    
  results = ls.getAll(statement, params)
  final = []
  for current in results:	
    f = '''{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": {}, "have": {} }}'''.format(current[0].replace('"', '\\"'), current[1], current[2], current[3], current[4], current[5], current[6], current[7], current[8], current[9])
    final.append(f)
    
  return (countResult[0], final)
  
def MultipleRequest(request):
  nset = None
  if 'new' in request:
    nset = request['new'] == 'yes'
  rset = None
  if 'retiring' in request:
    rset = request['retiring'] == 'yes'
  mind = 0.00
  maxd = 1.00
  if 'discount' in request:
    if request['discount'] == 'yes':
      mind = 0.01
    elif request['discount'] == 'no':
      maxd = 0.01
  page = 1
  if 'page' in request:
    page = int(request['page'])
  count = -1
  if 'count' in request:
    count = int(request['count'])
  (allCount, allLines) = getSets(nset, rset, maxd, mind, count, page)
  
  print('{{ "total": {}, "page": {}, "results": [{}]}}'.format(allCount, page, ','.join(allLines)))
  
def SingleRequest(request):
  curSet = None
  setcount = lf.runCheck('https://lego.com/en-us/product/{}'.format(request['setid']), '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-0 jkfnqG"]')
  
  if len(lf.sameSets) > 0:
    curSet = list(lf.sameSets.values())[0]
  elif len(lf.changedSets) > 0:
    setcount = 8
    curSet = list(lf.changedSets.values())[0]
    
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
  
def UpdateRequest(jsondata):
  countResult = ls.getOne('SELECT COUNT(*) FROM LegoTrack WHERE SetId = %s AND UserId = %s', (jsondata['setid'], 1))
  
  statement = 'UPDATE LegoTrack SET Track = %s, Have = %s WHERE SetId = %s AND UserId = %s;'
  if countResult != None and countResult[0] == 0:
    statement = 'INSERT INTO LegoTrack (Track, Have, SetId, UserId) VALUES (%s, %s, %s, %s);'
    
  ls.updaterow(statement, (jsondata['tracked'], jsondata['have'], jsondata['setid'], 1))
  
  print('["success"]')

def FormatFormData(formdata):
  parameters = ', '.join([f'{key}: "{formdata[key].value}"' for key in formdata.keys() if key != 'action'])
  return f'{{ action: "{formdata["action"].value}", parameters: {{ {parameters} }} }}'

def ProcessRequest(requestData):
  #This is common to all requests
  print('Content-type: application/javascript')
  print()

  #Here are all of our commands so far.
  #Eventually, this will probably need to be different
  if requestData['action'] == 'single':
    SingleRequest(requestData['parameters'])
  elif requestData['action'] == 'multiple':
    MultipleRequest(requestData['parameters'])
  elif requestData['action'] == 'update':
    UpdateRequest(requestData['parameters'])
  return None

if __name__ == '__main__':
  #Discover request being made
  if 'REQUEST_METHOD' in os.environ:
    #Default action, nothing
    requestData = json.loads('{ action: "invalid", parameters: [] }')
    if os.environ['REQUEST_METHOD'] == 'GET':
      formdata = cgi.FieldStorage()
      requestData = json.loads(FormatFormData(formdata))
    elif os.environ['REQUEST_METHOD'] == 'POST':
      requestData = (sys.stdin)

    ProcessRequest(requestData)