try:
    import modules.urequests as requests
except ImportError:
    import requests
import ujson
import ntptime
import utime
import machine
from network import STA_IF, WLAN
from Blinker.BlinkerConfig import *
from Blinker.BlinkerDebug import *
# from client import HTTPConnection

class Protocol():
    def __init__(self):
        self.conType = "BLINKER_WIFI"
        self.proto1 = None
        self.proto2 = None
        self.conn1 = None
        self.conn2 = None
        # self.debug = BLINKER_DEBUG

        self.msgFrom = None
        self.msgBuf = None
        self.sendBuf = ''
        self.isFormat = False
        self.autoFormatFreshTime = millis()
        self.state = CONNECTING

        self.isAvail = False
        self.isRead = False

        self.isThreadStart = False
        self.thread = None

        self.Buttons = {}
        self.Sliders = {}
        self.Toggles = {}
        self.Numbers = {}
        self.Texts = {}
        self.Datas = {}

        self.dataTime = BLINKER_DATA_FREQ_TIME
        self.dataCount = 0
        self.dataTimes = 0
        self.dataTimesLimit = 0
        self.dataStorageFunc = None

        # self.Joystick = [BLINKER_JOYSTICK_VALUE_DEFAULT, BLINKER_JOYSTICK_VALUE_DEFAULT]
        self.Joystick = {}
        self.Ahrs = [0, 0, 0, False]
        self.GPS = ["0.000000", "0.000000"]
        self.RGB = {}

        self.dataFunc = None
        self.heartbeatFunc = None        
        self.summaryFunc = None

        self.aliType = None
        self.duerType = None
        self.miType = None

        self.aliPowerSrareFunc = None
        self.aliSetColorFunc = None
        self.aliSetModeFunc = None
        self.aliSetcModeFunc = None
        self.aliSetBrightFunc = None
        self.aliRelateBrightFunc = None
        self.aliSetColorTempFunc = None
        self.aliRelateColorTempFunc = None
        self.aliQueryFunc = None

        self.miotPowerSrareFunc = None
        self.miotSetColorFunc = None
        self.miotSetModeFunc = None
        self.miotSetcModeFunc = None
        self.miotSetBrightFunc = None
        self.miotRelateBrightFunc = None
        self.miotSetColorTempFunc = None
        self.miotRelateColorTempFunc = None
        self.miotQueryFunc = None
        
 

        self.ntpInit = False

bProto = Protocol()

wlan = WLAN(STA_IF)

