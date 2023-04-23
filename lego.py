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
  params = { 'maxdiscount': maxdiscount, 'mindiscount':mindiscount }
  
  if newsets != None:
    clauses.append('ls.New = %(new)s')
    params['new'] = newsets
    
  if retiringsets != None:
    clauses.append('ls.Retiring = %(retiring)s')
    params['retiring'] = retiringsets

  bottomClause = bottomClause + ' AND '.join(clauses)

  countStatement = 'SELECT COUNT(*) {}'.format(bottomClause)
  countResult = ls.getOne(countStatement, params)

  if count > 0:
    statement = '''{} {} LIMIT {} OFFSET {}'''.format(statement, bottomClause, count, (page - 1) * count)
  else:
    statement = '''{} {}'''.format(statement, bottomClause)
    
  results = ls.getAll(statement, params)
  final = []
  for current in results:	
    f = '''{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": {}, "have": {} }}'''.format(current[0].replace('"', '\\"'), current[1], current[2], current[3], str(current[4]).lower(), str(current[5]).lower(), current[6], current[7], str(current[8]).lower(), str(current[9]).lower())
    final.append(f)
    
  return (countResult[0], final)
  
def MultipleRequest(request):
  nset = None
  if 'new' in request:
    nset = request['new'] == 'true'
  rset = None
  if 'retiring' in request:
    rset = request['retiring'] == 'true'
  mind = 0.00
  maxd = 1.00
  if 'discount' in request:
    if request['discount'] == 'true':
      mind = 0.01
    elif request['discount'] == 'false':
      maxd = 0.01
  page = 1
  if 'page' in request:
    page = int(request['page'])
  count = -1
  if 'count' in request:
    count = int(request['count'])
  (allCount, allLines) = getSets(nset, rset, mind, maxd, count, page)

  print('{{ "total": {}, "page": {}, "results": [{}]}}'.format(allCount, page, ','.join(allLines)))
  
def SingleRequest(request):
  (updatedSet, setcount) = lf.findSet(request['setid'])
  if updatedSet != None:
    print('''[{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": false, "have": false }}]'''.format(updatedSet.name.replace('"', '\\"'), updatedSet.salePrice, updatedSet.originalPrice, updatedSet.discount, str(updatedSet.retiring).lower(), str(updatedSet.new).lower(), updatedSet.modified, updatedSet.setid))
  else:
    print('[{{"status": "failure", "setcount": {} }}]'.format(setcount))
  
def UpdateRequest(jsondata):
  countResult = ls.getOne('SELECT COUNT(*) FROM LegoTrack WHERE SetId = %s AND UserId = %s', (jsondata['setid'], 1))
  
  statement = 'UPDATE LegoTrack SET Track = %s, Have = %s WHERE SetId = %s AND UserId = %s;'
  if countResult != None and countResult[0] == 0:
    statement = 'INSERT INTO LegoTrack (Track, Have, SetId, UserId) VALUES (%s, %s, %s, %s);'
    
  ls.updaterow(statement, (jsondata['tracked'], jsondata['have'], jsondata['setid'], 1))
  
  print('{{"status":"success"}}')

def FormatFormData(formdata):
  parameters = ', '.join([f'"{key}": "{formdata[key].value}"' for key in formdata.keys() if key != 'action' and key != 'order'])
  order = 'name'
  if 'order' in formdata:
    order = formdata['order'].value
  return f'{{ "action": "{formdata["action"].value}", "order": "{order}", "parameters": {{ {parameters} }} }}'

def ProcessRequest(requestData):
  routes = {
    'single': SingleRequest,
    'multiple': MultipleRequest,
    'update': UpdateRequest
  }

  #This is common to all requests
  print('Content-type: application/javascript')
  print()

  #Here are all of our commands so far.
  #Eventually, this will probably need to be different
  if requestData['action'] in routes:
    routes[requestData['action']](requestData['parameters'])
  else:
    print('{{"status:"invalid"}}')

if __name__ == '__main__':
  #Discover request being made
  if 'REQUEST_METHOD' in os.environ:
    #Default action, nothing
    requestData = json.loads('{ "action": "invalid", "parameters": { } }')
    if os.environ['REQUEST_METHOD'] == 'GET':
      formdata = cgi.FieldStorage()
      requestData = json.loads(FormatFormData(formdata))
    elif os.environ['REQUEST_METHOD'] == 'POST':
      requestData = json.load(sys.stdin)

    ProcessRequest(requestData)