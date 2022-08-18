from BlinkerUtility.BlinkerUtility import *

class BlinkerDebug():
    def __init__(self):
        self.isDebug = False
        self.isDebugAll = False

    def debug(self):
        self.isDebug = True
        self.isDebugAll = False

    def debugAll(self):
        self.isDebug = True
        self.isDebugAll = True

BLINKER_DEBUG = BlinkerDebug()

def BLINKER_LOG(arg1, *vartuple):
    # timeInfo = time.strftime("%H:%M:%S %Y", time.localtime())
    if BLINKER_DEBUG.isDebug == False :
        return

    data = str(arg1)
    for var in vartuple:
        data = data + str(var)
    data = '[' + str(millis()) + '] ' + data
    print("????????")
    print(data)

def BLINKER_ERR_LOG(arg1, *vartuple):
    # timeInfo = time.strftime("%H:%M:%S %Y", time.localtime())
    if BLINKER_DEBUG.isDebug == False :
        return

    data = str(arg1)
    for var in vartuple:
        data = data + str(var)
    data = '[' + str(millis()) + '] Error: ' + data
    print("/////////")
    print(data)
    
def BLINKER_LOG_ALL(arg1, *vartuple):
    # timeInfo = time.strftime("%H:%M:%S %Y", time.localtime())
    if BLINKER_DEBUG.isDebugAll == False :
        return
        
    data = str(arg1)
    for var in vartuple:
        data = data + str(var)
    data = '[' + str(millis()) + '] ' + data
    print("\\\\\\\\")
    print(data)

def BLINKER_ERR_LOG_ALL(arg1, *vartuple):
    # timeInfo = time.strftime("%H:%M:%S %Y", time.localtime())
    if BLINKER_DEBUG.isDebugAll == False :
        return
        
    data = str(arg1)
    for var in vartuple:
        data = data + str(var)
    data = '[' + str(millis()) + '] Error: ' + data
    print(data)