class BlinkerMpy:
    def mode(self, setType = 'BLINKER_WIFI'):
        if setType == "BLINKER_BLE":
            bProto.conType = setType
            return
        elif setType == "BLINKER_MQTT" or setType == "BLINKER_WIFI":
            bProto.conType = "BLINKER_MQTT"
            BLINKER_LOG('MODE: BLINKER_WIFI')

            import BlinkerAdapters.BlinkerWiFi as bMQTT

            bProto.proto1 = bMQTT
            bProto.conn1 = bProto.proto1.MQTTClients()

    def aliType(self, _type):
        if _type == 'BLINKER_ALIGENIE_LIGHT':
            bProto.aliType = '&aliType=light'
        elif _type == 'BLINKER_ALIGENIE_OUTLET':
            bProto.aliType = '&aliType=outlet'
        elif _type == 'BLINKER_ALIGENIE_MULTI_OUTLET':
            bProto.aliType = '&aliType=multi_outlet'
        elif _type == 'BLINKER_ALIGENIE_SENSOR':
            bProto.aliType = '&aliType=sensor'
            
    def miType(self, _type):
        if _type == 'BLINKER_MIOT_LIGHT':
            bProto.miType = '&miType=light'
        elif _type == 'BLINKER_MIOT_OUTLET':
            bProto.miType = '&miType=outlet'
        elif _type == 'BLINKER_MIOT_MULTI_OUTLET':
            bProto.miType = '&miType=multi_outlet'
        elif _type == 'BLINKER_MIOT_SENSOR':
            bProto.miType = '&miType=sensor'

        
    def begin(self, auth = None, ssid = None, pswd = None):
        if bProto.conType == "BLINKER_BLE":
            BLINKER_LOG('MODE: BLINKER_BLE')
        elif bProto.conType == "BLINKER_MQTT":
            BLINKER_LOG('auth: ', auth)
            wlan.active(True)
            wlan.connect(ssid, pswd)
            
            bProto.conn1.start(auth, bProto.aliType,bProto.miType, bProto.duerType)

            time.sleep(10.0)

    def checkData(self):
        if bProto.conType == "BLINKER_BLE":
            # return
            bProto.state = bProto.proto1.bleProto.state
            if bProto.proto1.bleProto.isRead is True:
                bProto.msgBuf = bProto.proto1.bleProto.msgBuf
                bProto.isRead = True
                bProto.proto1.bleProto.isRead = False
                # BlinkerMpy.parse(self)
        elif bProto.conType == "BLINKER_MQTT":
            bProto.state = bProto.conn1.bmqtt.state
            # if bProto.proto2.wsProto.state is CONNECTED:
            #     bProto.state = bProto.proto2.wsProto.state
            if bProto.conn1.bmqtt.isRead is True:
                bProto.msgBuf = bProto.conn1.bmqtt.msgBuf
                bProto.msgFrom = "BLINKER_MQTT"
                bProto.isRead = True
                bProto.conn1.bmqtt.isRead = False
                BlinkerMpy.parse(self)
            if bProto.conn1.bmqtt.isAliRead is True:
                bProto.msgBuf = bProto.conn1.bmqtt.msgBuf
                bProto.conn1.bmqtt.isAliRead = False
                BlinkerMpy.aliParse(self)
            if bProto.conn1.bmqtt.isMiotRead is True:
                bProto.msgBuf = bProto.conn1.bmqtt.msgBuf
                bProto.conn1.bmqtt.isMiotRead = False
                BlinkerMpy.miotParse(self)
            if bProto.conn1.bmqtt.isDuerRead is True:
                bProto.msgBuf = bProto.conn1.bmqtt.msgBuf
                bProto.conn1.bmqtt.isDuerRead = False
                BlinkerMpy.duerParse(self)
            # if bProto.proto2.wsProto.isRead is True:
            #     bProto.msgBuf = str(bProto.proto2.wsProto.msgBuf)
            #     bProto.msgFrom = "BLINKER_WIFI"
            #     bProto.isRead = True
            #     bProto.proto2.wsProto.isRead = False
            #     BlinkerMpy.parse(self)
    
    def ntpInit(self):
        if bProto.ntpInit is False:
            time.sleep(5)
            if wlan.isconnected():
                try:
                    ntptime.settime()
                except:
                    print('sync time error, skip.')
                t = utime.time()
                tm = utime.localtime(t + 8 * 60 * 60)
                tm = tm[0:3] + (0,) + tm[3:6] + (0,)
                machine.RTC().datetime(tm)
                bProto.ntpInit = True
    
    def vibrate(self, time = 200):
        if time > 1000:
            time = 1000
        BlinkerMpy.print(self, BLINKER_CMD_VIBRATE, time)

    def time(self):
        if bProto.ntpInit is False:
            return millis()
        return time.time() - 8*60*60

    def second(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _second

    def minute(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _minute

    def hour(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _hour

    def mday(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _mday

    def wday(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _weekday

    def month(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _month

    def year(self):
        if bProto.ntpInit is False:
            return -1
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = utime.localtime()
        return _year

    def run(self):
        if wlan.isconnected():
            BlinkerMpy.ntpInit(self)
            bProto.conn1.connect()
        else:
            BLINKER_LOG('network disconnected')
            time.sleep(2.0)        
        BlinkerMpy.checkData(self)
        BlinkerMpy.checkAutoFormat(self)


    
    def checkLength(self, data):
        if len(data) > BLINKER_MAX_SEND_SIZE:
            BLINKER_ERR_LOG('SEND DATA BYTES MAX THAN LIMIT!')
            return False
        else:
            return True

    def _print(self, data):
        if BlinkerMpy.checkLength(self, data) is False:
            return
        
        if bProto.conType == "BLINKER_BLE":
            bProto.conn1.response(data)
        # elif bProto.conType == "BLINKER_WIFI":
        #     bProto.conn1.broadcast(data)
        elif bProto.conType == "BLINKER_MQTT" and bProto.msgFrom == "BLINKER_MQTT":
            if BLINKER_CMD_NOTICE in data:
                _state = True
            elif BLINKER_CMD_STATE in data:
                _state = True
            else:
                _state = False
            bProto.conn1.pub(data, _state)
        # elif bProto.conType == "BLINKER_MQTT" and bProto.msgFrom == "BLINKER_WIFI":
        #     bProto.conn2.broadcast(data)

        # BlinkerMpy._parse(self, data)

    def print(self, key, value = None, uint = None):

        if value is None:
            if bProto.isFormat:
                return
            data = str(key)
            BlinkerMpy._print(self, data)
        else:
            key = str(key)
            # if not uint is None:
            #     value = str(value) + str(uint)
            # data = json_encode(key, value)
            # data = {}
            if bProto.isFormat == False:
                bProto.isFormat = True
                bProto.autoFormatFreshTime = millis()
            
            if (millis() - bProto.autoFormatFreshTime) < 100 :
                bProto.autoFormatFreshTime = millis()

            buffer = {}

            if bProto.sendBuf is not '' :
                buffer = ujson.loads(bProto.sendBuf)
            buffer[key] = value
            bProto.sendBuf = ujson.dumps(buffer)
            # # bProto.sendBuf[key] = value

            # # BLINKER_LOG_ALL("key: ", key, ", value: ", bProto.sendBuf[key])
            BLINKER_LOG_ALL("sendBuf: ", bProto.sendBuf)

    def checkAutoFormat(self):
        if bProto.isFormat :
            if (millis() - bProto.autoFormatFreshTime) >= 100 :
                # payload = {}
                # for key in bProto.sendBuf :
                #     BLINKER_LOG_ALL(key, ", ", bProto.sendBuf[key])
                BLINKER_LOG_ALL("auto format: ", ujson.loads(bProto.sendBuf))
                BlinkerMpy._print(self, ujson.loads(bProto.sendBuf))
                bProto.sendBuf = ''
                bProto.isFormat = False

    def notify(self, msg):
        BlinkerMpy.print(self, BLINKER_CMD_NOTICE, msg)

    def connected(self):
        if bProto.state is CONNECTED:
            return True
        else:
            return False 

    def connect(self, timeout = BLINKER_STREAM_TIMEOUT):
        bProto.state = CONNECTING
        start_time = millis()
        while (millis() - start_time) < timeout:
            BlinkerMpy.run(self)
            if bProto.state is CONNECTED:
                return True
        return False

    def disconnect(self):
        bProto.state = DISCONNECTED

    def delay(self, ms):
        start = millis()
        time_run = 0
        while time_run < ms:
            BlinkerMpy.run(self)
            time_run = millis() - start

    def available(self):
        return bProto.isAvail

    def attachData(self, func):
        bProto.dataFunc = func

    def attachHeartbeat(self, func):
        bProto.heartbeatFunc = func

    def attachSummary(self, func):
        bProto.summaryFunc = func

    def readString(self):
        bProto.isRead = False
        bProto.isAvail = False
        return bProto.msgBuf

    def times(self):
        return millis()

    def aliParse(self):
        data = bProto.msgBuf
        print("ooooopppp",type(data),data)
        if not data:
            return
        try:
            data = ujson.loads(data)
            BLINKER_LOG(data)
            # if data.has_key('set'):
            if 'get' in data.keys():
                _num = 0
                if 'num' in data.keys():
                    _num = int(data['num'])
                data = data['get']
                if data == 'state':
                    if bProto.aliType == '&aliType=multi_outlet':
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_ALL_NUMBER, _num)
                    else :
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_ALL_NUMBER)
                elif data == 'pState':
                    if bProto.aliType == '&aliType=multi_outlet':
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_POWERSTATE_NUMBER, _num)
                    else :
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_POWERSTATE_NUMBER)
                elif data == 'col':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_COLOR_NUMBER)
                elif data == 'clr':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_COLOR_NUMBER)
                elif data == 'colTemp':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_COLORTEMP_NUMBER)
                elif data == 'bright':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_BRIGHTNESS_NUMBER)
                elif data == 'temp':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_TEMP_NUMBER)
                elif data == 'humi':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_HUMI_NUMBER)
                elif data == 'pm25':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_PM25_NUMBER)
                elif data == 'pState':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_POWERSTATE_NUMBER)
                elif data == 'mode':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_MODE_NUMBER)
            
            # elif data.has_key('get'):
            elif 'set' in data.keys():
                data = data['set']
                _num = 0
                if 'num' in data.keys():
                    _num = int(data['num'])
                for key, value in data.items():
                    if key == 'pState':
                        if bProto.aliPowerSrareFunc:
                            # if data.has_key('num'):                            
                            if bProto.aliType == '&aliType=multi_outlet':
                                bProto.aliPowerSrareFunc(value, _num)
                            else :
                                bProto.aliPowerSrareFunc(value)
                    elif key == 'col':
                        if bProto.aliSetColorFunc:
                            bProto.aliSetColorFunc(value)
                    elif key == 'clr':
                        if bProto.aliSetColorFunc:
                            bProto.aliSetColorFunc(value)
                    elif key == 'bright':
                        if bProto.aliSetBrightFunc:
                            bProto.aliSetBrightFunc(value)
                    elif key == 'upBright':
                        if bProto.aliRelateBrightFunc:
                            bProto.aliRelateBrightFunc(value)
                    elif key == 'downBright':
                        if bProto.aliRelateBrightFunc:
                            bProto.aliRelateBrightFunc(value)
                    elif key == 'colTemp':
                        if bProto.aliSetColorTempFunc:
                            bProto.aliSetColorTempFunc(value)
                    elif key == 'upColTemp':
                        if bProto.aliRelateColorTempFunc:
                            bProto.aliRelateColorTempFunc(value)
                    elif key == 'downColTemp':
                        if bProto.aliRelateColorTempFunc:
                            bProto.aliRelateColorTempFunc(value)
                    elif key == 'mode':
                        if bProto.aliSetModeFunc:
                            bProto.aliSetModeFunc(value)
                    elif key == 'cMode':
                        if bProto.aliSetcModeFunc:
                            bProto.aliSetcModeFunc(value)

        except ValueError:
            pass
        except TypeError:
            pass
        finally:
            pass
        
        
    def miotParse(self):
        data = bProto.msgBuf
        print("miotopppp",type(data),data)
        if not data:
            return
        try:
            data = ujson.loads(data)
            BLINKER_LOG(data)
            # if data.has_key('set'):
            if 'get' in data.keys():
                _num = 0
                if 'num' in data.keys():
                    _num = int(data['num'])
                data = data['get']
                print("statestatestate",data,BLINKER_CMD_QUERY_ALL_NUMBER)
                if data == 'state':
                    if bProto.miType == '&miType=multi_outlet':
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_ALL_NUMBER, _num)
                    else :
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_ALL_NUMBER)
                elif data == 'pState':
                    if bProto.miType == '&miType=multi_outlet':
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_POWERSTATE_NUMBER, _num)
                    else :
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_POWERSTATE_NUMBER)
                elif data == 'col':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_COLOR_NUMBER)
                elif data == 'clr':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_COLOR_NUMBER)
                elif data == 'colTemp':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_COLORTEMP_NUMBER)
                elif data == 'bright':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_BRIGHTNESS_NUMBER)
                elif data == 'temp':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_TEMP_NUMBER)
                elif data == 'humi':
                    if bProto.aliQueryFunc:
                        bProto.aliQueryFunc(BLINKER_CMD_QUERY_HUMI_NUMBER)
                elif data == 'pm25':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_PM25_NUMBER)
                elif data == 'pState':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_POWERSTATE_NUMBER)
                elif data == 'mode':
                    if bProto.miotQueryFunc:
                        bProto.miotQueryFunc(BLINKER_CMD_QUERY_MODE_NUMBER)
            
            # elif data.has_key('get'):
            elif 'set' in data.keys():
                data = data['set']
                _num = 0
                if 'num' in data.keys():
                    _num = int(data['num'])
                for key, value in data.items():
                    if key == 'pstate':
                        if bProto.miotPowerSrareFunc:
                            # if data.has_key('num'):                            
                            if bProto.miType == '&miType=multi_outlet':
                                bProto.miotPowerSrareFunc(value, _num)
                            else :
                                bProto.miotPowerSrareFunc(value)
                    elif key == 'col':
                        if bProto.miotSetColorFunc:
                            bProto.miotSetColorFunc(value)
                    elif key == 'clr':
                        if bProto.miotSetColorFunc:
                            bProto.miotSetColorFunc(value)
                    elif key == 'bright':
                        if bProto.miotSetBrightFunc:
                            bProto.miotSetBrightFunc(value)
                    elif key == 'upBright':
                        if bProto.miotRelateBrightFunc:
                            bProto.miotRelateBrightFunc(value)
                    elif key == 'downBright':
                        if bProto.miotRelateBrightFunc:
                            bProto.miotRelateBrightFunc(value)
                    elif key == 'colTemp':
                        if bProto.miotSetColorTempFunc:
                            bProto.miotSetColorTempFunc(value)
                    elif key == 'upColTemp':
                        if bProto.miotRelateColorTempFunc:
                            bProto.miotRelateColorTempFunc(value)
                    elif key == 'downColTemp':
                        if bProto.miotRelateColorTempFunc:
                            bProto.miotRelateColorTempFunc(value)
                    elif key == 'mode':
                        if bProto.miotSetModeFunc:
                            bProto.miotSetModeFunc(value)
                    elif key == 'cMode':
                        if bProto.miotSetcModeFunc:
                            bProto.miotSetcModeFunc(value)

        except ValueError:
            pass
        except TypeError:
            pass
        finally:
            pass


    def parse(self):
        data = bProto.msgBuf
        if not data:
            return
        try:
            data = ujson.loads(data)
            BLINKER_LOG(data)
            # if not isinstance(data, dict):
            #     raise TypeError()
            for key, value in data.items():
                if key in bProto.Buttons:
                    bProto.isRead = False
                    bProto.Buttons[key].func(data[key])
                elif key in bProto.Sliders:
                    bProto.isRead = False
                    bProto.Sliders[key].func(data[key])
                # elif key in bProto.Toggles:
                #     bProto.isRead = False
                #     bProto.Toggles[key].func(data[key])
                elif key in bProto.RGB:
                    bProto.isRead = False
                    BLINKER_LOG(bProto.RGB[key])
                    bProto.RGB[key].func(data[key][R], data[key][G], data[key][B], data[key][BR])
                elif key in bProto.Joystick:
                    bProto.isRead = False
                    bProto.Joystick[key].func(data[key][J_Xaxis], data[key][J_Yaxis])
                elif key == BLINKER_CMD_AHRS:
                    # bProto.isAvail = False
                    bProto.isRead = False
                    bProto.Ahrs[Yaw] = data[key][Yaw]
                    bProto.Ahrs[Pitch] = data[key][Pitch]
                    bProto.Ahrs[Roll] = data[key][Roll]
                    bProto.Ahrs[AHRS_state] = True
                    # BLINKER_LOG(bProto.Ahrs)
                elif key == BLINKER_CMD_GPS:
                    bProto.isRead = False
                    bProto.GPS[LONG] = str(data[key][LONG])
                    bProto.GPS[LAT] = str(data[key][LAT])

                elif key == BLINKER_CMD_GET and data[key] == BLINKER_CMD_VERSION:
                    bProto.isRead = False
                    BlinkerMpy.print(self, BLINKER_CMD_VERSION, BLINKER_VERSION)

                elif key == BLINKER_CMD_GET and data[key] == BLINKER_CMD_STATE:
                    bProto.isRead = False
                    BlinkerMpy.heartbeat(self)
        
        except ValueError:
            pass
        except TypeError:
            pass
        finally:
            if bProto.isRead:
                # bProto.isAvail = 
                if bProto.dataFunc :
                    bProto.dataFunc(data)
                # bProto.isAvail = False

    def heartbeat(self):
        if bProto.conType == 'BLINKER_MQTT':
            # beginFormat()
            BlinkerMpy.print(self, BLINKER_CMD_STATE, BLINKER_CMD_ONLINE)
            if bProto.heartbeatFunc :
                bProto.heartbeatFunc()
            if bProto.summaryFunc :
                bProto.summaryFunc()
            # stateData()
            # if endFormat() is False:
            #     print(BLINKER_CMD_STATE, BLINKER_CMD_ONLINE)
        else:
            # beginFormat()
            BlinkerMpy.print(self, BLINKER_CMD_STATE, BLINKER_CMD_CONNECTED)
            if bProto.heartbeatFunc :
                bProto.heartbeatFunc()
            if bProto.summaryFunc :
                bProto.summaryFunc()

    def sms(self, msg):
        if bProto.conType == "BLINKER_MQTT":
            bProto.conn1.sms(msg)
        else:
            BLINKER_ERR_LOG('This code is intended to run on the MQTT!')

    def push(self, msg):
        if bProto.conType == "BLINKER_MQTT":
            bProto.conn1.push(msg)
        else:
            BLINKER_ERR_LOG('This code is intended to run on the MQTT!')

    def wechat(self, title, state, msg):
        if bProto.conType == "BLINKER_MQTT":
            bProto.conn1.wechat(title, state, msg)
        else:
            BLINKER_ERR_LOG('This code is intended to run on the MQTT!')

    def weather(self, city = 'default'):
        if bProto.conType == "BLINKER_MQTT":
            return bProto.conn1.weather(city)
        else:
            BLINKER_ERR_LOG('This code is intended to run on the MQTT!')

    def aqi(self, city = 'default'):
        if bProto.conType == "BLINKER_MQTT":
            return bProto.conn1.aqi(city)
        else:
            BLINKER_ERR_LOG('This code is intended to run on the MQTT!')

    def attachAliGenieSetPowerState(self, _func):
        bProto.aliPowerSrareFunc = _func
    
    def attachAliGenieSetColor(self, _func):
        bProto.aliSetColorFunc = _func

    def attachAliGenieSetMode(self, _func):
        bProto.aliSetModeFunc = _func

    def attachAliGenieSetcMode(self, _func):
        bProto.aliSetcModeFunc = _func

    def attachAliGenieSetBrightness(self, _func):
        bProto.aliSetBrightFunc = _func

    def attachAliGenieRelativeBrightness(self, _func):
        bProto.aliRelateBrightFunc = _func

    def attachAliGenieSetColorTemperature(self, _func):
        bProto.aliSetColorTempFunc = _func

    def attachAliGenieRelativeColorTemperature(self, _func):
        bProto.aliRelateColorTempFunc = _func

    def attachAliGenieQuery(self, _func):
        bProto.aliQueryFunc = _func

    def aliPrint(self, data):
        bProto.conn1.aliPrint(data)
        
        
    def attachMiotSetPowerState(self, _func):
        bProto.miotPowerSrareFunc = _func
    
    def attachMiotSetColor(self, _func):
        bProto.miotSetColorFunc = _func

    def attachMiotSetMode(self, _func):
        bProto.miotSetModeFunc = _func

    def attachMiotSetcMode(self, _func):
        bProto.miotSetcModeFunc = _func

    def attachMiotSetBrightness(self, _func):
        bProto.miotSetBrightFunc = _func

    def attachMiotRelativeBrightness(self, _func):
        bProto.miotRelateBrightFunc = _func

    # def attachAliGenieSetColorTemperature(self, _func):
    #     bProto.aliSetColorTempFunc = _func

    # def attachAliGenieRelativeColorTemperature(self, _func):
    #     bProto.aliRelateColorTempFunc = _func

    def attachMiotQuery(self, _func):
        bProto.miotQueryFunc = _func

    def miotPrint(self, data):
        bProto.conn1.miotPrint(data)
        
 

