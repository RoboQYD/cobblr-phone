#!/usr/bin/python
from engine import TextWriter
from engine import SystemState
from engine import Utilities
from engine import Timer
from engine import Menu
from engine import Screen
import os
import time
import serial
import signal

"""
Module: phone_module
Location: applications/phone/phone_module.py
"""

signal.signal(signal.SIGINT, Utilities.GracefulExit)

class PhoneState(object):
  pass

def Init():
  # Setup variables used by the phone app.
  SystemState.PhoneState = PhoneState
  SystemState.pressed_buttons = ''
  SystemState.pressed_button = None
  
  # Start serial port and listen.
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
  SystemState.PhoneState.serial_port = serial_port

def Process():
  button = str(SystemState.pressed_button)
  pygame = SystemState.pygame
  screen = SystemState.screen
  serial_port = SystemState.PhoneState.serial_port

  if button == 'delete':
    SystemState.pressed_buttons = SystemState.pressed_buttons[:-1]
    TextWriter.Write(
        state=SystemState, 
        text=SystemState.pressed_buttons,
        text_type = "top"
    )
  elif button == 'go_back':
    Menu.Back(change_application=True)
  elif button == 'call':
    if SystemState.screen_mode == 1:
      Menu.JumpTo(application='phone', screen_mode=2, store_history=False, change_application=True)
      serial_message = "ATD " + SystemState.pressed_buttons + ';'
      WriteToSerial(serial_port, serial_message)
      TextWriter.Write(
          text="Calling", 
          text_type = 'message'
      )
      TextWriter.Write(
          text=SystemState.pressed_buttons,
          text_type = 'subtext'
      )
    else:
      Menu.JumpTo(application='phone', screen_mode=2, store_history=False, change_application=True)
      WriteToSerial(serial_port, "ATA")
      TextWriter.Write(
          text=SystemState.pressed_buttons,
          text_type = 'subtext'
      )
  elif button == 'hangup':
    Menu.Back(change_application=True)
    WriteToSerial(serial_port, "ATH")
    TextWriter.Write(
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )
  elif button == 'hash':
    SystemState.pressed_buttons = SystemState.pressed_buttons + '#'
    TextWriter.Write(
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )
  elif button == 'star':
    SystemState.pressed_buttons = SystemState.pressed_buttons + '*'
    TextWriter.Write(
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )
  else:
    SystemState.pressed_buttons = SystemState.pressed_buttons + str(button)
    TextWriter.Write(
        text=SystemState.pressed_buttons,
        text_type = 'top'
    )

def Thread():
  serial_port = SystemState.PhoneState.serial_port
  
  # Infinite loop to pass found messages to InterruptSystem() in cobblr. 
  while True:
    # Looks for incomming serial messages (calls, texts, etc).
    try:
      serial_data = serial_port.readlines()
    except serial.SerialException:
      serial_data = [] # Evil.
 
    serial_data = ParseSerialData(serial_data)
    if len(serial_data) > 0:
        print 'serial data: ', serial_data
    
    # Call related interrupts
    if len(serial_data) > 0:
      message_type = serial_data[0]
      if message_type == 'RING':
        serial_data = serial_data[1].strip()
        stripped_number = serial_data.split('"')[1].strip('"')
        Screen.WakeScreen()
        
        # Setting RING timeout timer to hang up if NO CARRIER is not received.
        callback = Menu.Back
        callback_args = {'change_application': True}
        Timer.DeleteTimeOut('ring_timeout')
        Timer.SetTimeOut('ring_timeout', 6, callback, callback_args)

        # Changes menu
        callback_args = {'screen_mode': 3, 'application': 'phone', 'change_application': True, 'store_history': False}
        message = {'callback': Menu.JumpTo, 'callback_args': callback_args}
        SystemState.interrupt_queue.put(message)

        # Print's 'Incomming Call' on the screen.
        callback_args = {'permatext': True, 'text': 'Incomming Call', 'text_type': 'message'}
        message = {'callback': TextWriter.Write, 'callback_args': callback_args}
        SystemState.interrupt_queue.put(message)
        
        # Print's the phone number on the screen.
        callback_args = {'permatext': True, 'text': stripped_number, 'text_type': 'subtext'}
        message = {'callback': TextWriter.Write, 'callback_args': callback_args}
        SystemState.interrupt_queue.put(message)
      
      if message_type == 'ATA':
          Timer.DeleteTimeOut('ring_timeout')
      
      # If someone hang's up, go back to the lass application.
      if message_type == 'NO CARRIER':
        Timer.DeleteTimeOut('ring_timeout')
        callback_args = {'change_application': True}
        message = {'callback': Menu.Back,'callback_args': callback_args}
        SystemState.interrupt_queue.put(message)


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
