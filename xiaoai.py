#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine import Pin,PWM
import utime
import dht

from Blinker.Blinker import Blinker, BlinkerButton, BlinkerNumber, BlinkerMiot
from Blinker.BlinkerConfig import *
from Blinker.BlinkerDebug import *

#from BlinkerAdapters.BlinkerWiFi import MQTTClients
     

#print(BlinkerAliGenie.payload)
# 此处填入blinker app中获取的密钥
auth = ''
ssid = 'wifi名称'
pswd = 'wifi密码'

BLINKER_DEBUG.debugAll()

Blinker.mode('BLINKER_WIFI')
#Blinker.aliType('BLINKER_ALIGENIE_LIGHT')
Blinker.miType('BLINKER_MIOT_LIGHT')
Blinker.begin(auth, ssid, pswd)

button1 = BlinkerButton('btn-abc')
number1 = BlinkerNumber('num-abc')
number2 = BlinkerNumber('num-jbe')
number3 = BlinkerNumber('num-f9t')

counter = 0
pinValue = 0
oState = 'on'
temp = 0
hum = 0

p2 = Pin(2, Pin.OUT)
p2.value(pinValue)


#s = PWM(Pin(15,Pin.OUT))
#s.freq(50)
def Servo(angle):
    #value =int(((angle) / 180*2 + 0.5) / 20 * 1023)
    value = int((angle-0)*(125-25)/(180-0) + 25)
    print("value:",value)
    s.duty(value)

#Servo(0)


d = dht.DHT11(Pin(15))
def heartbeat_callback():
    global temp,hum
    d.measure()
    temp = d.temperature() # eg. 23 (°C)
    hum = d.humidity()    # eg. 41 (% RH)
    print("温度",temp,"湿度:",hum)

    number2.print(temp)
    number3.print(hum)


def aligeniePowerState(state):
    global oState
    print("#"*8,state)
    BLINKER_LOG('need set power state: ', state)
    if state == BLINKER_CMD_ON:
        p2.value(1)
        #Servo(180)
        #utime.sleep(1)
        BlinkerAliGenie.powerState("on")
        BlinkerAliGenie.print()
        oState = 'on'
        print(BLINKER_CMD_ON,"aaaaaaa")
    elif state == BLINKER_CMD_OFF:
        p2.value(0)
        #Servo(0)
        #utime.sleep(1)
        BlinkerAliGenie.powerState("off")
        BlinkerAliGenie.print()
        oState = 'off'
        print(BLINKER_CMD_OFF,"sssssss")
        
def miotPowerState(state):
    global oState
    print("#"*8,state)
    BLINKER_LOG('need set power state: ', state)
    if state == BLINKER_CMD_ON:
        p2.value(1)
        #Servo(180)
        #utime.sleep(1)
        BlinkerMiot.powerState("on")
        BlinkerMiot.print()
        oState = 'on'
        print(BLINKER_CMD_ON,"aaaaaaa")
    elif state == BLINKER_CMD_OFF:
        p2.value(0)
        #Servo(0)
        #utime.sleep(1)
        BlinkerMiot.powerState("off")
        BlinkerMiot.print()
        oState = 'off'
        print(BLINKER_CMD_OFF,"sssssss")
    

def miotQuery(queryCode):

    global oState,temp,hum
    BLINKER_LOG('miQuery Query codes: ', queryCode,oState)
    print("*"*8,queryCode,BLINKER_CMD_QUERY_ALL_NUMBER)

    if queryCode == BLINKER_CMD_QUERY_ALL_NUMBER :
        BLINKER_LOG('miQuery Query All')
        BlinkerMiot.powerState(oState)
        BlinkerMiot.temp(temp)
        BlinkerMiot.humi(hum)
        BlinkerMiot.print()
    elif queryCode == BLINKER_CMD_QUERY_POWERSTATE_NUMBER :
        BLINKER_LOG('miQuery Query Power State')
        BlinkerMiot.powerState(oState)
        BlinkerMiot.print()
    elif queryCode == BLINKER_CMD_QUERY_TEMP_NUMBER:
        BlinkerMiot.temp(temp)
        print("temp:",temp)
        BlinkerMiot.print()
    elif queryCode == BLINKER_CMD_QUERY_HUMI_NUMBER:
        print("hum:",hum)
        BlinkerMiot.humi(hum)
        BlinkerMiot.print()
    else :
        BlinkerMiot.powerState(oState)
        BlinkerMiot.print()

def button1_callback(state):
    ''' '''
    print("&"*8)
    BLINKER_LOG('get button state: ', state)

    button1.icon('icon_1')
    button1.color('#FFFFFF')
    button1.text('Your button name or describe')
    button1.print(state)

    global pinValue

    pinValue = 1 - pinValue
    p2.value(pinValue)

def data_callback(data):
    global counter
    print("+"*8)
    BLINKER_LOG('Blinker readString: ', data)
    counter += 1
    number1.print(counter)
    
#print(Blinker.aliParse())
button1.attach(button1_callback)
Blinker.attachData(data_callback)
Blinker.attachHeartbeat(heartbeat_callback)

BlinkerMiot.attachPowerState(miotPowerState)
#BlinkerMiot.attachQuery(miotQuery)
#BlinkerAliGenie.attachColor(aligenieColor)
#BlinkerAliGenie.attachPowerState(aligeniePowerState)
#BlinkerAliGenie.attachQuery(aligenieQuery)

if __name__ == '__main__':
    #msg = MQTTClients()
    #msg = Blinker.aliParse()
    while True:
        Blinker.run()
        
