import requests
import base64
import simplejson
import os
import json
import stat

class GetSubscribe():
    
    def __init__(self):
        self.subscribe = "https://lostcloud.net/link/kME8j06Wd7m8BwUk?mu=2"
        self.proxies = {
            "http": "http://127.0.0.1:8001",
            "https": "https://127.0.0.1:8001",
        }
        self.ServersPath = os.getcwd() + '/Servers.json'

    def getContent(self):
        text = requests.get(self.subscribe, verify=False).text
        if len(text) % 4:
            text += '=' * (4 - len(text) % 4)
        data = base64.b64decode(text)
        servers = bytes.decode(data).split('\n')[:-1]
        data = []
        for server in servers:
            info = server[8:]
            if len(info) % 4:
                info += '=' * (4 - len(info) % 4)
            info = bytes.decode(base64.b64decode(info))
            data.append(simplejson.loads(info))
        if not os.path.isfile(self.ServersPath):
            open(self.ServersPath, "w").close()
        with open(self.ServersPath, "w") as f:
            json.dump(data, f)
        print('保存完毕')



s = GetSubscribe()
s.getContent()
        