#!/usr/bin/env python3

import json
import cgitb
import psycopg2 as db
from service.legoSet import LegoSet

cgitb.enable()

settingsFile = './service/settings-local.ini'
openFile = open(settingsFile)
settings = json.load(openFile)
openFile.close()

def getAll(statement, params):
  con = db.connect(
    host=settings['host'],
    user=settings['user'],
    password=settings['password'],
    database=settings['db'])
  cur = con.cursor()
  
  cur.execute(statement, params)
  fields = [desc[0] for desc in cur.description]
  return [dict(zip(fields, row)) for row in cur.fetchall()]
    
def getOne(statement, params):
  con = db.connect(
    host=settings['host'],
    user=settings['user'],
    password=settings['password'],
    database=settings['db'])
  cur = con.cursor()
  
  cur.execute(statement, params)
  fields = [desc[0] for desc in cur.description]
  return dict(zip(fields, cur.fetchone()))
    
def insertrow(statement, params):
  con = db.connect(
    host=settings['host'],
    user=settings['user'],
    password=settings['password'],
    database=settings['db'])
  cur = con.cursor()
  
  cur.execute(statement, params)
  con.commit()
  return True

def updaterow(statement, params):
  con = db.connect(
    host=settings['host'],
    user=settings['user'],
    password=settings['password'],
    database=settings['db'])
  cur = con.cursor()
  
  cur.execute(statement, params)
  con.commit()
  return True
    
def deleterow(statement, params):
  con = db.connect(
    host=settings['host'],
    user=settings['user'],
    password=settings['password'],
    database=settings['db'])
  cur = con.cursor()
  
  cur.execute(statement, params)
  con.commit()
  return True

def disableCheck(setid):
  return updaterow('UPDATE LegoSet SET CanCheck = \'f\' WHERE SetId = %s', (setid,))

def saveSet(set):
  #Check for existing set
  setcount = getOne('SELECT COUNT(*) FROM LegoSet WHERE SetId = %s', (set.setid,))

  if len(setcount) == 0 or setcount[0] == 0:
    insertrow('''
      INSERT INTO LegoSet (Name, Price, OriginalPrice, Discount, Retiring, New, Modified, CanCheck, SetId)
      VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)''', (set.name, set.salePrice, set.originalPrice, set.discount, set.retiring, set.new, set.cancheck, set.setid))
  else:
    updaterow('''
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

def getUncheckedSets(since):
  dbResults = getAll('SELECT SetId FROM LegoSet WHERE CanCheck = \'t\' AND Modified < %s', (since,))
  results = [LegoSet(current) for current in dbResults]
  return results

def getUpdatedSets(since):
  dbResults = getAll('SELECT SetId FROM LegoSet WHERE Modified > %s', (since,))
  results = [LegoSet(current) for current in dbResults]
  return results

def hasChanges(item):
  try:
    dbset = getOne('''
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
      SetId = %s''', (item.setid,))
    if dbset == None or dbset[0] != item.name or dbset[1] != item.salePrice or dbset[2] != item.originalPrice or \
      dbset[3] != item.discount or dbset[4] != item.retiring or dbset[5] != item.new:
      return True
  except:
    return False
  return False
