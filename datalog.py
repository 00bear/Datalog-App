#!/usr/bin/python3
import requests
import urllib.parse

from time import strftime
import time

import serial

import RPi.GPIO as GPIO
from threading import Thread, Event

port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=3)

temp_sensor_path = '/sys/bus/w1/devices/28-020791774287/w1_slave'

#defining specefic user id for a device
uID = 1

enableMotion=True
enableButtons=False
motion_pin = 11
#motion_pin = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

motion_detected = False # flag that is set to True if motion is currently being detected
waiting_for_motion = False # flag is set to True if motion hasn't occured yet within a loop iteration
relay=[18,13,15,16]  #GPIO List
buttons=[22,24,26,32]
GPIO.setup(motion_pin,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(relay[0],GPIO.OUT)
GPIO.setup(relay[1],GPIO.OUT)
GPIO.setup(relay[2],GPIO.OUT)
GPIO.setup(relay[3],GPIO.OUT)
GPIO.setup(buttons[0],GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(buttons[1],GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(buttons[2],GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(buttons[3],GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#GPIO.setup(sensor_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

GPIO.output(relay[0],0)
GPIO.output(relay[1],0)
GPIO.output(relay[2],0)
GPIO.output(relay[3],0)


relayState=[0,0,0,0]


class Command(object):
  """Command object allows executon of commands that are sent to the GPRS module.

  cmd_text: text to send to the module
  error_message: printed message in case there is an exception raised
  success_message: shown when the command succeeds, written in terms of execution result
  error_value: value returned in case the module returns ERROR
  exception_value: value returned in case that an exception was raised
  errback: function called to check for aditional errors - Command object passed as argument
  waitintg_time: time waited for after command execution

  """
  def __init__(self, cmd_text, error_message, success_message = "{result}", error_value = -1, exception_value = 20, errback = None, waiting_time = 0):
    self.cmd_text = cmd_text
    self.error_message = error_message
    self.success_message = success_message
    self.error_value = error_value
    self.exception_value = exception_value
    self.failed = False
    self.errback = errback
    self.waiting_time = waiting_time

  def execute(self):
    try:
      self.result = execute(self.cmd_text)

      print(self.success_message.format(result=self.result))

      if self.errback:
        self.errback(self)

      if "ERROR" in self.result:
        close_all()
        self.failed = True
        self.failure_value = self.error_value
    except Exception as e:
      print(e)
      print(self.error_message)
      self.failed = True
      self.failure_value = self.exception_value

    if self.waiting_time > 0:
      time.sleep(self.waiting_time)


def relayHandle(id,onoff):
    global relay

    if (onoff==0):

        GPIO.output(relay[id],0)

    elif(onoff==1):
        GPIO.output(relay[id],1)

def c2f(temp_cel):

    return ((temp_cel * 9/5) + 32)

def execute(cmd):
    

    global port
    try:
        msg = (cmd + '\r').encode()

        port.write(msg)

        result = port.read(1000).decode()

        return result
    except:
        print('error.........')
        return 20


def close_all():

  try:
    
    cmd = "AT+CDSCB"

    #result = execute(cmd)

    print(result)
  except:
    print("module Close Error")
    return 20

  try:
    cmd = "AT+SAPBR=0,1"

    result = execute(cmd)

    print(result)
  except:
    print("GPRS disable Error")
    return 20

    #port.close()

##    if "ERROR" in result:
##        
##
##        close_all()
##
##    return -1

def tempRead():

  '''

  read temperature of system and return in fahrenheit formate

  '''

  global temp_sensor_path



  print('Reading temperature....')

  f = open(temp_sensor_path, 'r')

  lines = f.readlines()

  f.close()



  temp_output = lines[1].find("t=")



  if temp_output != -1:

    temp_string = lines[1].strip()[temp_output+2:]

    temp_c = float(temp_string)/1000.0

    temp_round = round(temp_c,1)

    f_temp = c2f(temp_round)

    print("Temperature: ", f_temp, " *F")



  else:

    print("Temperature not available")

    f_temp = -1



  return f_temp

def dateRead():
  """Read current date"""
  date = strftime("%Y-%m-%d ") + strftime("%H:%M:%S")
  print("Date: ", date)
  return date


def powerOnGps():

  print('Starting GPS first Time..........')
  try:
    cmd = "AT+CGNSPWR=1"
    result = execute(cmd)

    print(result)

    if "ERROR" in result:
      close_all()
      return -1
  except:
    print("GPS power on Error")
    return 20


def read_gps(firsttime):


  try:
    cmd = "AT+CGNSSEQ=\"RMC\""

    result = execute(cmd)

    print(result)

    if "ERROR" in result:


      close_all()

      return -1
  except:
    print("GPS sequence set Error")
    return 20
  
  time.sleep(0.3)

  try:
    cmd = "AT+CGNSINF"

    
    x=True
    while x==True:
        try:
            result = execute(cmd)
            print('result',result)
            data = result.split(':')[1]
            print('data',data)
            split_data = data.split(',') 
            print('split_data',split_data)           
            lng = split_data[4]
            
            lat = split_data[3]
            print('lat :', str(lat))
            print('lng :', str(lng))
            return (lng,lat)
        except IndexError:
            print('error ...')
            continue
        else:
            x=False
  except:
    print("GPS location Error")
    return 20

def init_Gprs():
  def net_errback(obj):
    obj.failed = True
    if(len(obj.result) >= 22):
      obj.failure_value = 20
      if(obj.result[20] == '3'):
        print("REGISTRATION DENIED "+obj.result)
      elif(obj.result[20] == '0'):
        print("No Network Found "+obj.result)
      elif(obj.result[20] == '2'):
        print("Network Not Registered "+obj.result)
      else:
        obj.failed = False
    else:
      obj.failure_value = -1

  print('GPRS initial INIT.........')

  test_power = Command("AT", 'No AT Response Check Power.', exception_value = -1)
  test_net = Command("AT+CREG?", "Sim Registration Error", "IS internet On #{result}#", errback = net_errback, waiting_time = 2)
  conf_contype = Command("AT+SAPBR=3,1,\"contype\",\"GPRS\"", "GPRS conType Error", waiting_time = 2)
  conf_apn = Command("AT+SAPBR=3,1,\"APN\",\"simple\"", "Apn Error", waiting_time = 2)
  open_ctx = Command("AT+SAPBR=1,1", "GPRS Context Error", "is GPRS OK {result}", error_value = -12, waiting_time = 5)
  query_ctx = Command("AT+SAPBR=2,1", "GPRS params Error", "is params ok {result}", waiting_time = 5)
  #init_http = Command("AT+HTTPINIT", "Already running Error", "Init HTTP {result}")

  for command in [test_power, test_net, conf_contype, conf_apn, open_ctx, query_ctx]:
    command.execute()
    if command.failed:
      return command.failure_value

  return 200


def getDataBytes(st):
   
   return len(st.encode('utf-8'))

def get_url(temp, date, lng, lat, motion):
  qdict = url = {
    'datetime': date,
    'temprature': temp,
    'latitude': lat,
    'longitude': lng,
    'motion': motion,
    'userId': uID
    }

  base = "http://www.cleartemp.site/datalog/savedatalog.php?"
  qstring = urllib.parse.urlencode(qdict)
  return base + qstring

def send_gsm(temp, date, lng, lat):
  global motion_detected, uID, waiting_for_motion
  
  dataStr = ""
  print('GPRS Data Execution.........')

  try:
    cmd = "AT+HTTPINIT"

    result = execute(cmd)
    #result = "HTTP"
    print("Init HTTP "+"Show ip addr")
    #Init HTTP ,,10,9,,,38,,
  except:
    print("Already Running "+"Inited")
  #if "ERROR" in result:

    #close_all()

    #return -1

  time.sleep(1)


  try:
    cmd = "AT+HTTPPARA=\"CID\",1"
            
    result = execute(cmd)
            
    print("end PARA "+result)
             
    if "ERROR" in result:
            
       close_all()
            
       return -1
  except:
    print("CID error")
    return 20

  time.sleep(2)

  motion = 0 if waiting_for_motion else 1
  waiting_for_motion = True if enableMotion and not motion_detected else False
  print('waiting_for_motion set to', waiting_for_motion)
  
  try:
     #cmd = "AT+HTTPPARA=\"URL\",\"http://hologram.io/test.html"
     # no network response from hologram io test
     
     cmd = 'AT+HTTPPARA="URL","' + get_url(temp, date, lng, lat, motion) + '"'
     #cmd = "AT+HTTPPARA=\"URL\",\""
     dataStr += "datetime="+str(date)
     dataStr += "temprature="+str(temp)
     dataStr += "latitude="+str(lat)
     dataStr += "longitude="+str(lng)
     dataStr += "motion="+str(motion)
     dataStr += "userId="+str(uID)
     print('cmd=======',cmd)
     result = execute(cmd)
	
     print(result)
	
     if "ERROR" in result:
	
         close_all()
	
         return -1
  except:
     print("Http Params Error")
     return 20
	
  time.sleep(2)


  #create timeout for cleartemp server to give reply
  try:
	  cmd = "AT+HTTPDATA="+str(getDataBytes(dataStr)) +",10000"
	  # 0 for get and 1 for post
	  #result = execute(cmd)
	
	  print("Data 10s timeout Result "+result)
          #r=1
	  #while r == 1:
	    #if "DOWNLOAD" in result:
             # r=2
           # print('wait for data through')
           # time.sleep(2)
	
	  #if "ERROR" in result:
	
	   #close_all()
	
    	    #return -1
  except:
    print("Post Error")
    return 20

  time.sleep(2)
  
  GPIO.remove_event_detect(motion_pin)

  try:
    cmd = "AT+HTTPACTION=1"
    # 0 for get and 1 for post
    result = execute(cmd)

    print("Action Result "+result)

    if "ERROR" in result:
      close_all()
      return -1
  except:
    print("Post Error")
    return 20

  GPIO.add_event_detect(motion_pin, GPIO.BOTH, callback=motionDetect)

  time.sleep(2)

#+HTTPACTION: 1,603,0. its network error.

  try:
    cmd = "AT+HTTPTERM"

    result = execute(cmd)

    print("Termination Result "+result)

    if "ERROR" in result:
      close_all()
      return -1
  except:
    	  print("Http Terminate Error")
    	  return 20

  return 200

def motionDetect(pin):
  """Sets motion_detected to True and disables interrupt."""
  global motion_detected, waiting_for_motion
  print('----------------------------------------------------------')
  print('motion state changed')
  #assert GPIO.input(pin)
  if GPIO.input(pin) == GPIO.HIGH:
    motion_detected = True
    waiting_for_motion = False
  else:
    motion_detected = False
  #GPIO.remove_event_detect(pin)
  print('motion detected?', motion_detected)
  print('----------------------------------------------------------')

      
def motionfallingDetect():
    global motion_pin
    # print(" not detected")
    #main(0)
    GPIO.remove_event_detect(motion_pin)

    
def b1(pin):
  global relayState

  if(GPIO.input(buttons[0])==0):
    if(relayState[0]==0):
      print('button 1 pressed, turning on relay 1')
      relayState[0]=1
      relayHandle(0,1)
    else:
      print('button 1 pressed, turning off relay 1')
      relayState[0]=0
      relayHandle(0,0)
      
def b2(pin):
  global relayState

  if(GPIO.input(buttons[1])==0):
    if(relayState[1]==0):
      print('button 2 pressed, turning on relay 2')
      relayState[1]=1
      relayHandle(1,1)
    else:
      print('button 2 pressed, turning off relay 2')
      relayState[1]=0
      relayHandle(1,0)
      
def b3(pin):
  global relayState

  if(GPIO.input(buttons[2])==0):
    if(relayState[2]==0):
      print('button 3 pressed, turning on relay 3')
      relayState[2]=1
      relayHandle(2,1)
    else:
      print('button 3 pressed, turning off relay 3')
      relayState[2]=0
      relayHandle(2,0)
    time.sleep(1.5)
      
def b4(pin):
  global relayState

  if(GPIO.input(buttons[3])==0):
    if(relayState[3]==0):
      print('button 4 pressed, turning on relay 4')
      relayState[3]=1
      relayHandle(3,1)
    else:
      print('button 4 pressed, turning off relay 4')
      relayState[3]=0
      relayHandle(3,0)

def recursiveMethod():
  temp = str(tempRead())
  time.sleep(0.2)
  date = dateRead()
  powerOnGps()
  time.sleep(0.2)
  lng,lat = read_gps(0)
  time.sleep(0.2)
  motionS = 1
	     
  code = send_gsm(temp,date,lng,lat,motionS)
  time.sleep(0.2)
  return code
 
def init_all():

  try:
    cmd = "AT"

    result = execute(cmd)

    print(result)

    if "OK" in result:
        print('AT is OK')
        print('Search for network')
        time.sleep(10)
    elif "ERROR" in result:

      #return -1
      close_all()

      return -1
    else:
      print('No AT Response')
      return 20
  except:
    print('No AT Response Check Power.')
    return -1

  try:
    
    cmd = "AT+CDSCB"

    #result = execute(cmd)

    print(result)


    try:
      cmd = "AT+SAPBR=0,1"

      result = execute(cmd)

      print(result)
    except:
      print('Already Executed')
    #port.close()
  except:
    return 20
  
  return 200

def testFunctionMotion():
    #motion test
    testMotion = 1
    while testMotion ==1:
      if(motion_detected == 1):
        print("Motion 1")
        motion_detected = 0
      print("Motion Loop")
      time.sleep(2)

def systemInit():

    #initReturn = 0
    initStatus = 1
    while initStatus == 1:
      print("Initilizing Modem")
      initReturn = init_all()
      if(initReturn == 200):
        initStatus = 2
        print("Modem Initilized")
      time.sleep(2)


def initGprsParams():
  try:
    gprsInit=0
    while gprsInit == 0:
      simActive = init_Gprs()
      if(simActive == 20):
        print("Not Registered On Network: ", simActive)
      elif(simActive == -1):
        print("GPRS not Active: ", simActive)
      elif(simActive == 200):
        gprsInit = 1
        print("Sim Registered for GPRS: ", simActive)
      time.sleep(1)
  except:
    return 20


def restart_motion_detection():
  global motion_detected, motion_pin
  pvalue = GPIO.input(motion_pin)
  print('motion_pin value during restart_motion_detection call: ', pvalue)
  if enableMotion and motion_detected and pvalue == 0:
    print ('motion detection restarted')
    motion_detected = False
    GPIO.add_event_detect(motion_pin, GPIO.RISING, callback=motionDetect)


def startLogging():
  global waiting_for_motion
  lng = '0'
  lat = '0'
  temp = 0
  waiting_for_motion = True
  while True:
    print("Running Forever")

    date = dateRead()
    try:
      temp = str(tempRead())
    except:
      print("Temperature sensor not present")
    time.sleep(0.2)
    while len(lat) <= 3 and len(lng) <= 3:
      lng,lat = read_gps(0)
      print("GPS reading")
      time.sleep(1)
    print("Location acquired")
    time.sleep(0.2)
    code = send_gsm(temp, date, lng, lat)
    time.sleep(3.5)
    if(code == -1):
      print("Error in Sim800 "+str(code))
      print("Executing Again "+str(code))
      #init_all()
      #init_Gprs()
      systemInit()
      initGprsParams()
      powerOnGps()
      time.sleep(4)

"""
def startLogging():
    global motion_detected
    motionVarient = 0
    lng = '0'
    lat = '0'
    code = 0
    var = 1
    motionS = 0
    while var == 1:
      print("Running Forever")
      if(enableMotion == False):
        motion_detected = 1
      if(motion_detected == 1):
        motionVarient = motionVarient + 1
        motion_detected = 0
        print('Varient Added : ' + str(motionVarient))
      if(motionVarient >= 2):
        motionS = 1
        motionVarient = 0
        date = strftime("%Y-%m-%d ") + strftime("%H:%M:%S")
        print("Date: ", date)
        temp = 0
        try:
          temp = str(tempRead())
        except:
          print("Temperature sensor not present")
        time.sleep(0.2)
        #lng,lat = read_gps(0)
        location = 0
        while location < 2:
          if(len(lat) <= 3 and len(lng) <= 3):
            lng,lat = read_gps(0)
            print("GPS reading")
            time.sleep(1)
          else:
            location = 2
          print("Location acquired")
          time.sleep(0.2)
          code = send_gsm(temp,date,lng,lat,motionS,1)
          time.sleep(0.2)
          time.sleep(4)
          #close_all()
          #code = -1
          if(code == -1):
            print("Error in Sim800 "+str(code))
            print("Executing Again "+str(code))
            #init_all()
            #init_Gprs()
            systemInit()
            initGprsParams()
            powerOnGps()
            time.sleep(4)
            #tryCode = recursiveMethod()
            #if(tryCode == -1):
              # print("Error in Sim800 "+str(code))
               #print("Executing Again "+str(code))
               #tryCode = recursiveMethod()
               #continue
        continue
"""
   
def main(motionV):
    
    global motion_detected,motion_pin, port
    print('MAIN Data Execution.........')
    dateRead()
    gprsInit = 0

    
    systemInit()
    initGprsParams()
    powerOnGps()
    startLogging()

def addInterrupts(): 
    global motion_pin
    if(enableMotion):
      GPIO.add_event_detect(motion_pin, GPIO.BOTH, callback=motionDetect)

    if(enableButtons):
      GPIO.add_event_detect(buttons[0], GPIO.BOTH, callback=b1 )
      GPIO.add_event_detect(buttons[1], GPIO.BOTH, callback=b2 )
      GPIO.add_event_detect(buttons[2], GPIO.FALLING, callback=b3 )
      GPIO.add_event_detect(buttons[3], GPIO.BOTH, callback=b4 )
         

#if __name__ == '__main__' 

#GPIO.add_event_detect(motion_pin, GPIO.RISING, callback=motionDetect )
#GPIO.add_event_detect(buttons[0], GPIO.BOTH, callback=b1 )
#GPIO.add_event_detect(buttons[1], GPIO.BOTH, callback=b2 )
#GPIO.add_event_detect(buttons[2], GPIO.FALLING, callback=b3 )
#GPIO.add_event_detect(buttons[3], GPIO.BOTH, callback=b4 )

addInterrupts()
main(0)
time.sleep(3)

port.close()
