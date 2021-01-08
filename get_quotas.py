#!/usr/bin/python3

import http.client
import json
import os
import urllib
import socket
import subprocess
import pwd
import sys
from stat import *

Q_HOST = ""
Q_PORT = "8000"
Q_USER = ""
Q_PASS = ""

def _send_req(method, uri, data, hdrs):
    c = http.client.HTTPSConnection(Q_HOST, Q_PORT)
    
    try:
        if data != None:
            json_data = json.dumps(data)
        else:
            json_data = None
        
        c.request(method, uri, json_data, hdrs)
        rsp = c.getresponse()
     
        if (rsp.status != 200):
            raise Exception("%d: %s" % (rsp.status, rsp.reason))

        j = rsp.read().decode()
 
        return(json.loads(j))

    except Exception as e:
        message = os.strerror(e.errno) if hasattr(e, 'errno') else str(e)
        print(message)
        sys.exit(-1)

def auth():

    r = _send_req("POST", "/v1/session/login", { "username": Q_USER, "password": Q_PASS }, { 'Content-Type': "application/json" })

    return(r['bearer_token'])

def getHPCquotas(token):
    q = {}
    done = False

    uri = "/v1/files/quotas/status/"

    while not done:
        r = _send_req("GET", uri, None, { "Authorization": "Bearer " + token })    
        uri = r['paging']['next']

        if (uri == ""):
            done = True
        
        for e in r['quotas']:
            q[e['path']] = { 'limit' : e['limit'] }
        
    return(q)

api_token = auth()
quotas = getHPCquotas(api_token)

for q in quotas:
    print("%s:%s" % (q, quotas[q]['limit']))