Blinker = BlinkerMpy()

class BlinkerButton(object):
    """ """

    def __init__(self, name, func=None):
        self.name = name
        self.func = func
        self._icon = ""
        self.iconClr = ""
        self._content = ""
        self._text = ""
        self._text1 = ""
        self.textClr = ""
        self.buttonData = {}

        bProto.Buttons[name] = self

    def icon(self, _icon):
        self._icon = _icon

    def color(self, _clr):
        self.iconClr = _clr

    def content(self, _con):
        self._content = str(_con)

    def text(self, _text1, _text2=None):
        self._text = str(_text1)
        if _text2:
            self._text1 = str(_text2)

    def textColor(self, _clr):
        self.textClr = _clr

    def attach(self, func):
        self.func = func

    def print(self, state=None):

        if state :
            self.buttonData[BLINKER_CMD_SWITCH] = state
        if self._icon:
            self.buttonData[BLINKER_CMD_ICON] = self._icon
        if self.iconClr:
            self.buttonData[BLINKER_CMD_COLOR] = self.iconClr
        if self._content:
            self.buttonData[BLINKER_CMD_CONNECTED] = self._content
        if self._text:
            self.buttonData[BLINKER_CMD_TEXT] = self._text
        if self._text1:
            self.buttonData[BLINKER_CMD_TEXT1] = self._text1
        if self.textClr:
            self.buttonData[BLINKER_CMD_TEXTCOLOR] = self.textClr

        if len(self.buttonData) :
            # data = json.dumps(self.buttonData)
            # data = {self.name: self.buttonData}
            # Blinker._print(data)
            Blinker.print(self.name, self.buttonData)

            self.buttonData.clear()

            self._icon = ""
            self.iconClr = ""
            self._content = ""
            self._text = ""
            self._text1 = ""
            self.textClr = ""


