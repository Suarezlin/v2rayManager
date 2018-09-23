from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QSystemTrayIcon, QAction, QApplication, QMenu, \
    QMessageBox, QWidget, QHBoxLayout, QMainWindow
import os
import sys, json
from ProcessServers import ProcessServers
from SwitchV2ray import SwitchV2ray
import threading
import Ping
import threading, re, prettytable
from scanServer import ScanServer
sys.path.append("../view")
from ServerConfigController import ServerConfigView



# lib_path = os.path.abspath(os.path.join('..'))
# sys.path.append(lib_path)

from resource import source


class SystemTray(QWidget):

    def __init__(self, parent=None):
        super(SystemTray, self).__init__(parent)
        with open("../config/manager.json", 'r') as f:
            self.config = json.load(f)
        with open("../config/Servers.json", 'r') as f:
            self.s = json.load(f)
        self.lock = threading.Lock()
        self.createActions()
        self.createTrayIcon()
        self.trayIcon.show()
        self.setWindowIcon(QIcon(':pic/pic/v2rayIcon.png'))

    def getV2rayStatu(self):
        cmd = '''export PATH=${PATH}:/usr/local/bin/
        supervisorctl status'''
        result = list(os.popen(cmd))[0]
        if "RUNNING" in result:
            return True
        else:
            return False

    def switchV2ray(self):
        switch = SwitchV2ray()
        if self.getV2rayStatu():
            switch.turnV2rayOff()
            if not self.getV2rayStatu():
                self.infoAction.setText("v2ray: off")
                self.switchAction.setText("开启 v2ray")
                self.showMessage("关闭 v2ray 成功", "当前 v2ray 服务已关闭", 5)
        else:
            switch.turnV2rayOn()
            if self.getV2rayStatu():
                self.infoAction.setText("v2ray: on")
                self.switchAction.setText("关闭 v2ray")
                self.showMessage("开启 v2ray 成功", "当前服务器: {}".format(
                    self.config["server"]["ps"]), 5)

    def threadChange(self, i, sender):
        if not self.getV2rayStatu():
            return
        switch = SwitchV2ray()
        result = switch.changeServer(i)
        with open("../config/manager.json", 'r') as f:
            self.config = json.load(f)
        if result:
            self.infoAction.setText("v2ray: on")
            self.switchAction.setText("关闭 v2ray")
        sender.setChecked(True)
        self.showMessage("切换服务器成功",
                         "当前服务器: {}".format(self.config["server"]["ps"]), 5)

    def changeServer(self):
        for action in self.servers.actions():
            if action.isChecked():
                action.setChecked(False)
        i = int(self.sender().text().split('-')[0]) - 1
        t = threading.Thread(target=self.threadChange, args=[i, self.sender()])
        t.start()

    def threadChangeRule(self, sender):
        if not self.getV2rayStatu():
            return
        switch = SwitchV2ray()
        if sender.text() == "智能 rule 模式":
            self.turnGlobalOnAction.setChecked(False)
            result = switch.switchRule()
            with open("../config/manager.json", 'r') as f:
                self.config = json.load(f)
            if result:
                self.showMessage("切换 Rule 模式成功", "当前服务器: {}".format(
                    self.config["server"]["ps"]), 5)
        else:
            self.turnRuleOnAction.setChecked(False)
            result = switch.switchGlobal()
            with open("../config/manager.json", 'r') as f:
                self.config = json.load(f)
            if result:
                self.showMessage("切换全局模式成功", "当前服务器: {}".format(
                    self.config["server"]["ps"]), 5)

    def changeRule(self):
        sender = self.sender()
        t = threading.Thread(target=self.threadChangeRule, args=[sender])
        t.start()

    def showMessage(self, title, body, duration):
        self.trayIcon.showMessage(title, body, QIcon(':pic/pic/v2rayIcon.png'),
                                  duration * 1000)

    def Tcp(self, tb, server, i):
        ping = Ping.Ping(server["add"], int(server["port"]))
        ping.ping(5)
        time = ping.delay
        if time == "0.00ms":
            time = "连接超时"
        self.lock.acquire()
        try:
            tb.field_names = ["i", "server", "delay"]
            tb.set_style(prettytable.PLAIN_COLUMNS)
            tb.add_row([i, self.servers.actions()[i].text(), time])
            tb.align = "l"
        except:
            pass
        finally:
            self.lock.release()

    def completeScan(self):
        #print("complete")
        self.tb.sortby = "i"
        self.tb.align["server"] = 'l'
        self.tb.align["      delay"] = 'c'
        self.tb.right_padding_width = 0

        s = self.tb.get_string(fields=["server", "      delay"]).split("\n")[1:]
        #print(s)
        i = 0
        for item in s:
            self.servers.actions()[i].setText(item)
            i += 1


    def threadScanServer(self):
        self.tb = prettytable.PrettyTable()
        self.tb.align = "l"
        self.tb.field_names = ["i", "server", "      delay"]
        self.tb.set_style(prettytable.PLAIN_COLUMNS)
        scan = ScanServer(self.s, self.tb)
        scan.start()
        scan.finished.connect(self.completeScan)
        
    def configServers(self):
        # self.configServer.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.configServer.setFocus()
        self.configServer.show()

    def createActions(self):

        self.infoAction = QAction("v2ray: off", self, enabled=False)
        self.switchAction = QAction("开启 v2ray", self,
                                    triggered=self.switchV2ray)
        if self.getV2rayStatu():
            self.infoAction.setText("v2ray: on")
            self.switchAction.setText("关闭 v2ray")

        self.turnRuleOnAction = QAction("智能 rule 模式", self, checkable=True,
                                        triggered=self.changeRule)
        self.turnGlobalOnAction = QAction("全局模式", self, checkable=True,
                                          triggered=self.changeRule)
        if self.config["mode"] == "rule":
            self.turnRuleOnAction.setChecked(True)
        else:
            self.turnGlobalOnAction.setChecked(True)

        self.proxySettings = QMenu(self)
        self.proxySettings.setTitle("代理设置")
        self.editUserRuleAction = QAction("用户自定规则", self)
        self.proxySettingsAction = QAction("代理设置", self)
        self.proxySettings.addAction(self.editUserRuleAction)
        self.proxySettings.addAction(self.proxySettingsAction)

        self.servers = QMenu(self)
        self.servers.setTitle("服务器")
        p = ProcessServers()
        p.getServerLists()
        serverList = p.serverList
        i = 0
        current = self.config["server"]["ps"]
        for server in serverList:
            action = QAction(server, self, checkable=True,
                             triggered=self.changeServer)
            # hLayout = QHBoxLayout()
            font = QFont()
            font.setFamily("Menlo")
            font.setBold(True)
            font.setWeight(75)
            font.setPointSize(10)
            action.setFont(font)
            self.servers.addAction(action)
            if "-".join(server.split("-")[1:]) == current:
                action.setChecked(True)
            i += 1

        self.serversScanAction = QAction("服务器测速", self,
                                         triggered=self.threadScanServer)
        self.serverConfigAction = QAction("服务器设置", self, triggered=self.configServers)
        self.configServer = ServerConfigView()
        self.seniorSettingsAction = QAction("高级设置", self)
        self.httpProxySettingsAction = QAction("HTTP 代理设置", self)
        self.autoConnectAction = QAction("打开时自动连接", self, checkable=True)

        self.showLogAction = QAction("显示日志", self)
        self.feedBackAction = QAction("反馈", self)
        self.aboutAction = QAction("关于", self)

        self.quitAction = QAction("退出", self,
                                  triggered=QApplication.instance().quit)
        self.quitAction.setShortcut("Ctrl+Q")

    def createTrayIcon(self):
        self.trayMenu = QMenu(self)
        self.trayMenu.addAction(self.infoAction)
        self.trayMenu.addAction(self.switchAction)

        self.trayMenu.addSeparator()

        self.trayMenu.addAction(self.turnRuleOnAction)
        self.trayMenu.addAction(self.turnGlobalOnAction)
        self.trayMenu.addMenu(self.proxySettings)

        self.trayMenu.addSeparator()

        self.trayMenu.addMenu(self.servers)
        self.trayMenu.addAction(self.serversScanAction)
        self.trayMenu.addAction(self.serverConfigAction)
        self.trayMenu.addAction(self.seniorSettingsAction)
        self.trayMenu.addAction(self.httpProxySettingsAction)
        self.trayMenu.addAction(self.autoConnectAction)

        self.trayMenu.addSeparator()

        self.trayMenu.addAction(self.showLogAction)
        self.trayMenu.addAction(self.feedBackAction)
        self.trayMenu.addAction(self.aboutAction)

        self.trayMenu.addSeparator()

        self.trayMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.setIcon(QIcon(':pic/pic/v2rayIcon.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    import AppKit

    NSApplicationActivationPolicyRegular = 0
    NSApplicationActivationPolicyAccessory = 1
    NSApplicationActivationPolicyProhibited = 2
    AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
    tray = SystemTray()
    QApplication.setQuitOnLastWindowClosed(False)
    # window.show()
    sys.exit(app.exec_())
