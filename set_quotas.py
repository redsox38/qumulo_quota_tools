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

CONFIG_FILE = "/etc/ua_hpc_acct.conf"

def parse_config_file(fname):
    c = {}

    f = open(fname, 'rb')
    for l in f:
        parts = l.split()
        c[parts[0].decode('utf-8')] = parts[1].decode('utf-8')

    f.close()

    return c  

def _send_req(method, uri, data, hdrs):
    c = http.client.HTTPSConnection("target.hpc.arizona.edu", cfg['qPort'])
    
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

def auth(cfg):

    r = _send_req("POST", "/v1/session/login", { "username": cfg['qUser'], "password": cfg['qPass'] }, { 'Content-Type': "application/json" })

    return(r['bearer_token'])

def createQuota(token, fid, limit):

    uri = "/v1/files/quotas/"

    r = _send_req("POST", uri, { "limit": limit, "id": fid }, { 'Content-Type': "application/json", "Authorization": "Bearer " + token })

    return(True)

def getFileId(tkn, path):

    uri = "/v1/files/" + urllib.parse.quote(path, safe = '') + "/info/attributes"

    r = _send_req("GET", uri, None, { "Authorization": "Bearer " + tkn })
  
    return(r['file_number'])


cfg = parse_config_file(CONFIG_FILE)
api_token = auth(cfg)

for l in sys.stdin:
    [ path, limit ] = l.rstrip().split(':')
    
    fid = getFileId(api_token, path)
    createQuota(api_token, fid, limit)
    print("set %s to %s" % (path, limit))