class BlinkerNumber(object):
    """ """

    def __init__(self, name):
        self.name = name
        self._icon = ""
        self._color = ""
        self._unit = ""
        self._text = ""
        self.numberData = {}

        bProto.Numbers[name] = self

    def icon(self, _icon):
        self._icon = _icon

    def color(self, _clr):
        self._color = _clr

    def unit(self, _unit):
        self._unit = _unit
    
    def text(self, _text):
        self._text = _text

    def print(self, value = None):
        if value:
            self.numberData[BLINKER_CMD_VALUE] = value
        if self._icon:
            self.numberData[BLINKER_CMD_ICON] = self._icon
        if self._color:
            self.numberData[BLINKER_CMD_COLOR] = self._color
        if self._unit:
            self.numberData[BLINKER_CMD_UNIT] = self._unit
        if self._text:
            self.numberData[BLINKER_CMD_TEXT] = self._text

        if len(self.numberData) :
            # data = json.dumps(self.numberData)
            # data = {self.name: self.numberData}
            # Blinker._print(data)
            Blinker.print(self.name, self.numberData)

            self.numberData.clear()

            self._icon = ""
            self._color = ""
            self._unit = ""
            self._text = ""


class BlinkerRGB(object):
    """ """

    def __init__(self, name, func=None):
        self.name = name
        self.func = func
        self.rgbbrightness = 0
        self.rgbData = []
        self.registered = False

        bProto.RGB[name] = self

    def attach(self, func):
        self.func = func

    def brightness(self, _bright):
        self.rgbbrightness = _bright

    def print(self, r, g, b, _bright=None):
        self.rgbData.append(r)
        self.rgbData.append(g)
        self.rgbData.append(b)
        if _bright is None:
            self.rgbData.append(self.rgbbrightness)
        else:
            self.rgbData.append(_bright)
        
        # _print(self.rgbData)
        # data = {self.name: self.rgbData}
        # Blinker._print(data)
        Blinker.print(self.name, self.rgbData)


