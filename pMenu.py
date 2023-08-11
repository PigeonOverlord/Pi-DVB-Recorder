#!/usr/bin/env python

import time
import atexit
import subprocess
import scanFuncs
import os, sys, shutil

from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw

width, height = lcd.dimensions()

# A squarer pixel font
#font = ImageFont.truetype(fonts.BitocraFull, 11)

# A slightly rounded, Ubuntu-inspired version of Bitocra
font = ImageFont.truetype(fonts.BitbuntuFull, 10)

image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)

satList = [{
    'name': 'Astra 19.2E',
    'frequency': '11229000000',
    'symb': '22000000',
    'polarity': 'vertical'},
    {
    'name': 'Eutelsat 5W B',
    'frequency': '11096000000',
    'symb': '29950000',
    'polarity': 'vertical'}
    ]

# Menu class
class MenuOption:
    def __init__(self, name, action, options=()):
        self.name = name
        self.action = action
        self.options = options
        self.size = font.getsize(name)
        self.width, self.height = self.size

    def trigger(self):
        self.action(*self.options)
        

def set_backlight(r, g, b):
    backlight.set_all(r, g, b)
    backlight.show()

# Start Menu screen
def startMenu():
    global current_menu_option
    current_menu_option = 0
    global menu_options
    menu_options = [
    MenuOption('Terrestrial scan', set_backlight, (0, 0, 255)),
    MenuOption('Satellite scan', set_backlight, (0, 0, 255)),
    MenuOption('Exit', sys.exit, (0,))
    ]

# Scan menu screen
def mainMenu():
    global current_menu_option
    current_menu_option = 0
    global menu_options
    menu_options = [
    MenuOption('Record', set_backlight, (255, 0, 0)),
    MenuOption('Initial scan', set_backlight, (0, 255, 0)),
    MenuOption('Back', set_backlight, (255, 0, 0)),
    MenuOption('Exit', sys.exit, (0,))
    ]
    
def satMenu():
    trigger_action = False
    global current_menu_option
    current_menu_option = 0
    global menu_options
    menu_options = [
    MenuOption('Astra 19.2E', set_backlight, (255, 0, 0)),
    MenuOption('Eutelsat 5W B', set_backlight, (0, 255, 0)),
    MenuOption('Back', set_backlight, (255, 0, 0)),
    MenuOption('Exit', sys.exit, (0,))
    ]

def scanningWaitScreen():
    global current_menu_option
    current_menu_option = 0
    global menu_options
    menu_options = [
    MenuOption('Scanning...', set_backlight, (0, 0, 255)),
    MenuOption('Please wait', set_backlight, (0, 0, 255))]

# Screen display for when record is running
def recordingWaitScreen():
    global current_menu_option
    current_menu_option = 0
    global menu_options
    menu_options = [
    MenuOption('Recording...', set_backlight, (0, 0, 255)),
    MenuOption('Please wait', set_backlight, (0, 0, 255))]

# Screen confirmation for user feedback
def confirmationScreen():
    global current_menu_option
    current_menu_option = 0
    global menu_options
    menu_options = [
    MenuOption('Done!', set_backlight, (0, 0, 0))]

# menu navigation function - imported scanFuncs are called here 
def menu_nav():
    global scanType
    global satName
    if menu_options[current_menu_option].name == 'Terrestrial scan':
        mainMenu()
        scanType = 'terrestrial'
    elif menu_options[current_menu_option].name == 'Satellite scan':
        satMenu()
        scanType = 'satellite'
    elif menu_options[current_menu_option].name == 'Astra 19.2E':
        satName = menu_options[current_menu_option].name
        mainMenu()
    elif menu_options[current_menu_option].name == 'Eutelsat 5W B':
        satName = menu_options[current_menu_option].name
        mainMenu()
    elif menu_options[current_menu_option].name == 'Record':
        print(trigger_action)
        if scanType == 'satellite':
            recordingWaitScreen()
            scanFuncs.satRecordingsDeleteFolder()
            scanFuncs.satService_listDeleteFolder()
            scanFuncs.satNetworkRecord(satName)
            confirmationScreen()
        else:
            scanningWaitScreen()
            recordingWaitScreen()
            scanFuncs.terrRecordingsDeleteFolder()
            scanFuncs.terrService_listDeleteFolder()
            scanFuncs.terrNetworkRecord()
            confirmationScreen()
    elif menu_options[current_menu_option].name == 'Initial scan':        
        if scanType == 'satellite':
            for sat in satList:
                if sat['name'] == satName:
                    scanningWaitScreen()
                    scanFuncs.satScan(sat['name'], sat['frequency'], sat['symb'], sat['polarity'])
                    confirmationScreen()
        else:
            scanningWaitScreen()
            scanFuncs.terrScan()
            confirmationScreen()
   
    elif menu_options[current_menu_option].name == 'Back':
        startMenu()
    elif menu_options[current_menu_option].name == 'Done!':
        startMenu()
    elif menu_options[current_menu_option].name == 'Exit':
        cleanup()
        sys.exit()

startMenu()

current_menu_option = 1

trigger_action = False

# button press function for Pi display unit, triggers menu navigation
def handler(ch, event):
    global current_menu_option, trigger_action
    if event != 'press':
        return
    if ch == 1:
        current_menu_option += 1
    if ch == 0:
        current_menu_option -= 1
    if ch == 4:
        trigger_action = True
        menu_nav()
        trigger_action = False

                    
    current_menu_option %= len(menu_options)
    
for x in range(6):
    touch.set_led(x, 0)
    backlight.set_pixel(x, 255, 255, 255)
    touch.on(x, handler)

backlight.show()

## Clear screen
def cleanup():
    backlight.set_all(0, 0, 0)
    backlight.show()
    lcd.clear()
    lcd.show()

atexit.register(cleanup)

try:
    while True:
        image.paste(0, (0, 0, width, height))
        offset_top = 0

        if trigger_action:
            menu_options[current_menu_option].trigger()
            trigger_action = False

        for index in range(len(menu_options)):
            if index == current_menu_option:
                break
            offset_top += 12

        for index in range(len(menu_options)):
            x = 10
            y = (index * 12) + (height / 2) - 4 - offset_top
            option = menu_options[index]
            if index == current_menu_option:
                draw.rectangle(((x-2, y-1), (width, y+10)), 1)
            draw.text((x, y), option.name, 0 if index == current_menu_option else 1, font)

        w, h = font.getsize('>')
        draw.text((0, (height - h) / 2), '>', 1, font)

        for x in range(width):
            for y in range(height):
                pixel = image.getpixel((x, y))
                lcd.set_pixel(x, y, pixel)

        lcd.show()
        time.sleep(1.0 / 30)

except KeyboardInterrupt:
    cleanup()
cleanup()
