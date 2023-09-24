#!/usr/bin/env python3

import os
import sys
import json
import cgi
import cgitb
import service.legoService as ls
import api.legofinder as lf
from models import LegoSet

cgitb.enable(1, '/home/toast/Projects/lego', 5, 'text')
#TODO remove all of the SQL from here and put it in the service
def getSets(filter, order, asc, count, page):
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

  countStatement = 'SELECT COUNT(*) {}'.format(bottomClause)
  countResult = ls.getOne(countStatement, params)

  direction = 'DESC'
  if asc:
    direction = 'ASC'

  if count > 0:
    statement = '''{} {} ORDER BY {} {} LIMIT {} OFFSET {}'''.format(statement, bottomClause, order, direction, count, (page - 1) * count)
  else:
    statement = '''{} {}'''.format(statement, bottomClause)
    
  results = ls.getAll(statement, params)
  final = []
  for current in results:	
    f = '''{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": {}, "have": {} }}'''.format(current[0].replace('"', '\\"'), current[1], current[2], current[3], str(current[4]).lower(), str(current[5]).lower(), current[6], current[7], str(current[8]).lower(), str(current[9]).lower())
    final.append(f)
    
  return (countResult[0], final)
  
def MultipleRequest(request):
  filter = {}
  if 'new' in request:
    filter['new'] = request['new'] == 'true'
  if 'retiring' in request:
    filter['retiring'] = request['retiring'] == 'true'
  if 'have' in request:
    filter['have'] = request['have'] == 'true'
  if 'track' in request:
    filter['track'] = request['track'] == 'true'
  if 'setid' in request:
    filter['setid'] = request['setid']
  if 'name' in request:
    filter['name'] = request['name']
  if 'discount' in request:
    filter['discount'] = request['discount'] == 'true'
    
  page = 1
  if 'page' in request:
    page = int(request['page'])
  count = 10
  if 'count' in request:
    count = int(request['count'])

  (allCount, allLines) = getSets(filter, request['order'], 'asc' in request and request['asc'], count, page)

  print('{{ "total": {}, "page": {}, "results": [{}]}}'.format(allCount, page, ','.join(allLines)))
  
def SingleRequest(request):
  updatedSet = lf.FindSingleSet(request['setid'])
  if updatedSet != None:
    print('''[{{ "name": "{}", "price": {}, "originalprice": {}, "discount": {}, "retiring": {}, "new": {}, "modified": "{}", "setid": "{}", "tracked": false, "have": false }}]'''.format(updatedSet.name.replace('"', '\\"'), updatedSet.salePrice, updatedSet.originalPrice, updatedSet.discount, str(updatedSet.retiring).lower(), str(updatedSet.new).lower(), updatedSet.modified, updatedSet.setid))
  else:
    print('[{{"status": "failure", "setcount": 0 }}]')
  
def UpdateRequest(jsondata):
  countResult = ls.getOne('SELECT COUNT(*) FROM LegoTrack WHERE SetId = %s AND UserId = %s', (jsondata['setid'], 1))
  
  statement = 'UPDATE LegoTrack SET Track = %s, Have = %s WHERE SetId = %s AND UserId = %s;'
  if countResult != None and countResult[0] == 0:
    statement = 'INSERT INTO LegoTrack (Track, Have, SetId, UserId) VALUES (%s, %s, %s, %s);'
    
  ls.updaterow(statement, (jsondata['tracked'], jsondata['have'], jsondata['setid'], 1))
  
  print('{{"status":"success"}}')

def FormatFormData(formdata):
  parameters = ', '.join([f'"{key}": "{formdata[key].value}"' for key in formdata.keys() if key != 'action'])
  return f'{{ "action": "{formdata["action"].value}", "parameters": {{ {parameters} }} }}'

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