#!/usr/bin/env python3

import os
import sys
import json
import cgi
import cgitb

from configuration import Configuration
from services import \
  DatabaseService, LegoSetService, LegoTrackService, ScrapingService
from controllers import LegoController

cgitb.enable(1, '/home/toast/Projects/lego', 5, 'text')


def FormatFormData(formdata):
    parameters = ', '.join([
        f'"{key}": "{formdata[key].value}"'
        for key in formdata.keys() if key != 'action'])
    return f'{{ "action": "{formdata["action"].value}",' \
        f'"parameters": {{ {parameters} }} }}'


if __name__ == '__main__':
    config = Configuration(os.path.join(
        os.path.dirname(__file__), 'settings-local.ini'))
    db = DatabaseService(config)
    ss = ScrapingService(config)
    ls = LegoSetService(db)
    lt = LegoTrackService(db)
    lc = LegoController(ls, lt, ss)

    # Discover request being made
    if 'REQUEST_METHOD' in os.environ:
        # Default action, nothing
        requestData = json.loads('{ "action": "invalid", "parameters": { } }')
        if os.environ['REQUEST_METHOD'] == 'GET':
            formdata = cgi.FieldStorage()
            requestData = json.loads(FormatFormData(formdata))
        elif os.environ['REQUEST_METHOD'] == 'POST':
            requestData = json.load(sys.stdin)

        lc.ProcessRequest(requestData)
