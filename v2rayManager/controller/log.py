import time
import json
import sys, os


class log():
    def __init__(self):
        with open("../config/manager.json", 'r') as f:
            self.config = json.load(f)
        self.logPath = self.config["log path"]
        #print(self.logPath)

    def log(self, message):
        if not os.path.isfile(self.logPath):
            open(self.logPath, "w").close()
        with open(self.logPath, 'w') as f:
            f.write("{} {}".format(time.asctime(time.localtime(time.time())),
                                   message))
