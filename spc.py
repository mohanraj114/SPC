import sys
from urllib.request import urlopen
import requests
import os
import serial
from threading import Thread
from collections import defaultdict
import time
from time import strftime
import datetime
import calendar
#import RPi.GPIO as pin
#pin.setmode(pin.BCM)
#pin.setup(18,pin.OUT)
import paho.mqtt.client as mqtt
import modbus_tk
import csv
from multiprocessing import Process, Queue
import modbus_tk.defines as cst
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
'''import logging
import subprocess
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)'''


#link_toSendUrl="http://www.flsevoii.com:3093/api/data?sid=0&"
link_toSendUrl="http://www.flsevoii.com:3093/api/data"
link_toGetUrl="http://www.flsevoii.com:3093/api/getdata?sid=0"
link_toFetchReqUrl="http://www.flsevoii.com:3093/api/FD?sid=0&"
link_toPostFetchUrl="http://www.flsevoii.com:3093/api/FDD/0"
link_toSendMasterurl="http://www.flsevoii.com:3093/api/MD?sid=0&"

eC=[1,2,4,8]
errorCode=[None]*len(eC)
for i in range (len(eC)):
    errorCode[i]=hex(eC[i])
porta='COM4'
baudratea= 9600
ID=1


#client = ModbusClient(method='rtu', port=porta,timeout=2, parity='E', stopbits=1, baudrate=9600, unit=1)
client = ModbusClient('localhost', port=502, timeout=1, parity='N', baudrate=9600, unit=1)

now = datetime.datetime.now()
sendTime = now.replace(hour=23, minute=45, second=0, microsecond=0)

def getmodbusData(rL):
    client.connect()
    rr = client.read_holding_registers(1, rL, unit=1)
    if not hasattr(rr,'registers'):
        print ('recurring---')
        time.sleep(4)
        getmodbusData(rL)
    client.close()
    return rr.registers

def bytes(num):
    return hex(num >> 8), hex(num & 0xFF)

def combine_Bytes(a,b):
    a=a.rstrip("L").lstrip("0x")
    b=b.rstrip("L").lstrip("0x")
    return a+b

def SEND_STREAMDATA(dataArray):
    valString="sid=0&"
    for i in range (len(dataArray)):
        valString=valString+"value"+str(i+1)+"="+str(dataArray[i])+"&"
    valString=valString[:-1]
    print (valString)
    r=requests.get(link_toSendUrl,valString)
    print(r.status_code, r.reason)

def SEND_SETTINGDATA(dataArray):
        hexsplit=[]
        hexf=[None]*len(fdataResp)
        for i in range (len(fdataResp)):
           hexf[i]=hex(fdataResp[i])
        for i in range (len(fdataResp)):
          if(i!=0):
              a,b=bytes(fdataResp[i])
              hexsplit.append(a)
              hexsplit.append(b)
          else:
              hexsplit.append(fdataResp[i])
        statusResp=[]
        i=0
        while (i <(len(hexsplit)-1)):
            if(i==8):
                statusResp.append(combine_Bytes(hexsplit[i],hexsplit[i+1]))
                i=i++1       
            else:
                statusResp.append(hexsplit[i])
                i=i+1
        Setting_urL=link_toPostFetchUrl+"0"
        for i in range(len(statusResp)):
            Setting_urL=Setting_urL+"/"+str(statusResp[i])
        u=requests.get(Setting_urL,"")
        return u.reason
    
def get_FetchReq():
    response=urlopen(link_toFetchReqUrl)
    response=response.read().decode('utf-8')
    return response

def get_SetDATA():
    response = urlopen(link_toGetUrl)
    response=response.read().decode('utf-8')
    vals_fromWeb=response.split(" ")
    return vals_fromWeb

def SEND_MASTERDATA(dataArray):
    valString="sid=0&"
    for i in range (len(dataArray)-8):
        valString=valString+"value"+str(i+1)+"="+str(dataArray[i])+"&"
    valString=valString[:-1]
    print (valString)
    r=requests.get(link_toSendUrl,valString)
    print(r.status_code, r.reason)
    return r.reason 
   
try:
    while True:
        dataResp=getmodbusData(9)
        print (dataResp)
        SEND_STREAMDATA(dataResp)
        print ('||||||||||||||||||||--------------------------')
        FReq=get_FetchReq()
        setVals=get_SetDATA()
        for i in range (len(setVals)):
            setVals[i]=int(setVals[i])
        writingSet=client.write_registers(1,setVals,unit=1)
        if (get_FetchReq() == 'FETCH'):
            fdataResp=getmodbusData(14)
            stResp=SEND_SETTINGDATA(fdataResp)
            masterSta=getmodbusData(16)
            MasterResp=SEND_MASTERDATA(masterSta)
            #print (writingSet)
            #print (setVals)
            print (fdataResp)
            print (stResp)
            print (masterSta)
            print (MasterResp)
        print ('Request Status----'+FReq)
           
except KeyboardInterrupt:
    client.close()

    '''
except serial.SerialException:
    os.system('python spc.py')
    
except ModbusIOException:
    os.system('python spc.py')'''
    
