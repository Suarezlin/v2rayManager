from PyQt5.QtWidgets import QWidget, QListWidgetItem
from v2rayManager.view.ServerConfigView import Ui_ServerConfig
import json


class ServerConfigView(QWidget, Ui_ServerConfig):
    def __init__(self, parent=None):
        super(ServerConfigView, self).__init__(parent)
        self.setupUi(self)
        with open("../config/Servers.json", 'r') as f:
            self.servers = json.load(f)
        self.oldServers = self.servers
        self.showServerList()
        self.listWidget.itemClicked.connect(self.showServerInfo)
        self.TSLInput.toggled.connect(self.changeTSL)
        self.AddServerButton.clicked.connect(self.addServer)
        self.addServerList = []
        self.DeleteServerList = []
        self.AcceptButton.clicked.connect(self.accept)
        self.CancelButton.clicked.connect(self.cancel)
        self.EditServerButton.clicked.connect(self.saveServer)
        self.DeleteServerButton.clicked.connect(self.deleteServer)


    def addServer(self):
        q = QListWidgetItem("新服务器")
        self.AddressInput.setText("")
        self.PortInput.setText("")
        self.MethodSelect.setCurrentIndex(0)
        self.UIDInput.clear()
        self.AIDInput.clear()
        self.ConnectInput.setCurrentIndex(0)
        self.RemarkInput.setText("新服务器")
        self.TSLInput.setChecked(False)
        self.DownlinkCapacityInput.clear()
        self.UplinkCapacityInput.clear()
        self.ReadBufferInput.clear()
        self.WriteBufferInput.clear()
        self.TtiInput.clear()
        self.MtuInput.clear()
        self.CongestionInput.setCurrentIndex(0)

        self.HeaderTypeInput.setCurrentIndex(0)

        self.TCPHeaderInput.clear()

        self.WsPathInput.clear()
        self.WsHeadersInput.clear()

        self.Http2HostInput.clear()
        self.Http2PathInput.clear()

        self.listWidget.addItem(q)
        self.listWidget.setCurrentItem(q)

    def saveServer(self):
        s = {
            "v": "2",
            "ps": "",
            "add": "",
            "port": "",
            "id": "",
            "aid": "",
            "net": "",
            "type": "",
            "host": "",
            "path": "",
            "tls": ""
        }
        s["ps"] = self.RemarkInput.text()
        s["add"] = self.AddressInput.text()
        s["port"] = int(self.PortInput.text())
        s["id"] = self.UIDInput.text()
        s["aid"] = self.AIDInput.text()
        s["net"] = self.ConnectInput.currentText()
        s["type"] = "auto"
        if self.TSLInput.isChecked():
            s["tls"] = "tls"
        i = 0
        for server in self.servers:
            if server["add"] == s["add"]:
                self.servers[i] = s
                self.listWidget.setCurrentItem(QListWidgetItem(s["ps"]))
                break
                return
            i += 1
        self.servers.append(s)
        self.listWidget.setCurrentItem(QListWidgetItem(s["ps"]))


    def deleteServer(self):
        name = self.listWidget.currentItem().text()
        i = 0
        for server in self.servers:
            if server["ps"] == name:
                self.DeleteServerList.append(server)
                self.servers.remove(self.servers[i])
                self.listWidget.removeItemWidget(self.listWidget.currentItem())
            i += 1

    def accept(self):
        with open("../config/Servers.json", 'w') as f:
            json.dump(self.servers, f)
        self.close()

    def cancel(self):
        self.servers = self.oldServers
        self.close()




    def changeTSL(self):
        if self.TSLInput.isChecked():
            self.TLSAllowInput.setEnabled(True)
        else:
            self.TLSAllowInput.setEnabled(False)

    def showServerInfo(self, item):
        for server in self.servers:
            if item.text() == server["ps"]:
                self.AddressInput.setText(server["add"])
                self.PortInput.setText(str(server["port"]))
                if server["type"] is None:
                    self.MethodSelect.setCurrentIndex(0)
                elif server["type"] == "aes-256-cfb":
                    self.MethodSelect.setCurrentIndex(1)
                self.UIDInput.setText(server["id"])
                self.AIDInput.setText(str(server["aid"]))
                if server["net"] == "tcp":
                    self.ConnectInput.setCurrentIndex(0)
                elif server["net"] == "kcp":
                    self.ConnectInput.setCurrentIndex(1)
                self.RemarkInput.setText(server["ps"])
                if server["tls"] == "tls":
                    self.TSLInput.setChecked(True)
                else:
                    self.TSLInput.setChecked(False)
                if server.get("streamSettings") is not None:
                    self.DownlinkCapacityInput.setText(
                        server["streamSettings"]["kcpSettings"][
                            "downlinkCapacity"])
                    self.UplinkCapacityInput.setText(
                        server["streamSettings"]["kcpSettings"][
                            "uplinkCapacity"])
                    self.ReadBufferInput.setText(
                        server["streamSettings"]["kcpSettings"][
                            "readBufferSize"])
                    self.WriteBufferInput.setText(
                        server["streamSettings"]["kcpSettings"][
                            "writeBufferSize"])
                    self.TtiInput.setText(
                        server["streamSettings"]["kcpSettings"][
                            "tti"])
                    self.MtuInput.setText(
                        server["streamSettings"]["kcpSettings"][
                            "mtu"])
                    if server["streamSettings"]["kcpSettings"][
                        "congestion"]:
                        self.CongestionInput.setCurrentIndex(1)
                    if server["streamSettings"]["kcpSettings"][
                        "header"]["type"] == "srtp":
                        self.HeaderTypeInput.setCurrentIndex(1)
                    elif server["streamSettings"]["kcpSettings"][
                        "header"]["type"] == "utp":
                        self.HeaderTypeInput.setCurrentIndex(2)
                    elif server["streamSettings"]["kcpSettings"][
                        "header"]["type"] == "wechat-video":
                        self.HeaderTypeInput.setCurrentIndex(3)
                    elif server["streamSettings"]["kcpSettings"][
                        "header"]["type"] == "dtls":
                        self.HeaderTypeInput.setCurrentIndex(4)

                    self.TCPHeaderInput.setPlainText(
                        str(server["streamSettings"]["tcpSettings"]))

                    self.WsPathInput.setText(
                        server["streamSettings"]["wsSettings"]["path"])
                    self.WsHeadersInput.setPlainText(
                        str(server["streamSettings"]["wsSettings"]["headers"]))

                    self.Http2HostInput.setText(",".join(
                        server["streamSettings"]["httpSettings"]["host"]))
                    self.Http2PathInput.setText(
                        server["streamSettings"]["httpSettings"]["path"])

    def showServerList(self):
        i = 0
        for server in self.servers:
            item = QListWidgetItem("{}".format(server["ps"]))
            self.listWidget.addItem(item)
            if i == 0:
                self.listWidget.setCurrentItem(item)
            i += 1
        self.showServerInfo(QListWidgetItem("{}".format(self.servers[0]["ps"])))
