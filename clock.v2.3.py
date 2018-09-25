#!/usr/bin/python 

# v1.00 First release

# v1.10
# Day of week alarm off
# Use cron for checks
# Toggle countdown from button
# Write config on button press
# day colours

# v1.20
# sunset blank problem
# Temperature characters
# Sunrise +1 hour

# v1.2.1
# weather error checking
# Get data error checking

# v1.22
# Sunrise blank - Cron check once

# v1.3
# Radio controls incuding volume
# Weather icon too bright (off for night?)
# Make service start/stop correctly
# Backup alarm after 5 mins
# Display radio station
# Countdown select on menu
# Restart on failure
# Alert on failure
# Service uses links for version control
# config dir service start

# v1.4
# Snooze

# v1.41
# NTP restart on sync error

# v1.5
# config dir service start
# Reversed buttons for upside down clock
# Restart NTP on error
# Alarm next on display - if alarm tomorrow is on and alarm today > alarm

# v1.6
# Menu timeout

# v1.7
# Threaded get external data and ntp check to stop lag
# Extra check for day/night colours

# v1.8
# Added reboot button

# v1.9
# Added status page

# v2.0
# Added custom anniversary music

# v1.2
# Added backgrounds

# v2.2
# Fixed font issue

# v2.3
# Display anniversary name

# Known issues:
# Config file corruption on crash
# Snooze - play last sound
# Global sound variable
# Sound name display not right
# Adjust logging levels
# Backgrounds
# Borders around display items for backgrounds
# Graphical buttons
# Reload config every day
# Change snooze layout/colour
# Move timesync display to clock screen only
# Next alarm daytime colour wrong

# Alarms - Heart, Magic, Vangellis, Pirates
# mpc lsplaylists - shows all playlists
# Add playlists and songs into /var/lib/mpc

import time
from datetime import datetime, timedelta
from commands import *
import os
import pygame
import sys
import logging
import ConfigParser
import urllib2
import json
from threading import Thread
import Queue

# Screen and touchscreen setup and calibration
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

# Change screen rotate in /etc/modprobe.d/adafruit.conf and /boot/cmdline.tst
# Recalibrate with following bash commands
# TSLIB_FBDEVICE=/dev/fb1
# TSLIB_TSDEVICE=/dev/input/touchscreen ts_calibrate

# Set up logging
#logging.basicConfig(filename="/var/log/clock.log", level=logging.INFO, format='%(asctime)s %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logging.info('###### Clock Started ######')

# Set up variables

logging.info('Setting up variables')

# Define colours
colourWhite = (255, 255, 255)
colourGrey = (128, 128, 128)
colourDarkGrey = (64, 64, 64)
colourBlack = (0, 0, 0)
colourGreen = (0, 100, 0)
colourBlue = (0, 130, 130)
colourDarkBlue = (0, 5, 150)
colourLightBlue = (0 , 64, 200)
colourRed = (200 ,0 ,0)

colourDay = colourDarkBlue
colourNight = colourBlack
colourAlarm = colourGreen

colourDayTime = colourWhite
colourDayDate = colourWhite
colourDayGeneral = colourWhite
colourDayAlarmStatus = colourWhite
colourDayAlarmDimmed = colourBlack
colourDayTemp = colourWhite
colourDayCountdown = colourWhite

colourNightTime = colourDarkBlue
colourNightDate = colourGrey
colourNightGeneral = colourGrey
colourNightAlarmStatus = colourGrey
colourNightAlarmDimmed = colourDarkGrey
colourNightTemp = colourGrey
colourNightCountdown = colourGrey

colourAlarmDimmed = colourDarkGrey

# Default display to clock view
display = "clock"

# Default alarm to off
alarm = "off"

# Default NTP sync to ok
sync=1

# Default day/night colours
day = "no"

# Default radio to off
radio = "off"

# Define Radio Stations - Must be mpc playlists
radio_1 = "Heart"
radio_2 = "Magic"

# Define message - used for anniversary display
message = ""

# Define alarm backup
alarmbackup = "Pirates"

alarmselect = "1"
triggeralarm1 = "no"
triggeralarm2 = "no"

snooze = "off"
snoozetime = "none"

alarm1box = colourWhite
alarm2box = colourWhite

menutimeout = 150
menutimeoutcount = 0

# Define button positions
button_back = pygame.Rect(10, 10, 50, 50)
button_alarm1 = pygame.Rect(105, 40, 75, 40)
button_alarm2 = pygame.Rect(185, 40, 75, 40)

button_alarm_menu = pygame.Rect(30, 80, 50, 50)
button_countdown_menu = pygame.Rect(110, 80, 80, 50)
button_radio_menu = pygame.Rect(230, 80, 50, 50)
button_status_menu = pygame.Rect(70, 140, 50, 50)
button_reboot = pygame.Rect(100, 200, 100, 30)

button_snooze = pygame.Rect(50, 175, 210, 100)

button_0 = pygame.Rect(10, 90, 50, 50)
button_1 = pygame.Rect(70, 90, 50, 50)
button_2 = pygame.Rect(130, 90, 50, 50)
button_3 = pygame.Rect(190, 90, 50, 50)
button_4 = pygame.Rect(250, 90, 50, 50)
button_5 = pygame.Rect(10, 150, 50, 50)
button_6 = pygame.Rect(70, 150, 50, 50)
button_7 = pygame.Rect(130, 150, 50, 50)
button_8 = pygame.Rect(190, 150, 50, 50)
button_9 = pygame.Rect(250, 150, 50, 50)

button_day_0 = pygame.Rect(5, 210, 30, 30)
button_day_1 = pygame.Rect(50, 210, 30, 30)
button_day_2 = pygame.Rect(95, 210, 30, 30)
button_day_3 = pygame.Rect(140, 210, 30, 30)
button_day_4 = pygame.Rect(185, 210, 30, 30)
button_day_5 = pygame.Rect(230, 210, 30, 30)
button_day_6 = pygame.Rect(275, 210, 30, 30)

button_countdown_on = pygame.Rect(30, 80, 50, 50)
button_countdown_off = pygame.Rect(110, 80, 50, 50)

button_radio_1 = pygame.Rect(30, 80, 80, 30)
button_radio_2 = pygame.Rect(30, 120, 80, 30)
button_radio_off = pygame.Rect(30, 160, 80, 30)

