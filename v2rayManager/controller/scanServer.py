import Ping
import prettytable, time
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

class ScanServer(QThread):
    trigger = pyqtSignal()
    def __init__(self, s, tb, parent=None):
        super(ScanServer, self).__init__(parent)
        self.s = s
        self.tb = tb
        self.count = 0
        self.sum = len(s)

    def __del__(self):
        self.wait()

    def run(self):
        i = 0
        threads = []
        #print("ScanServer Run")
        # tb.align = "l"
        # tb.set_style(prettytable.PLAIN_COLUMNS)
        for server in self.s:
            t = Tcp(server, i, self.tb)
            threads.append(t)
            i += 1
        for t in threads:
            t.start()
            #t.trigger.connect(self.processTCP)
        for t in threads:
            t.wait()
        self.trigger.emit()

    def processTCP(self):
        self.count += 1
        print(self.count, len(self.s))
        if self.count == self.sum:
            self.trigger.emit()
            self.quit()

class Tcp(QThread):
    trigger = pyqtSignal()
    def __init__(self, server, i, tb, parent=None):
        super(Tcp, self).__init__(parent)
        self.server = server
        self.i = i
        self.tb = tb
        self.lock = QMutex()

    # def __del__(self):
    #     self.wait()

    def run(self):
        # 处理你要做的业务逻辑，这里是通过一个回调来处理数据，这里的逻辑处理写自己的方法
        # wechat.start_auto(self.callback)
        # self._signal.emit(msg);  可以在这里写信号焕发
        # self._signal.emit(msg)
        ping = Ping.Ping(self.server["add"], int(self.server["port"]))
        ping.ping(5)
        time = ping.delay
        if time == "0.00ms":
            time = "连接超时"
        self.lock.lock()
        try:
            self.tb.add_row([self.i, str(self.i + 1) + "-" + self.server["ps"], time])
        except:
            pass
        finally:
            self.lock.unlock()
            self.trigger.emit()

    def callback(self, msg):
        # 信号焕发，我是通过我封装类的回调来发起的
        # self._signal.emit(msg)
        pass
