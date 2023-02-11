#!/usr/bin/env python3

import os
import json
import cgitb
import psycopg2 as db

cgitb.enable()

settingsFile = os.path.expanduser('/home/toast/Projects/lego/settings.ini')
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
    return cur.fetchall()
    
def getOne(statement, params):
    con = db.connect(
        host=settings['host'],
        user=settings['user'],
        password=settings['password'],
        database=settings['db'])
    cur = con.cursor()
    
    cur.execute(statement, params)
    return cur.fetchone()
    
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