button_volume_up = pygame.Rect(180, 60, 80, 80)
button_volume_down = pygame.Rect(180, 150, 80, 80)

# Read settings from clock.conf
# Get current directory for config file location
full_path = os.path.realpath(__file__)

logging.info('Reading settings from clock.conf')

config = ConfigParser.ConfigParser()
config.read((os.path.dirname(full_path))+"/clock.conf")

onpi=config.get("system","onpi")
displayicon=config.get("system","displayicon")

installdir=config.get("paths","installdir")
icondir=config.get("paths","icondir")
tempdir=config.get("paths","tempdir")
confdir=config.get("paths","confdir")
fontdir=config.get("paths","fontdir")

alarm1=config.get("alarms","alarm1")
alarm1enabled=config.get("alarms","alarm1enabled")
alarm1sound=config.get("alarms","alarm1sound")
alarm1doty=config.get("alarms","alarm1doty")
alarm1ontomorrow="no"

alarm2=config.get("alarms","alarm2")
alarm2enabled=config.get("alarms","alarm2enabled")
alarm2sound=config.get("alarms","alarm2sound")
alarm2doty=config.get("alarms","alarm2doty")
alarm2ontomorrow="no"

countdownday=int(config.get("countdown","countdownday"))
countdownmonth=int(config.get("countdown","countdownmonth"))
countdownyear=int(config.get("countdown","countdownyear"))
countdownenabled=config.get("countdown","countdownenabled")

anniversary1=config.get("anniversary","anniversary1")
anniversary1=anniversary1.split(',')
anniversary2=config.get("anniversary","anniversary2")
anniversary2=anniversary2.split(',')
anniversary3=config.get("anniversary","anniversary3")
anniversary3=anniversary3.split(',')
anniversary4=config.get("anniversary","anniversary4")
anniversary4=anniversary4.split(',')
anniversary5=config.get("anniversary","anniversary5")
anniversary5=anniversary5.split(',')
anniversary6=config.get("anniversary","anniversary6")
anniversary6=anniversary6.split(',')
anniversary7=config.get("anniversary","anniversary7")
anniversary7=anniversary7.split(',')
anniversary8=config.get("anniversary","anniversary8")
anniversary8=anniversary8.split(',')
anniversary9=config.get("anniversary","anniversary9")
anniversary9=anniversary9.split(',')

# Define global variables

temp = "99"
weathericon = "10n"
sunrise = "08:00"
sunset = "18:00"

# Get alarm days
alarm1doty=alarm1doty.split(",")
alarm2doty=alarm2doty.split(",")

# Calculate countdown days + 1 to show full days not hours
countdown = str((datetime(countdownyear,countdownmonth,countdownday) - datetime.now()).days +1)

# Define clock ticks
clock=pygame.time.Clock()

# Set up queue for threads
q = Queue.Queue()

#Set GPIO mode
if onpi=="yes":

	logging.info('Setting up GPIO')
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)

	# Setup GPIO - Pi B v1 uses GPIO 21 instead of 27
	GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	#GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(18, GPIO.RISING)
	GPIO.add_event_detect(22, GPIO.RISING)
	GPIO.add_event_detect(23, GPIO.RISING)
	GPIO.add_event_detect(27, GPIO.RISING)

# Set up fonts
pygame.font.init()
fontpath = fontdir+"DroidSans.ttf"
#fontpath = pygame.font.match_font('droidsans')
font = pygame.font.Font(fontpath, 60)
fontSm = pygame.font.Font(fontpath, 18)
fontTiny = pygame.font.Font(fontpath, 14)

# Define functions
logging.info('Defining function')

def get_data():
	#global temp
	#global weathericon
	#global sunrise
	#global sunset
	logging.info('get_data thread running')
	try:
		response = urllib2.urlopen('http://api.openweathermap.org/data/2.5/weather?q=Westerham,uk&APPID=d1a563a41a98799694adbb5b63e2c008')
	except Exception:
		logging.info('*** Data download error ***')
	else:
		try:
			data = json.load(response)
		except ValueError:
			logging.info('*** Data parsing error ***')
			return ()
		temp = str(-273 + int(data['main']['temp']))
		#logging.info('temp = ' + temp)
		weathericon = data['weather'][0]['icon']
		#logging.info('weathericon = ' + weathericon)
		sunrise = time.strftime('%H:%M', time.localtime(data['sys']['sunrise']))
		#logging.info('sunrise = ' + sunrise)
		sunset =  time.strftime('%H:%M', time.localtime(data['sys']['sunset']))
		#logging.info('sunset = ' + sunset)
	q.put("data,"+temp+","+weathericon+","+sunrise+","+sunset)


def check_ntp():
	logging.info('check_ntp thread running')
	ntp = getoutput("ntpq -pn |grep \* |awk {'print $9'}")
	#ntp = "1"
	#logging.info('ntp = ' + ntp)
	check=is_number(ntp)
	if check == False:
		return(999)
	#return(ntp)
	q.put("ntp,"+ntp)

def play_music(sound):
	logging.info('Playing '+sound)
	output = getoutput("mpc clear ; mpc load "+sound+"; mpc volume 65 ; mpc play")
	return(output)

def stop_music():
	logging.info('Stopping music')
	output = getoutput("mpc stop")
	return(output)

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def shift_time_left(time,digit):
	digit=str(digit)
	joined = ','.join(time)
	digits = joined.split(',')

	digits[0]=digits[1]
	digits[1]=digits[3]
	digits[3]=digits[4]
	digits[4]=digit

	return(digits[0]+digits[1]+digits[2]+digits[3]+digits[4])

def toggle(value):
	if value == "0":
		value = "1"
	else:
		value = "0"
	return(value)


# Main code

# First run of shell scrips for external checks
logging.info('Get external data')

#data=get_data()
# Call get_data thread
data = Thread(target=get_data, args=())
data.start()

ntp=check_ntp()

# Check if day or night
now = datetime.now()
curhour = now.strftime('%H')
curmin = now.strftime('%M')
sunrisesplit=sunrise.split(":")
sunsetsplit=sunset.split(":")
if now.strftime('%H') > sunrisesplit[0]: day="yes"
if curhour > sunsetsplit[0]: day="no"

# Check for anniversary
shortdate = time.strftime("%d"+"/"+"%m")
if shortdate == anniversary1[0]:
	logging.info("Anniversary detected, setting music to "+anniversary1[2])
	alarm1sound = anniversary1[2]
	alarm2sound = anniversary1[2]
	message = anniversary1[3]