class BlinkerSlider(object):
    """ """

    def __init__(self, name, func=None):
        self.name = name
        self.func = func
        self.textClr = ""
        self.sliderData = {}

        bProto.Sliders[name] = self

    def attach(self, func):
        self.func = func

    def color(self, _clr):
        self.textClr = _clr

    def print(self, value):
        self.sliderData[BLINKER_CMD_VALUE] = value
        if self.textClr:
            self.sliderData[BLINKER_CMD_COLOR] = self.textClr

        # data = json.dumps(self.sliderData)
        # data = {self.name: self.sliderData}
        # Blinker._print(data)
        Blinker.print(self.name, self.sliderData)


class BlinkerText(object):
    """ """

    def __init__(self, name):
        self.name = name
        self.textData = {}

        bProto.Texts[name] = self

    def print(self, text1, text2=None):
        self.textData[BLINKER_CMD_TEXT] = text1
        if text2:
            self.textData[BLINKER_CMD_TEXT1] = text2

        # data = json.dumps(self.textData)        
        # data = {self.name: self.textData}
        # Blinker._print(data)
        Blinker.print(self.name, self.textData)


class BlinkerJoystick(object):
    """ """

    def __init__(self, name, func=None):
        self.name = name
        self.func = func

        bProto.Joystick[name] = self

    def attach(self, _func):
        self.func = _func


