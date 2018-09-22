import json
import sys
import os
from log import log
import subprocess


class SwitchV2ray():
    def __init__(self):
        self.l = log()
        with open("../config/manager.json", 'r') as f:
            self.config = json.load(f)

    def turnV2rayOn(self):
        if self.config["server"] == {}:
            self.l.log("请选择服务器")
        else:
            cmd = '''export PATH=${PATH}:/usr/local/bin/
supervisorctl start v2ray
echo lzn19971012 | sudo -S networksetup -setwebproxy 'Wi-Fi' 127.0.0.1 8001 && sudo networksetup -setsecurewebproxy 'Wi-Fi' 127.0.0.1 8001 && sudo networksetup -setsocksfirewallproxy 'Wi-Fi' 127.0.0.1 1081'''
            result = subprocess.check_output(cmd, shell=True).decode("utf8")
            self.l.log(result)
            cmd = '''export PATH=${PATH}:/usr/local/bin/
                    supervisorctl status'''
            result = subprocess.check_output(cmd, shell=True).decode("utf8")
            self.l.log(result)
            if "RUNNING" in result:
                self.l.log("v2ray 启动成功")
                self.l.log("服务器: {}".format(self.config["server"]))
            else:
                self.l.log("v2ray 启动失败")

    def turnV2rayOff(self):
        cmd = '''export PATH=${PATH}:/usr/local/bin/
supervisorctl stop v2ray
echo lzn19971012 | sudo -S networksetup -setwebproxystate 'Wi-Fi' off && sudo networksetup -setsecurewebproxystate 'Wi-Fi' off && sudo networksetup -setsocksfirewallproxystate 'Wi-Fi' off'''
        result = subprocess.check_output(cmd, shell=True).decode("utf8")
        self.l.log(result)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
                            supervisorctl status'''
        result = subprocess.check_output(cmd, shell=True).decode("utf8")
        self.l.log(result)
        if "RUNNING" not in result:
            self.l.log("v2ray 关闭成功")
        else:
            self.l.log("v2ray 关闭成功")

    def changeServer(self, i):
        with open("../config/Servers.json", 'r') as f:
            servers = json.load(f)
        server = servers[i]
        with open("../v2ray/config.json", 'r') as f:
            config = json.load(f)
        settings = config["outbound"]["settings"]
        settings["vnext"][0]["address"] = server["add"]
        settings["vnext"][0]["port"] = int(server["port"])
        settings["vnext"][0]["users"][0]["id"] = server["id"]
        settings["vnext"][0]["users"][0]["alterId"] = int(server["aid"])
        settings["vnext"][0]["remark"] = server["ps"]
        streamSettings = config["outbound"]["streamSettings"]
        if server["tls"] == "tls":
            streamSettings["tlsSettings"]["serverName"] = server["add"]
            streamSettings["security"] = "tls"
        else:
            streamSettings["security"] = "none"
        if server["net"] == "tcp":
            streamSettings["network"] = "tcp"
        elif server["net"] == "kcp":
            streamSettings["network"] = "kcp"
        config["outbound"]["settings"] = settings
        config["outbound"]["streamSettings"] = streamSettings
        with open("../v2ray/config.json", 'w') as f:
            json.dump(config, f)
        self.config["server"] = server
        with open("../config/manager.json", 'w') as f:
            json.dump(self.config, f)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
                            supervisorctl status'''
        result = list(os.popen(cmd))[0]
        if "RUNNING" in result:
            cmd = '''export PATH=${PATH}:/usr/local/bin/
            supervisorctl stop v2ray
            supervisorctl start v2ray'''
            result = subprocess.check_output(cmd, shell=True)
            self.l.log(result)
        else:
            cmd = '''export PATH=${PATH}:/usr/local/bin/
            supervisorctl start v2ray'''
            result = subprocess.check_output(cmd, shell=True)
            self.l.log(result)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
                                    supervisorctl status'''
        result = list(os.popen(cmd))[0]
        if "RUNNING" in result:
            return True
        else:
            return False

    def switchRule(self):
        with open("../v2ray/config.json", 'r') as f:
            config = json.load(f)
        rules = [{
            "domain": [
                "localhost",
                "geosite:cn"
            ],
            "type": "field",
            "outboundTag": "direct"
        },
            {
                "type": "field",
                "outboundTag": "direct",
                "ip": [
                    "geoip:private",
                    "geoip:cn"
                ]
            }
        ]
        config["routing"]["settings"]["rules"] = rules
        with open('../v2ray/config.json', 'w') as f:
            json.dump(config, f)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
python3 /Users/hayashikoushi/Documents/code/v2rayManager/SwitchPAC.py
supervisorctl stop v2ray
supervisorctl start v2ray'''
        result = subprocess.check_output(cmd, shell=True)
        self.config["mode"] = "rule"
        with open("../config/manager.json", 'w') as f:
            json.dump(self.config, f)
        self.l.log(result)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
                                            supervisorctl status'''
        result = list(os.popen(cmd))[0]
        if "RUNNING" in result:
            return True
        else:
            return False

    def switchGlobal(self):
        with open('../v2ray/config.json', 'r') as f:
            config = json.load(f)
        rules = [{
            "type": "field",
            "outboundTag": "direct",
            "ip": [
                "geoip:private",
            ]
        }]
        config["routing"]["settings"]["rules"] = rules
        with open('../v2ray/config.json', 'w') as f:
            json.dump(config, f)
        self.config["mode"] = "global"
        with open("../config/manager.json", 'w') as f:
            json.dump(self.config, f)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
        python3 /Users/hayashikoushi/Documents/code/v2rayManager/SwitchPAC.py
        supervisorctl stop v2ray
        supervisorctl start v2ray'''
        result = subprocess.check_output(cmd, shell=True)
        self.l.log(result)
        cmd = '''export PATH=${PATH}:/usr/local/bin/
                                                    supervisorctl status'''
        result = list(os.popen(cmd))[0]
        if "RUNNING" in result:
            return True
        else:
            return False