elif shortdate == anniversary2[0]:
	logging.info("Anniversary detected, setting music to "+anniversary2[2])
	alarm1sound = anniversary2[2]
	alarm2sound = anniversary2[2]
	message = anniversary2[3]
elif shortdate == anniversary3[0]:
	logging.info("Anniversary detected, setting music to "+anniversary3[2])
	alarm1sound = anniversary3[2]
	alarm2sound = anniversary3[2]
	message = anniversary3[3]
elif shortdate == anniversary4[0]:
	logging.info("Anniversary detected, setting music to "+anniversary4[2])
	alarm1sound = anniversary4[2]
	alarm2sound = anniversary4[2]
	message = anniversary4[3]
elif shortdate == anniversary5[0]:
	logging.info("Anniversary detected, setting music to "+anniversary5[2])
	alarm1sound = anniversary5[2]
	alarm2sound = anniversary5[2]
	message = anniversary5[3]
elif shortdate == anniversary6[0]:
	logging.info("Anniversary detected, setting music to "+anniversary6[2])
	alarm1sound = anniversary6[2]
	alarm2sound = anniversary6[2]
	message = anniversary6[3]
elif shortdate == anniversary7[0]:
	logging.info("Anniversary detected, setting music to "+anniversary7[2])
	alarm1sound = anniversary7[2]
	alarm2sound = anniversary7[2]
	message = anniversary7[3]
elif shortdate == anniversary8[0]:
	logging.info("Anniversary detected, setting music to "+anniversary8[2])
	alarm1sound = anniversary8[2]
	alarm2sound = anniversary8[2]
	message = anniversary8[3]
elif shortdate == anniversary9[0]:
	logging.info("Anniversary detected, setting music to "+anniversary9[2])
	alarm1sound = anniversary9[2]
	alarm2sound = anniversary9[2]
	message = anniversary9[3]
else:
	alarm1sound=config.get("alarms","alarm1sound")
	#logging.info('Alarm sound 1 set to '+alarmsound1)
	alarm2sound=config.get("alarms","alarm2sound")
	#logging.info('Alarm sound 2 set to '+alarmsound2)
	message = " "



logging.info('Initialising pygame')
# Enable screen

pygame.display.init()

screen = pygame.display.set_mode((320,240))

pygame.display.set_caption("Clock")

# Initialise font support
#pygame.font.init()

# Hide mouse pointer
if onpi == "yes":
	pygame.mouse.set_visible(False)

# Stop music if any is playing
stop_music()

#pygame.mixer.init()
#pygame.mixer.music.set_volume(85)

clock=pygame.time.Clock()

