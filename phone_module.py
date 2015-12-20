#!/usr/bin/python
from engine import TextWriter
from engine import SystemState
import os
import time
import serial

"""
Module: phone_module
Location: applications/phone/phone_module.py
"""

class PhoneState(object):
    pass

def Init():
  # Setup variables used by the phone app.
  SystemState.PhoneState = PhoneState
  
  SystemState.pressed_buttons = ''
  SystemState.pressed_button = None
  SystemState.battery_life = None 
  
  # Start serial port and listen. Place anything it finds in the system queue.
  serial_port = serial.Serial("/dev/ttyAMA0", 115200, timeout=0.5)
  
  # TODO: Move this to FONA provisioning module.
  WriteToSerial(serial_port, "AT+CLIP=1")
  module_settings = SystemState.application_configs['phone']['module-settings']
  
  if module_settings is not None:
    speaker = module_settings.get('speaker')
    mic = module_settings.get('mic')
    if speaker == 'external':
      WriteToSerial(serial_port, "AT+CHFA=1")
    if speaker == 'internal':
      WriteToSerial(serial_port, "AT+CHFA=0")
    if mic == 'external':
      WriteToSerial(serial_port, "AT+CMIC=1")
    if mic == 'internal':
      WriteToSerial(serial_port, "AT+CMIC=0")
    
    # TODO: Add phone volume controls.
    WriteToSerial(serial_port, "AT+CLVL=100")

  # Setting system time using the FONA  
  try: # TODO: Tell system fona is off
    fona_response = WriteToSerial(serial_port, "AT+CCLK?")
    fona_response = fona_response[1].split('"')
    fona_response = fona_response[1].split(',')
    fona_date = fona_response[0].replace('/','')
    fona_time = fona_response[1]
    os.system('date +%y%m%d -s' + str(fona_date))
    os.system('date +%T-%:::z -s' + str(fona_time))
  except:
    pass

  # TODO: Learn about FONA commands to test for signal, etc.
  SystemState.serial_port = serial_port

def Process():
  button = str(SystemState.pressed_button)
  pygame = SystemState.pygame
  screen = SystemState.screen
  serial_port = SystemState.serial_port
  
  if button == 'delete':
    SystemState.pressed_buttons = SystemState.pressed_buttons[:-1]
    TextWriter.Write(
        state=SystemState, 
        text=SystemState.pressed_buttons,
        text_type = "top"
    )
  elif button == 'call':
    if SystemState.screen_mode == 1:
      SystemState.next_screen_mode = 2
      serial_message = "ATD " + SystemState.pressed_buttons + ';'
      WriteToSerial(serial_port, serial_message)
      TextWriter.Write(
          state=SystemState,
          text="Calling", 
          text_type = 'message'
      )
      TextWriter.Write(
          state=SystemState,
          text=SystemState.pressed_buttons,
          text_type = 'subtext'
      )
    if SystemState.screen_mode == 3:
      SystemState.next_screen_mode = 2
      WriteToSerial(serial_port, "ATA")
      TextWriter.Write(
          state=SystemState,
          text=SystemState.pressed_buttons,
          text_type = 'message'
      )
  elif button == 'hangup':
    SystemState.next_screen_mode = 1
    WriteToSerial(serial_port, "ATH")
    TextWriter.Write(
        state=SystemState,
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )
  elif button == 'hash':
    SystemState.pressed_buttons = SystemState.pressed_buttons + '#'
    TextWriter.Write(
        state=SystemState,
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )
  elif button == 'star':
    SystemState.pressed_buttons = SystemState.pressed_buttons + '*'
    TextWriter.Write(
        state=SystemState,
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )
  else:
    SystemState.pressed_buttons = SystemState.pressed_buttons + str(button)
    TextWriter.Write(
        state=SystemState,
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )

def Thread():
  serial_port = SystemState.serial_port
  battery_checked = False
  # Infinite loop to pass found messages to InterruptSystem() in cobblr. 
  while True:
    # Looks for incomming serial messages (calls, texts, etc).
    serial_data = serial_port.readlines(None)
    serial_data = ParseSerialData(serial_data)
    
    # Checks the battery power every 5 minutes.
    check_min = time.localtime().tm_min
    check_sec = time.localtime().tm_sec
   
    # At the 5 minute mark, take 5 chances to get the battery power.
    if battery_checked is True:
      if check_min % 5 == 0 and check_sec % 20 == 0:
        battery_info = WriteToSerial(serial_port, 'AT+CBC')
        print "BATT_CHECK:", check_min, check_sec
    else:
      battery_info = WriteToSerial(serial_port, 'AT+CBC')
       
    # Call related interrupts
    if len(serial_data) > 0:
      message_type = serial_data[0]
      if message_type  == 'RING':
        serial_data = serial_data[1].strip()
        message = {'application': 'phone', 'screen_mode': 3, 'message': serial_data}
        SystemState.interrupt_queue.put(message)
      if message_type == 'NO CARRIER':
        serial_data = message_type
        message = {'application': 'desktop', 'screen_mode': 1, 'message': serial_data}
        SystemState.interrupt_queue.put(message)
    
    # Battery related interrupts.
    if len(battery_info) > 0:
      battery_info = ParseSerialData(battery_info)
      message_type = battery_info[0]
      if message_type == 'AT+CBC':
        if battery_info[-1] != 'ERROR':
          battery_checked = True
          print battery_info
          battery_info= battery_info[1].split(',')[1]
          message = {'application': 'battery', 'screen_mode': 1, 'message': battery_info}
          SystemState.interrupt_queue.put(message)
      battery_info = [] # Resetting battery info.


def WriteToSerial(serial_port, message):
  message = str(message) + '\r'
  serial_port.write(message)
  try:
    response = serial_port.readlines(None)
  except:
    response = None
  return response

def ParseSerialData(data):
  return [i.strip('\r\n') for i in data if i != '\r\n']