class BlinkerSwitch(object):
    """ """

    def __init__(self, name=BLINKER_CMD_BUILTIN_SWITCH, func=None):
        self.name = name
        self.func = func

        bProto.Toggles[name] = self

    def attach(self, _func):
        self.func = _func

    def print(self, _state):
        Blinker.print(self.name, _state)

BUILTIN_SWITCH = BlinkerSwitch()

class BLINKERA_LIGENIE():
    def __init__(self):
        self.payload = {}

    def attachPowerState(self, _func):
        Blinker.attachAliGenieSetPowerState(_func)

    def attachColor(self, _func):
        Blinker.attachAliGenieSetColor(_func)

    def attachMode(self, _func):
        Blinker.attachAliGenieSetMode(_func)

    def attachCancelMode(self, _func):
        Blinker.attachAliGenieSetcMode(_func)
    
    def attachBrightness(self, _func):
        Blinker.attachAliGenieSetBrightness(_func)

    def attachRelativeBrightness(self, _func):
        Blinker.attachAliGenieRelativeBrightness(_func)

    def attachColorTemperature(self, _func):
        Blinker.attachAliGenieSetColorTemperature(_func)

    def attachRelativeColorTemperature(self, _func):
        Blinker.attachAliGenieRelativeColorTemperature(_func)

    def attachQuery(self, _func):
        Blinker.attachAliGenieQuery(_func)

    def powerState(self, state, num = None):
        self.payload['pState'] = state
        if num :
            self.payload['num'] = num

    def color(self, clr):
        self.payload['clr'] = clr

    def mode(self, md):
        self.payload['mode'] = md

    def colorTemp(self, clrTemp):
        self.payload['colTemp'] = clrTemp

    def brightness(self, bright):
        self.payload['bright'] = bright

    def temp(self, tem):
        self.payload['temp'] = tem

    def humi(self, hum):
        self.payload['humi'] = hum

    def pm25(self, pm):
        self.payload['pm25'] = pm

    def print(self):
        BLINKER_LOG_ALL(self.payload)
        Blinker.aliPrint(self.payload)
        self.payload.clear()

