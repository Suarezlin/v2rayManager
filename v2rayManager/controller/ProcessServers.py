import json
import sys

class ProcessServers():
    def __init__(self):
        self.serversPath = "../config/Servers.json"
        self.v2rayConfigPath = "../v2ray/config.json"

    def getServersWithJson(self):
        with open(self.serversPath, 'r') as f:
            try:
                self.servers = json.load(f)
            except:
                print("读取读取服务器列表失败!")
                sys.exit()

    def getServerLists(self):
        self.getServersWithJson()
        result = []
        i = 1
        for server in self.servers:
            result.append("{}-{}".format(i, server["ps"]))
            i += 1
        self.serverList = result

    def getV2rayConfig(self):
        with open(self.v2rayConfigPath, 'r') as f:
            try:
                self.servers = json.load(f)
            except:
                print("读取读取 v2ray 配置失败!")
                sys.exit()



