import requests

from time import strftime
import time

import serial

import RPi.GPIO as GPIO
from threading import Thread, Event

port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=3)

temp_sensor_path = '/sys/bus/w1/devices/28-020791774287/w1_slave'

#defining specefic user id for a device
uID = 

enableMotion=False
enableButtons=False
#motion_pin = 11
motion_pin = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

motionVal=0  #global motion variable
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
  print('GPRS initial INIT.........')
  try:
    cmd = "AT"

    result = execute(cmd)

    print(result)

    if "ERROR" in result:

      #return -1
      close_all()

      return -1
  except:
    print('No AT Response Check Power.')
    return -1

  try:
	  cmd = "AT+CREG?"
	
	  result = execute(cmd)
	
	  print("IS internet On #"+result + "#")
	  #print("IS internet On #"+result[17] + "#")
	  #print("IS internet On #"+result[18] + "#")
	  #print("IS internet On #"+result[19] + "#")
	  #print("IS internet On #"+result[20] + "#")
	  if(len(result) >= 22):
	    if(result[20] == '3'):
	      print("REGISTRATION DENIED "+result)
	      return 20
	    elif(result[20] == '0'):
	      print("No Network Found "+result)
	      return 20
	    elif(result[20] == '2'):
	      print("Network Not Registered "+result)
	      return 20
	  else:
	    return -1
	  if "ERROR" in result:
	
	    close_all()
	
	    return -1
  except:
    print("Sim Registration Error")
    return 20

  time.sleep(2)

  try:

	  cmd = "AT+SAPBR=3,1,\"contype\",\"GPRS\""
	
	  result = execute(cmd)
	
	  print(result)
	
	  if "ERROR" in result:
	
	
	    close_all()
	
	    return -1
  except:
    print("GPRS conType Error")
    return 20


  time.sleep(2)
  try:
	  cmd = "AT+SAPBR=3,1,\"APN\",\"simple\""
	
	  result = execute(cmd)
	
	  print(result)
	
	  if "ERROR" in result:
	
	    close_all()
	
	    return -1
  except:
    print("Apn Error")
    return 20
  #we have to enable gprs before any thing

  
  time.sleep(2)
  try:
    cmd = "AT+SAPBR=1,1"

    result = execute(cmd)

    print("is GPRS OK "+result)
 
    if "ERROR" in result:

      close_all()

      return -12
  except:
    print("GPRS indent Error")
    return 20

  time.sleep(5)

  try:
	  cmd = "AT+SAPBR=2,1"
	
	  result = execute(cmd)
	
	  print("eooo "+result)
	 
	  if "ERROR" in result:
	
	    close_all()
	
	    return -1
  except:
    print("GPRS params Error")
    return 20
  time.sleep(5)

  try:
    cmd = "AT+HTTPINIT"

    result = execute(cmd)

    print("Init HTTP "+result)
  except:
    print("Already Running "+result)
  #if "ERROR" in result:

    #close_all()

    #return -1
  return 200


def getDataBytes(st):
   
   return len(st.encode('utf-8'))

def send_gsm(temp, date, lng, lat, motion, firsttime):
    
  global motionVal, uID
  
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
  
  try:
     #cmd = "AT+HTTPPARA=\"URL\",\"http://hologram.io/test.html"
     # no network response from hologram io test
     
     cmd = "AT+HTTPPARA=\"URL\",\"http://www.cleartemp.site/datalog/savedatalog.php?"
     #cmd = "AT+HTTPPARA=\"URL\",\""
     time.sleep(0.05)
     cmd+="&datetime="+str(date)
     dataStr += "datetime="+str(date)
     cmd += "&temprature="+str(temp)
     dataStr += "temprature="+str(temp)
     cmd += "&latitude="+str(lat)
     dataStr += "latitude="+str(lat)
     cmd += "&longitude="+str(lng)
     dataStr += "longitude="+str(lng)
     cmd += "&motion="+str(motion)
     dataStr += "motion="+str(motion)
     cmd += "&userId="+str(uID)
     dataStr += "userId="+str(uID)
     cmd+="\""
     print('cmd=======',cmd)
     time.sleep(0.05)
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

def motionDetect(self):
  global motion_pin,motionVal
  print('detecting motion')
  #return GPIO.input(sensor_pin)
  if(GPIO.input(motion_pin)):
    print("motion detected pin high")
    motionVal=1
    print('motion value=',motionVal)
    
  else:
    print('motion detected pin low')
    motionVal=motionVal

      
def motionfallingDetect():
    global motion_pin
    # print(" not detected")
    #main(0)
    GPIO.remove_event_detect(motion_pin)

    
def b1(self):
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
      
def b2(self):
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
      
def b3(self):
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
      
def b4(self):
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
        date = strftime("%Y-%m-%d ") + strftime("%H:%M:%S")
        print("Date: ", date)
        powerOnGps()
        time.sleep(0.2)
	lng,lat = read_gps(0)
        time.sleep(0.2)
        motionS = 1
	
        
        
        code = send_gsm(temp,date,lng,lat,motionS,1)
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
      if(motionVal == 1):
        print("Motion 1")
	motionVal = 0
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

def startLogging():
    global motionVal
    motionVarient = 0
    lng = '0'
    lat = '0'
    code = 0
    var = 1
    while var == 1:
      print("Running Forever")
      if(enableMotion == False):
        motionVal = 1
      if(motionVal == 1):
        motionVarient = motionVarient + 1
        motionVal = 0
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
   
def main(motionV):
    
    global motionVal,motion_pin, port
    print('MAIN Data Execution.........')
    date = strftime("%Y-%m-%d ") + strftime("%H:%M:%S")
    print("Date: ", date)
    gprsInit = 0

    
    systemInit()
    initGprsParams()
    powerOnGps()
    startLogging()

def addInterrupts(): 
    global motion_pin
    if(enableMotion):
      GPIO.add_event_detect(motion_pin, GPIO.RISING, callback=motionDetect )

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
