import sys
from random import randint
import os
import serial
from threading import Thread
from collections import defaultdict
import time
from time import strftime
import datetime
import calendar
import paho.mqtt.client as mqtt
#import modbus_tk
import  Adafruit_ADS1x15
import csv
from multiprocessing import Process, Queue
#import modbus_tk.defines as cst
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
#from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import logging
import subprocess
#os.system('python home/pi/Test/onmcu.py')
#time.sleep(5)
#os.system('sudo wvdial 3gconnect')
#time.sleep(5)
#logging.basicConfig()
speP='CM/SPEPARAM/183000002'
stdP='CM/STDPARAM/18300002'
porta='/dev/ttyUSB0'
baudratea=9600
ID=1
broker="tmqtt.venaqua.com"
mqPort=1883
adc = Adafruit_ADS1x15.ADS1015()
testVal=[8654,7456,8965,4587,4526,3657,4519,6542,12785,10245,12763,1265,4756,8653,7586,12456,1234]
mclient=mqtt.Client("tx")
mclient.username_pw_set("tuser","123456")
#mclient.connect(broker,mqPort)
#mclient.username_pw_set("tuser","123456")
adc = Adafruit_ADS1x15.ADS1015()
client=ModbusClient(method='rtu', port=porta, timeout=1, parity='E', bytesize=8 ,stopbits= 1 ,baudrate=9600, unit=1)
#client=ModbusClient('ip',port= 'a',timeout=1, parity='E', baudrate=baudratea,unit=1)
def get_FromConfig(param):
        with open ('/home/pi/Compressor/con1.csv','rU') as infile:
                reader=csv.DictReader(infile)
                data={}
                for row in reader:
                        for header,value in row.items():
                                try:
                                        data[header].append(value)
                                except KeyError:
                                        data[header]=[value]
        return data[param]

def on_connect(client, userdata, flags, rc):
 #    logging.info("Connected flags"+str(flags)+"result code "\
  #   +str(rc)+"client1_id ")
     client.connected_flag=True

def getmodbusData(sa):
        rr=client.read_holding_registers(sa,2,unit=1)
        return rr.registers[0]

def transmit_MQTT(data):
        eTime=calendar.timegm(time.gmtime())
        mclient.connect(broker,mqPort)
        for i in range (len(data)):
                topic=str(topics[i])
                print 'Transmitting................///'+str(data)+"=="+str(topic)+"====="+str(i)
                #fiData=str(data[i])+':'+str(eTime)
                fiData=str(data[i])
                mclient.publish(topic,fiData)
        mclient.disconnect()
def logToCSV(Dresponse):
        store_Data=(str(Dresponse))[1:-1]
        t_Date=datetime.datetime.today().strftime('%d-%m-%Y')
        file_Name="/home/pi/Compressor/DataLog/"+t_Date+"_Log.csv"
        with open(file_Name,"a") as dataLog:
                dataLog.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(store_Data)))
a=True
mclient.on_connect= on_connect

try:
        topics=get_FromConfig('SENSOR UNIQUE')
        print topics
        addresses=get_FromConfig('ADDRESS')
        #mclient.connect(broker,mqPort)
        #addresses=[3057]
        Adr=[]
        for i in range (len(addresses)-1):
                if(addresses[i] != 'None'):
                        adr=addresses[i].split(',')
                        print adr
                        for j in range (len(adr)):
                                adr[j]=int(adr[j]) #%100
                        Adr.append(adr)
        print  (Adr)
        past_Data=[None]*len_T
        while a==True:
                #mclient.connect(broker,mqPort)
                #cur_Data=[None]*len_T
                #client.connect()
                cur_Data=[]
                count=0
                #os.system('python home/pi/Test/onmcu.py')
                for i in range (len(Adr)):
                        tempD=[]
                        for j in range (len(Adr[i])):
                                Resval=getmodbusData(int(Adr[i][count]))
                                print (Resval)
                                #Resval=(hex(testVal[count])[2:].upper())
                                tempD.append(Resval)
                                count=count+1
                                time.sleep(1)
                        tempD=','.join(map(str, tempD))
                        cur_Data.append(tempD)
                pressure=adc.read_adc(0, gain=2)        #randint(0,1024)
                kwh=getmodbusData(2699)
                speVals=[]
                speVals.append(kwh)
                speVals.append(pressure)
                speVals=','.join(map(str,speVals))
                cur_Data.append(speVals)
                os.system('echo '+ str(cur_Data))
                transmit_MQTT(cur_Data)
                '''for i in range (len(cur_Data)):
                        if past_Data[i]!=cur_Data[i]:
                                writeFlag=1
                                #transmit_MQTT(cur_Data[i],i)
                                past_Data[i]=cur_Data[i]
                        elif not past_Data:
                                past_Data[i]=cur_Data[i]
                if writeFlag==1:
                        logToCSV(cur_Data)
                        writeFlag=0'''
                #client.close()
except KeyboardInterrupt:
        print ('Quitting...')
        client.close()
        mclient.disconnect()
'''except ModbusIOException:
        client.close()
'''