logging.info('Entering loop')
# Start an endless loop as time never ends!
while 1:

	# Update 5 times a second if in menu
	if display != "clock":
		clock.tick(5)
	else:
		clock.tick(1)

	# Check queue for date returned
	while not q.empty():
		logging.info('Data returned from thread')
		queuedata=(q.get())
		queuedata=queuedata.split(",")
		if queuedata[0] == "data":
			temp=str(queuedata[1])
			logging.info('temp = ' + temp)
			weathericon=queuedata[2]
			logging.info('weathericon = ' + weathericon)
			sunrise=queuedata[3]
			logging.info('sunrise = ' + sunrise)
			sunset=queuedata[4]
			logging.info('sunset = ' + sunset)
		if queuedata[0] == "ntp":
			ntp=queuedata[1]
			logging.info('ntp = ' + ntp)
			if int(float(ntp)) > 55:
				logging.info('NTP Time is out, restarting NTP')
				restartntp = getoutput("service ntp restart")
				ntp=check_ntp()
			if int(float(ntp)) > 55:
				sync = 0
		#sync = 0
		else:
			logging.info('NTP Time is in sync')
			sync = 1

	# Exit if running in a window
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			logging.info('Quit received')
			if onpi=="yes":
				GPIO.cleanup()
			sys.exit()

		# Stop sound on screen touch
		if event.type is pygame.MOUSEBUTTONDOWN:
			menutimeoutcount = 0
			if alarm == "on":
				x, y = pygame.mouse.get_pos()
				if button_snooze.collidepoint(x, y):
					snooze = "on"
					#snoozesound = 
					timeout = datetime.now()+timedelta(minutes=10)
					snoozetime = timeout.strftime('%H:%M:%S')
					alarm = "off"
					stop_music()
					logging.info('Snoozing until '+snoozetime)
				else:
					alarm = "off"
					snooze = "off"
					stop_music()
					logging.info('Alarm off')


			elif display == "topmenu":

				x, y = pygame.mouse.get_pos()
				if button_back.collidepoint(x, y): 
					logging.info('Display Clock')
					display = "clock"

				if button_alarm_menu.collidepoint(x, y):
					logging.info('Display Alarm Menu')
					display = "alarmmenu"
				if button_countdown_menu.collidepoint(x, y):
					logging.info('Display Countdown Menu')
					display = "countdownmenu"
				if button_radio_menu.collidepoint(x, y):
					logging.info('Display Radio Menu')
					display = "radiomenu"
				if button_status_menu.collidepoint(x, y):
					logging.info('Display Status Menu')
					display = "statusmenu"
				if button_reboot.collidepoint(x, y):
					logging.info('Rebooting...')
					if onpi=="yes":
						GPIO.cleanup()
					reboot = getoutput("reboot")
					quit()

			elif display == "alarmmenu":

				x, y = pygame.mouse.get_pos()

				if button_back.collidepoint(x, y): 
					display = "topmenu"
					snooze = "off"
					alarmselect = "1"
					# Save config
					logging.info('Save Config')
					config.set("alarms","alarm1",alarm1)
					config.set("alarms","alarm1enabled",alarm1enabled)
					#config.set("alarms","alarm1sound",alarm1sound)
					alarm1dotyJoined = ",".join(alarm1doty)
					config.set("alarms","alarm1doty",alarm1dotyJoined)

					config.set("alarms","alarm2",alarm2)
					config.set("alarms","alarm2enabled",alarm2enabled)
					#config.set("alarms","alarm2sound",alarm2sound)
					alarm2dotyJoined = ",".join(alarm2doty)
					config.set("alarms","alarm2doty",alarm2dotyJoined)

					configfile = open(confdir+"clock.conf","w") 
					config.write(configfile)

					logging.info('Display Top Menu')

				if button_alarm1.collidepoint(x, y):
					logging.info('Alarm 1 Selected')
					alarmselect = "1"
				if button_alarm2.collidepoint(x, y):
					logging.info('Alarm 2 Selected')
					alarmselect = "2"

				if button_0.collidepoint(x, y):
					logging.info('Button 0')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,0)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,0)						
				if button_1.collidepoint(x, y):
					logging.info('Button 1')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,1)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,1)
				if button_2.collidepoint(x, y):
					logging.info('Button 2')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,2)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,2)
				if button_3.collidepoint(x, y):
					logging.info('Button 3')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,3)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,3)
				if button_4.collidepoint(x, y):
					logging.info('Button 4')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,4)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,4)
				if button_5.collidepoint(x, y):
					logging.info('Button 5')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,5)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,5)
				if button_6.collidepoint(x, y):
					logging.info('Button 6')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,6)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,6)
				if button_7.collidepoint(x, y):
					logging.info('Button 7')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,7)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,7)
				if button_8.collidepoint(x, y):
					logging.info('Button 8')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,8)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,8)
				if button_9.collidepoint(x, y):
					logging.info('Button 9')
					if alarmselect == "1": alarm1 = shift_time_left(alarm1,9)
					if alarmselect == "2": alarm2 = shift_time_left(alarm2,9)

				if button_day_0.collidepoint(x, y):
					logging.info('Day Sun')
					if alarmselect == "1": alarm1doty[0] = toggle(alarm1doty[0])
					if alarmselect == "2": alarm2doty[0] = toggle(alarm2doty[0])
				if button_day_1.collidepoint(x, y):
					logging.info('Day Mon')
					if alarmselect == "1": alarm1doty[1] = toggle(alarm1doty[1])
					if alarmselect == "2": alarm2doty[1] = toggle(alarm2doty[1])
				if button_day_2.collidepoint(x, y):
					logging.info('Day Tue')
					if alarmselect == "1": alarm1doty[2] = toggle(alarm1doty[2])
					if alarmselect == "2": alarm2doty[2] = toggle(alarm2doty[2])
				if button_day_3.collidepoint(x, y):
					logging.info('Day Wed')
					if alarmselect == "1": alarm1doty[3] = toggle(alarm1doty[3])
					if alarmselect == "2": alarm2doty[3] = toggle(alarm2doty[3])
				if button_day_4.collidepoint(x, y):
					logging.info('Day Thu')
					if alarmselect == "1": alarm1doty[4] = toggle(alarm1doty[4])
					if alarmselect == "2": alarm2doty[4] = toggle(alarm2doty[4])
				if button_day_5.collidepoint(x, y):
					logging.info('Day Fri')
					if alarmselect == "1": alarm1doty[5] = toggle(alarm1doty[5])
					if alarmselect == "2": alarm2doty[5] = toggle(alarm2doty[5])
				if button_day_6.collidepoint(x, y):
					logging.info('Day Sat')
					if alarmselect == "1": alarm1doty[6] = toggle(alarm1doty[6])
					if alarmselect == "2": alarm2doty[6] = toggle(alarm2doty[6])

			elif display == "countdownmenu":

				x, y = pygame.mouse.get_pos()

				if button_back.collidepoint(x, y): 
					display = "topmenu"
					logging.info('Display Top Menu')
				if button_countdown_on.collidepoint(x, y):
					countdownenabled = "yes"
					config.set("countdown","countdownenabled",countdownenabled)
					configfile = open(confdir+"clock.conf","w")
					config.write(configfile)
					logging.info('Countdown On')
				if button_countdown_off.collidepoint(x, y):
					countdownenabled = "no"
					config.set("countdown","countdownenabled",countdownenabled)
					configfile = open(confdir+"clock.conf","w")
					config.write(configfile)
					logging.info('Countdown Off')

			elif display == "radiomenu":

				x, y = pygame.mouse.get_pos()

				if button_back.collidepoint(x, y): 
					display = "topmenu"
					logging.info('Display Top Menu')
				if button_radio_1.collidepoint(x, y):
					play_music(radio_1)
					radio = radio_1
				if button_radio_2.collidepoint(x, y):
					play_music(radio_2)
					radio = radio_2
				if button_radio_off.collidepoint(x, y):
					stop_music()
					radio = "off"
				if button_volume_up.collidepoint(x, y):
					logging.info('Volume Up')
					output = getoutput("mpc volume +2")
				if button_volume_down.collidepoint(x, y):
					logging.info('Volume Down')
					output = getoutput("mpc volume -2")

			elif display == "statusmenu":

				x, y = pygame.mouse.get_pos()

				if button_back.collidepoint(x, y): 
					display = "topmenu"
					logging.info('Display Top Menu')

			elif display == "clock":
				display = "topmenu"
				#config.close()
				logging.info('Display Top Menu')

		if event.type is pygame.KEYDOWN:
			logging.info('Key pressed')
			if event.key == "K_ESCAPE":
				logging.info('Escape pressed, exiting')
				if onpi=="yes":
					GPIO.cleanup()
				sys.exit()


	# Check for button presses

	if onpi=="yes":
		if GPIO.event_detected(18):
			logging.info('Button 1 pressed')
			if alarm1enabled == "yes":
				alarm1enabled = "no"
			else:
				alarm1enabled = "yes"
				logging.info('Save Config')
				config.set("alarms","alarm1enabled",alarm1enabled)
				configfile = open(confdir+"clock.conf","w")
				config.write(configfile)
			#config.close()

			#text = fontSm.render("23", True, colourWhite)
			#screen.blit(text, (200, 5))
			#pygame.display.update()

		if GPIO.event_detected(27):
			logging.info('Button 2 pressed')
			if alarm2enabled == "yes":
				alarm2enabled = "no"
			else:
				alarm2enabled = "yes"

			logging.info('Save Config')
			config.set("alarms","alarm2enabled",alarm2enabled)
			configfile = open(confdir+"clock.conf","w")
			config.write(configfile)
			#config.close()

			#text = fontSm.render("22", True, colourWhite)
			#screen.blit(text, (200, 5))
			#pygame.display.update()

		if GPIO.event_detected(22):
			logging.info('Button 3 pressed')
			if countdownenabled == "yes":
				countdownenabled = "no"
			else:
				countdownenabled = "yes"

			config.set("countdown","countdownenabled",countdownenabled)
			configfile = open(confdir+"clock.conf","w")
			config.write(configfile)
			#config.close()

			#text = fontSm.render("27", True, colourWhite)
			#screen.blit(text, (200, 5))
			#pygame.display.update()

		if GPIO.event_detected(23):
		#if (GPIO.input(27) == False):
			logging.info('Button 4 pressed')
			#init = getoutput('init 0')
			if radio == "off":
				play_music(radio_1)
				radio = "on"
			else:
				stop_music()
				radio = "off"
			#text = fontSm.render("18", True, colourWhite)
			#screen.blit(text, (200, 5))
			#pygame.display.update()

	# Check for menu timeout
	if display != "clock":
		menutimeoutcount +=1
		if menutimeoutcount >= menutimeout:
			menutimeoutcount = 0
			logging.info('Menu timeout')
			display = "clock"

        # Get current time
	now = datetime.now()
	curtime = now.strftime('%H:%M:%S')

	#curtime = time.strftime("%H"+":"+"%M"+":"+"%S")
	curdate = time.strftime("%a"+" "+"%d"+" "+"%b"+" "+"%Y")
	shortdate = time.strftime("%d"+"/"+"%m")

	curday = time.strftime("%a")

	# Check for scheduled actions
	# Set variable for mins and seconds
	subtime = time.strftime("%M"+":"+"%S")

	# 11pm
	#if curtime == '23:00:00':
		#logging.info('Running 11pm checks')
		# Reload config

	# On the hour and ten seconds (stops lag at zero seconds)
	if subtime == "00:10":
		logging.info('Running hourly checks')
		data = Thread(target=get_data, args=())
		data.start()

		if countdownenabled == "yes":
			countdown = str((datetime(countdownyear,countdownmonth,countdownday) - datetime.now()).days +1)

		if shortdate == anniversary1[0]:
			logging.info("Anniversary detected, setting music to "+anniversary1[2])
			alarm1sound = anniversary1[2]
			alarm2sound = anniversary1[2]
			message = anniversary1[3]
		elif shortdate == anniversary2[0]:
			logging.info("Anniversary detected, setting music to "+anniversary2[2])
			alarm1sound = anniversary2[2]
			alarm2sound = anniversary2[2]
			message = anniversary2[3]
		elif shortdate == anniversary3[0]:
			logging.info("Anniversary detected, setting music to "+anniversary3[2])
			alarm1sound = anniversary3[2]
			alarm2sound = anniversary3[2]
			message = anniversary3[3]
		elif shortdate == anniversary4[0]:
			logging.info("Anniversary detected, setting music to "+anniversary4[2])
			alarm1sound = anniversary4[2]
			alarm2sound = anniversary4[2]
			message = anniversary4[3]
		elif shortdate == anniversary5[0]:
			logging.info("Anniversary detected, setting music to "+anniversary5[2])
			alarm1sound = anniversary5[2]
			alarm2sound = anniversary5[2]
			message = anniversary5[3]
		elif shortdate == anniversary6[0]:
			logging.info("Anniversary detected, setting music to "+anniversary6[2])
			alarm1sound = anniversary6[2]
			alarm2sound = anniversary6[2]
			message = anniversary6[3]
		elif shortdate == anniversary7[0]:
			logging.info("Anniversary detected, setting music to "+anniversary7[2])
			alarm1sound = anniversary7[2]
			alarm2sound = anniversary7[2]
			message = anniversary7[3]
		elif shortdate == anniversary8[0]:
			logging.info("Anniversary detected, setting music to "+anniversary8[2])
			alarm1sound = anniversary8[2]
			alarm2sound = anniversary8[2]
			message = anniversary8[3]
		elif shortdate == anniversary9[0]:
			logging.info("Anniversary detected, setting music to "+anniversary9[2])
			alarm1sound = anniversary9[2]
			alarm2sound = anniversary9[2]
			message = anniversary9[3]
		else:
			alarm1sound=config.get("alarms","alarm1sound")
			#logging.info('Alarm sound 1 set to '+alarmsound1)
			alarm2sound=config.get("alarms","alarm2sound")
			#logging.info('Alarm sound 2 set to '+alarmsound2)
			message = ""

	# Every 15 mins and 30 seconds
	if subtime == "00:30" or subtime == "15:30" or subtime == "30:30" or subtime == "45:30":
		logging.info('Running 15 min checks')
		# Check time is in sync
		#ntp=check_ntp()
		ntp_thread = Thread(target=check_ntp, args=())
		ntp_thread.start()