BlinkerAliGenie = BLINKERA_LIGENIE()


class BLINKERA_MIOT():
    def __init__(self):
        self.payload = {}

    def attachPowerState(self, _func):
        Blinker.attachMiotSetPowerState(_func)

    def attachColor(self, _func):
        Blinker.attachMiotSetColor(_func)

    def attachMode(self, _func):
        Blinker.attachMiotSetMode(_func)

    def attachCancelMode(self, _func):
        Blinker.attachMiotSetcMode(_func)
    
    def attachBrightness(self, _func):
        Blinker.attachMiotSetBrightness(_func)

    def attachRelativeBrightness(self, _func):
        Blinker.attachMiotRelativeBrightness(_func)

    def attachColorTemperature(self, _func):
        Blinker.attachMiotSetColorTemperature(_func)

    def attachRelativeColorTemperature(self, _func):
        Blinker.attachMiotRelativeColorTemperature(_func)

    def attachQuery(self, _func):
        Blinker.attachMiotQuery(_func)

    def powerState(self, state, num = None):
        self.payload['pstate'] = state
        if num :
            self.payload['num'] = num

    def color(self, clr):
        self.payload['clr'] = clr

    def mode(self, md):
        self.payload['mode'] = md

    def colorTemp(self, clrTemp):
        self.payload['colTemp'] = clrTemp

    def brightness(self, bright):
        self.payload['bright'] = bright

    def temp(self, tem):
        self.payload['temp'] = tem

    def humi(self, hum):
        self.payload['humi'] = hum

    def pm25(self, pm):
        self.payload['pm25'] = pm

    def print(self):
        BLINKER_LOG_ALL(self.payload)
        Blinker.miotPrint(self.payload)
        self.payload.clear()

BlinkerMiot= BLINKERA_MIOT()