#		if int(float(ntp)) > 55:
#			logging.info('NTP Time is out, restarting NTP')
#			restartntp = getoutput("service ntp restart")
#			ntp=check_ntp()
#			if int(float(ntp)) > 55:
#				sync = 0
#		#sync = 0
#		else:
#			logging.info('NTP Time is in sync')
#			sync = 1

	# Check for alarms
	if alarm == "off" and alarm1enabled == "yes" and alarm1+":00" == curtime:
			if curday == "Sun" and alarm1doty[0] == "1": triggeralarm1 = "yes"
			if curday == "Mon" and alarm1doty[1] == "1": triggeralarm1 = "yes"
			if curday == "Tue" and alarm1doty[2] == "1": triggeralarm1 = "yes"
			if curday == "Wed" and alarm1doty[3] == "1": triggeralarm1 = "yes"
			if curday == "Thu" and alarm1doty[4] == "1": triggeralarm1 = "yes"
			if curday == "Fri" and alarm1doty[5] == "1": triggeralarm1 = "yes"
			if curday == "Sat" and alarm1doty[6] == "1": triggeralarm1 = "yes"

			if triggeralarm1 == "yes":
				logging.info('Alarm 1 triggered')
				alarm = "on"

				# Set time for alarm auto-off
				timeout = datetime.now()+timedelta(minutes=30)
				alarmtimeout = timeout.strftime('%H:%M:%S')
				logging.info('Alarm timeout '+alarmtimeout)

				# Play backup sound incase streaming radio fails
				backup = datetime.now()+timedelta(minutes=5)
				backupalarm = backup.strftime('%H:%M:%S')
				logging.info('Backup Alarm '+backupalarm)

				# Play sound
				play_music(alarm1sound)
				triggeralarm1 = "no"

	if alarm == "off" and alarm2enabled == "yes" and alarm2+":00" == curtime:
			if curday == "Sun" and alarm2doty[0] == "1": triggeralarm2 = "yes"
			if curday == "Mon" and alarm2doty[1] == "1": triggeralarm2 = "yes"
			if curday == "Tue" and alarm2doty[2] == "1": triggeralarm2 = "yes"
			if curday == "Wed" and alarm2doty[3] == "1": triggeralarm2 = "yes"
			if curday == "Thu" and alarm2doty[4] == "1": triggeralarm2 = "yes"
			if curday == "Fri" and alarm2doty[5] == "1": triggeralarm2 = "yes"
			if curday == "Sat" and alarm2doty[6] == "1": triggeralarm2 = "yes"

			if triggeralarm2 == "yes":
				logging.info('Alarm 2 triggered')
				alarm = "on"
				timeout = datetime.now()+timedelta(minutes=30)
				alarmtimeout = timeout.strftime('%H:%M:%S')
				logging.info('Alarm timeout '+alarmtimeout)

				# Set time for alarm auto-off
				timeout = datetime.now()+timedelta(minutes=30)
				alarmtimeout = timeout.strftime('%H:%M:%S')
				logging.info('Alarm timeout '+alarmtimeout)

				# Play backup sound incase streaming radio fails
				backup = datetime.now()+timedelta(minutes=5)
				backupalarm = backup.strftime('%H:%M:%S')
				logging.info('Backup Alarm '+backupalarm)

				# Play sound
				play_music(alarm2sound)
				triggeralarm2 = "no"

	# Turn off alam after 30 mins
	if alarm == "on":
		if alarmtimeout == curtime:
			logging.info('Alarm timeout')
			alarm = "off"
			stop_music()

	# Play backup alarm sound
	if alarm == "on":
		if curtime == backupalarm:
			logging.info('Alarm backup tiggered')
			play_music(alarmbackup)	

	# Snooze alarm
	if snooze == "on":
		if curtime == snoozetime:
			logging.info('Snooze tiggered')
			alarm = "on"
			snooze = "off"
			play_music(alarm1sound)	# Should be previous alarm


	# Various checks for background colour

	now = datetime.now()
	curhour = now.strftime('%H')
	curmin = now.strftime('%M')
	sunrisesplit=sunrise.split(":")
	sunsetsplit=sunset.split(":")
	if now.strftime('%H') > sunrisesplit[0]: day="yes"
	if curhour > sunsetsplit[0]: day="no"

	# Daytime
	if curtime == sunrise+":00":
		day = "yes"

	# Nighttime
	if curtime == sunset+":00":
		day = "no"

	# Change colours
	if day == "yes":
		background = colourDay
		colourTime = colourDayTime
		colourDate = colourDayDate
		colourGeneral = colourDayGeneral
		colourAlarm1Status = colourDayAlarmStatus
		colourAlarm2Status = colourDayAlarmStatus
		colourAlarm1Dimmed = colourDayAlarmDimmed
		colourAlarm2Dimmed = colourDayAlarmDimmed
		colourTemp = colourDayTemp
		colourCountdown = colourDayCountdown

	else:
		background = colourNight
		colourTime = colourNightTime
		colourDate = colourNightDate
		colourGeneral = colourNightGeneral
		colourAlarm1Status = colourNightAlarmStatus
		colourAlarm2Status = colourNightAlarmStatus
		colourAlarm1Dimmed = colourNightAlarmDimmed
		colourAlarm2Dimmed = colourNightAlarmDimmed
		colourTemp = colourNightTemp
		colourCountdown = colourNightCountdown

	if alarm == "on":
		background = colourAlarm

	# if alarm is on tomorrow and is less than 23 hours away

	if alarm1enabled == "yes":
		if curday == "Sun" and alarm1doty[1] == "1": alarm1ontomorrow = "yes"
		elif curday == "Mon" and alarm1doty[2] == "1": alarm1ontomorrow = "yes"
		elif curday == "Tue" and alarm1doty[3] == "1": alarm1ontomorrow = "yes"
		elif curday == "Wed" and alarm1doty[4] == "1": alarm1ontomorrow = "yes"
		elif curday == "Thu" and alarm1doty[5] == "1": alarm1ontomorrow = "yes"
		elif curday == "Fri" and alarm1doty[6] == "1": alarm1ontomorrow = "yes"
		elif curday == "Sat" and alarm1doty[0] == "1": alarm1ontomorrow = "yes"
		else: alarm1ontomorrow = "no"

	if alarm2enabled == "yes":
		if curday == "Sun" and alarm2doty[1] == "1": alarm2ontomorrow = "yes"
		elif curday == "Mon" and alarm2doty[2] == "1": alarm2ontomorrow = "yes"
		elif curday == "Tue" and alarm2doty[3] == "1": alarm2ontomorrow = "yes"
		elif curday == "Wed" and alarm2doty[4] == "1": alarm2ontomorrow = "yes"
		elif curday == "Thu" and alarm2doty[5] == "1": alarm2ontomorrow = "yes"
		elif curday == "Fri" and alarm2doty[6] == "1": alarm2ontomorrow = "yes"
		elif curday == "Sat" and alarm2doty[0] == "1": alarm2ontomorrow = "yes"
		else: alarm2ontomorrow = "no"

	if alarm1ontomorrow == "yes":
		colourAlarm1Status = colourGreen
	else:
		if day == "yes":
			colourAlarm1Status = colourBlack
		else:
			colourAlarm1Status = colourGrey

	if alarm2ontomorrow == "yes":
		colourAlarm2Status = colourGreen	
	else:
		if day == "yes":
			colourAlarm2Status = colourGrey
		else:
			colourAlarm2Status = colourGrey



	#	b = str(alarm1-curtime)
	#	c = b.split(":")
	#	print c[0]


        # Draw background

	pygame.draw.rect(screen,background,(0,0,320,240))

	#if day == "yes":
		#pygame.draw.rect(screen,background,(0,0,320,240))
		#r,g,b = background.split(",")
		#r=int(r)
		#g=int(g)
		#b=int(b)
		#for l in range (0,255):
	    		#pygame.draw.rect(screen,(r,g,b),(0,l-1,320,l))

			#r=r-1;g=g-1;b=b-1
			#if r<=0: r=0
			#if g<=0: g=0
			#if b<=0: b=0
	#else:
		#pygame.draw.rect(screen,backgound,(0,0,320,240))

	#background = pygame.image.load("nature-blue-water.gif").convert_alpha()
	#screen.blit(background, (0, 0))

	if display == "topmenu":

		text = fontSm.render("Menu", True, colourWhite)
		screen.blit(text, (140, 10))

		text = fontSm.render("Back", True, colourWhite)
		screen.blit(text, (15, 25))
		pygame.draw.rect(screen, colourWhite, (button_back),2)

		text = fontTiny.render("Alarm", True, colourWhite)
		screen.blit(text, (35, 97))
		pygame.draw.rect(screen, colourWhite, (button_alarm_menu),2)

		text = fontTiny.render("Countdown", True, colourWhite)
		screen.blit(text, (115, 97))
		pygame.draw.rect(screen, colourWhite, (button_countdown_menu),2)

		text = fontTiny.render("Radio", True, colourWhite)
		screen.blit(text, (235, 97))
		pygame.draw.rect(screen, colourWhite, (button_radio_menu),2)

		text = fontTiny.render("Reboot", True, colourWhite)
		screen.blit(text, (130, 210))
		pygame.draw.rect(screen, colourWhite, (button_reboot),2)

		text = fontTiny.render("Status", True, colourWhite)
		screen.blit(text, (80, 150))
		pygame.draw.rect(screen, colourWhite, (button_status_menu),2)

		pygame.display.update()


	if display == "alarmmenu":


		# Display alarms
		if alarm1enabled == "yes":
			text = fontSm.render(alarm1, True, colourAlarm1Status)
		else:
			text = fontSm.render(alarm1, True, colourAlarm1Dimmed)
		screen.blit(text, (120, 50))
		
		if alarm2enabled == "yes":
			text = fontSm.render(alarm2, True, colourAlarm2Status)
		else:
			text = fontSm.render(alarm2, True, colourAlarm2Dimmed)
		screen.blit(text, (200, 50))

		text = fontSm.render("Menu", True, colourWhite)
		screen.blit(text, (140, 10))

		text = fontSm.render("Back", True, colourWhite)
		screen.blit(text, (15, 25))
		pygame.draw.rect(screen, colourWhite, (button_back),2)

		if alarmselect == "0":
			alarm1box = colourWhite
			alarm2box = colourWhite
		if alarmselect == "1":
			alarm1box = colourRed
			alarm2box = colourWhite
		if alarmselect == "2":
			alarm2box = colourRed
			alarm1box = colourWhite

		pygame.draw.rect(screen, alarm1box, (button_alarm1),2)
		pygame.draw.rect(screen, alarm2box, (button_alarm2),2)

		pygame.draw.rect(screen, colourWhite, (button_0),2)
		pygame.draw.rect(screen, colourWhite, (button_1),2)
		pygame.draw.rect(screen, colourWhite, (button_2),2)
		pygame.draw.rect(screen, colourWhite, (button_3),2)
		pygame.draw.rect(screen, colourWhite, (button_4),2)
		pygame.draw.rect(screen, colourWhite, (button_5),2)
		pygame.draw.rect(screen, colourWhite, (button_6),2)
		pygame.draw.rect(screen, colourWhite, (button_7),2)
		pygame.draw.rect(screen, colourWhite, (button_8),2)
		pygame.draw.rect(screen, colourWhite, (button_9),2)
		
		text = font.render("0", True, colourWhite)
		screen.blit(text, (20, 80))
		text = font.render("1", True, colourWhite)
		screen.blit(text, (80, 80))
		text = font.render("2", True, colourWhite)
		screen.blit(text, (140, 80))
		text = font.render("3", True, colourWhite)
		screen.blit(text, (200, 80))
		text = font.render("4", True, colourWhite)
		screen.blit(text, (260, 80))
		text = font.render("5", True, colourWhite)
		screen.blit(text, (20, 140))
		text = font.render("6", True, colourWhite)
		screen.blit(text, (80, 140))
		text = font.render("7", True, colourWhite)
		screen.blit(text, (140, 140))
		text = font.render("8", True, colourWhite)
		screen.blit(text, (200, 140))
		text = font.render("9", True, colourWhite)
		screen.blit(text, (260, 140))

		pygame.draw.rect(screen, colourWhite, (button_day_0),2)
		pygame.draw.rect(screen, colourWhite, (button_day_1),2)
		pygame.draw.rect(screen, colourWhite, (button_day_2),2)
		pygame.draw.rect(screen, colourWhite, (button_day_3),2)
		pygame.draw.rect(screen, colourWhite, (button_day_4),2)
		pygame.draw.rect(screen, colourWhite, (button_day_5),2)
		pygame.draw.rect(screen, colourWhite, (button_day_6),2)

		if alarmselect=="1":
			if alarm1doty[0]=="1":
				text = fontSm.render("S", True, colourWhite)
				screen.blit(text, (15, 215))
			if alarm1doty[1]=="1":
				text = fontSm.render("M", True, colourWhite)
				screen.blit(text, (57, 215))
			if alarm1doty[2]=="1":
				text = fontSm.render("T", True, colourWhite)
				screen.blit(text, (105, 215))
			if alarm1doty[3]=="1":
				text = fontSm.render("W", True, colourWhite)
				screen.blit(text, (145, 215))
			if alarm1doty[4]=="1":
				text = fontSm.render("T", True, colourWhite)
				screen.blit(text, (195, 215))
			if alarm1doty[5]=="1":
				text = fontSm.render("F", True, colourWhite)
				screen.blit(text, (240, 215))
			if alarm1doty[6]=="1":
				text = fontSm.render("S", True, colourWhite)
				screen.blit(text, (285, 215))
		if alarmselect=="2":
			if alarm2doty[0]=="1":
				text = fontSm.render("S", True, colourWhite)
				screen.blit(text, (15, 215))
			if alarm2doty[1]=="1":
				text = fontSm.render("M", True, colourWhite)
				screen.blit(text, (57, 215))
			if alarm2doty[2]=="1":
				text = fontSm.render("T", True, colourWhite)
				screen.blit(text, (105, 215))
			if alarm2doty[3]=="1":
				text = fontSm.render("W", True, colourWhite)
				screen.blit(text, (145, 215))
			if alarm2doty[4]=="1":
				text = fontSm.render("T", True, colourWhite)
				screen.blit(text, (195, 215))
			if alarm2doty[5]=="1":
				text = fontSm.render("F", True, colourWhite)
				screen.blit(text, (240, 215))
			if alarm2doty[6]=="1":
				text = fontSm.render("S", True, colourWhite)
				screen.blit(text, (285, 215))

		pygame.display.update()

	if display == "countdownmenu":

		text = fontSm.render("Countdown", True, colourWhite)
		screen.blit(text, (140, 10))

		text = fontSm.render("Back", True, colourWhite)
		screen.blit(text, (15, 25))
		pygame.draw.rect(screen, colourWhite, (button_back),2)

		text = fontTiny.render("On", True, colourWhite)
		screen.blit(text, (40, 97))
		pygame.draw.rect(screen, colourWhite, (button_countdown_on),2)

		text = fontTiny.render("Off", True, colourWhite)
		screen.blit(text, (125, 97))
		pygame.draw.rect(screen, colourWhite, (button_countdown_off),2)

		#text = fontSm.render("TBA", True, colourWhite)
		#screen.blit(text, (230, 80))
		#pygame.draw.rect(screen, colourWhite, (button_countdown_3),2)

		pygame.display.update()

	if display == "radiomenu":

		text = fontSm.render("Radio", True, colourWhite)
		screen.blit(text, (140, 10))

		text = fontSm.render("Back", True, colourWhite)
		screen.blit(text, (15, 25))
		pygame.draw.rect(screen, colourWhite, (button_back),2)

		text = fontTiny.render(radio_1, True, colourWhite)
		screen.blit(text, (35, 85))
		pygame.draw.rect(screen, colourWhite, (button_radio_1),2)

		text = fontTiny.render(radio_2, True, colourWhite)
		screen.blit(text, (35, 125))
		pygame.draw.rect(screen, colourWhite, (button_radio_2),2)

		text = fontTiny.render("Radio Off", True, colourWhite)
		screen.blit(text, (35, 165))
		pygame.draw.rect(screen, colourWhite, (button_radio_off),2)

		text = fontTiny.render("Volume +", True, colourWhite)
		screen.blit(text, (185, 90))
		pygame.draw.rect(screen, colourWhite, (button_volume_up),2)

		text = fontTiny.render("Volume -", True, colourWhite)
		screen.blit(text, (185, 180))
		pygame.draw.rect(screen, colourWhite, (button_volume_down),2)


		pygame.display.update()

	if display == "statusmenu":

		text = fontSm.render("Status", True, colourWhite)
		screen.blit(text, (140, 10))

		text = fontSm.render("Back", True, colourWhite)
		screen.blit(text, (15, 25))
		pygame.draw.rect(screen, colourWhite, (button_back),2)

		ifconfig = getoutput("ifconfig | grep -A1 wlan |grep inet|awk '{print $2}'")
		#ifconfig = "addr:192.168.10.18"
		text = fontSm.render(ifconfig, True, colourWhite)
		screen.blit(text, (0, 80))

		ping = getoutput ("ping -c 1 -W 1 -n google.co.uk| head -2")
		#ping = "1 packets transmitted, 0 received, 100% packet loss, time 0ms"
		text = fontSm.render(ping, True, colourWhite)
		screen.blit(text, (0, 100))

		space = getoutput ("df -h /")
		#space = "Filesystem      Size  Used Avail Use% Mounted on"
		text = fontSm.render(space, True, colourWhite)
		screen.blit(text, (0, 120))

		ntpq = getoutput ("ntpq -pn")
		#ntpq = "*195.186.4.100   195.186.133.101  2 u  962 1024  377   31.252    1.399   1.249"
		text = fontSm.render(ntpq, True, colourWhite)
		screen.blit(text, (0, 160))

		pygame.display.update()

	if display == "clock":

		# Display timesync warning
		if sync == 0:
			text = fontSm.render("Time out if sync", True, colourRed)
			screen.blit(text, (140, 30))	
	
        # Display the weather icon
		if displayicon=="yes":
			logo = pygame.image.load(icondir+weathericon+".png").convert_alpha()
			screen.blit(logo, (0, 0))

        # Display the temperature
		text = fontSm.render(temp+chr(176)+"C", True, colourTemp)
		screen.blit(text, (70, 10))

		# Display countdown
		if countdownenabled == "yes":
			text = fontSm.render(countdown+" days", True, colourCountdown)
			screen.blit(text, (2, 215))

		# Display alarms
		if alarm1enabled == "yes":
			text = fontSm.render(alarm1, True, colourAlarm1Status)
		else:
			text = fontSm.render(alarm1, True, colourAlarm1Dimmed)
		screen.blit(text, (120, 50))
		
		if alarm2enabled == "yes":
			text = fontSm.render(alarm2, True, colourAlarm2Status)
		else:
			text = fontSm.render(alarm2, True, colourAlarm2Dimmed)
		screen.blit(text, (200, 50))

		# Display radio station
		if radio != "off":
			text = fontSm.render(radio, True, colourGeneral)
			screen.blit(text, (200, 215))

		# Display snooze button
		if alarm == "on":
			text = fontSm.render("Snooze", True, colourGeneral)
			pygame.draw.rect(screen, colourWhite, (button_snooze),2)
			text_pos = text.get_rect()
			text_pos.centerx = screen.get_width()/2
			text_pos.top = 220
			screen.blit(text, text_pos)

		# Display snoozing
		if snooze == "on":
			text = fontSm.render("Snoozing until "+snoozetime, True, colourGeneral)
			text_pos = text.get_rect()
			text_pos.centerx = screen.get_width()/2
			text_pos.top = 220
			screen.blit(text, text_pos)

		# Display message
		text = fontSm.render(message, True, colourGeneral)
		text_pos = text.get_rect()
		text_pos.centerx = screen.get_width()/2
		text_pos.top = 150
		screen.blit(text, text_pos)

        # Display the time
		text = font.render(curtime, True, colourTime)
		text_pos = text.get_rect()
		text_pos.centerx = screen.get_width()/2
		text_pos.top = 75
		screen.blit(text, text_pos)

	    # Display the date
		text = fontSm.render(curdate, True, colourDate)
		text_pos = text.get_rect()
		text_pos.centerx = screen.get_width()/2
		text_pos.top = 180
		screen.blit(text, text_pos)

		#text = fontSm.render(chr(176), True, colourDate)
		#screen.blit(text, (0, 0))

		pygame.display.update()

if onpi=="yes":
	GPIO.cleanup()

logging.info('End of main code')


