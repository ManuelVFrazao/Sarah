import socket
import math
import colorsys
import types
import datetime
import threading
import calendar
import math
import re
import random

import pygame
#import numpy as N
#import pygame.surfarray as surfarray

import sarahAI
import sarahMQTT
import sarahMysql
import sarahXBMC
import sarahSerial

class SARaH:
	def __init__(self):
		pygame.init()
		#self.screen = pygame.display.set_mode((320, 240),(pygame.FULLSCREEN))
		self.screen = pygame.display.set_mode((320, 240))
		pygame.display.set_caption("SARaH")
		self.keepRunning = True
		#pygame.mouse.set_visible(False)
		self.mousePressed = False
		self.mousePressPos = (0,0)
		self.mouseReleasedPos = (0,0)
		self.mouseDrag = (0,0)
		self.clock = pygame.time.Clock()
		self.autoCommit = False
		
		self.AI = sarahAI.SarahAI(self)
		self.AIThread = sarahAI.aiThread(self.AI)
		self.AIThread.daemon = True
		self.AIThread.start()
		
		self.MQTT = sarahMQTT.SarahMQTT()
		self.MQTT.client.on_message = self.MQTTReceive
		
		self.AI.mqtt = sarahAI.aiMqtt(self.MQTT.client, "sarah/house")
		
		self.MySQL = sarahMysql.SarahMySQL(self)
		
		self.xbmc = sarahXBMC.SarahXBMC()
		
		self.serial = sarahSerial.SarahSerial()
		self.serialThread = sarahSerial.SerialThread(self.serial)
		self.serialThread.daemon = True
		self.serialThread.start()
		
		self.rooms = [
			#{"name":"Kitchen","lights":[{"name":"Ceiling","lightR":127,"lightG":127,"lightB":127},{"name":"Oven","lightR":127,"lightG":127,"lightB":127},],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"Coffee machine","on":True,"consumption":0},{"name":"Toaster","on":True,"consumption":0}]},
			#{"name":"Living room","lights":[{"name":"Ceiling","lightR":127,"lightG":127,"lightB":127},{"name":"Wall","lightR":127,"lightG":127,"lightB":127},],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0},{"name":"Sound system","on":True,"consumption":0}]},
			#{"name":"Bathroom","lights":[{"name":"Ceiling","lightR":127,"lightG":127,"lightB":127},{"name":"Chandelier","lightR":127,"lightG":127,"lightB":127},],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"Hair dryer","on":True,"consumption":0}]},
			#{"name":"Dining room","lights":[{"name":"Ceiling","lightR":127,"lightG":127,"lightB":127},{"name":"Chandelier","lightR":127,"lightG":127,"lightB":127},],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			#{"name":"Master bedroom","lights":[{"name":"Ceiling","lightR":127,"lightG":127,"lightB":127},{"name":"Right night lamp","lightR":127,"lightG":127,"lightB":127},{"name":"Left night lamp","lightR":127,"lightG":127,"lightB":127},],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			#{"name":"Kid bedroom","lights":[],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			#{"name":"Guest bedroom","lights":[],"temperature":20.0,"currentTemperature":19.5,"outlets":[]},
			#{"name":"Garage","lights":[{"name":"Ceiling","lightR":127,"lightG":127,"lightB":127},{"name":"Lamp","lightR":127,"lightG":127,"lightB":127},],"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"Central Vacuum","on":True,"consumption":0},{"name":"Water heater","on":True,"consumption":0}]},
		]
		
		self.currentRoom = 0
		self.inputsValue = {
			"lightSlider":100,
			"temperatureSlider":20.0,
			"RGBWheel":(0,0, 0,0),
			"musicVolumeSlider":50,
			
			"sarahImage":"",
			
			"waterLeakSensor":"",
			"fireSensor":"",
			"naturalGazSensor":"",
			
			"sensor1":"images/Icons/ghost7.png",
			"sensor1Status":"images/Icons/traffic20.png",
			"sensor2":"images/Icons/ghost7.png",
			"sensor2Status":"images/Icons/traffic20.png",
			"sensor3":"images/Icons/ghost7.png",
			"sensor3Status":"images/Icons/traffic20.png",
		}
		self.inputs = []
		
		self.presets = [
			{
				"name":"Home",
				"action":""
			},
			{
				"name":"Away",
				"action":""
			},
			{
				"name":"Morning",
				"action":""
			},
			{
				"name":"Evening",
				"action":""
			},
			{
				"name":"Night",
				"action":""
			},
			{
				"name":"Movie",
				"action":""
			},
			{
				"name":"Vacation",
				"action":""
			},
			{
				"name":"Party",
				"action":""
			},
		]
		self.customActions = [
			{
				"name":"Make Coffee in the morning",
				"action":"-1,coffee,1",
				"conditions":"True",
				"schedule":21600,
				"keepWaiting":0,
				"triggered":False,
			},
			{
				"name":"Water the garden on Sundays",
				"action":"-1,waterGarden,1",
				"conditions":"weekday == 6",
				"schedule":21600,
				"keepWaiting":0,
				"triggered":False,
			},
			{
				"name":"Clean the floor if not home",
				"action":"-1,cleanFloor,1",
				"conditions":"home == 0",
				"schedule":21600,
				"keepWaiting":True,
				"triggered":False,
			},
			{
				"name":"lock the doors",
				"action":"-1,lockDoor,0;-1,lockDoor,1",
				"conditions":"garageDoorOpen == 0",
				"schedule":21600,
				"keepWaiting":True,
				"triggered":False,
			},
		]
		self.buttonScroll = 0
		
		self.mediaDevices = [
		]
		
		self.passCode = {
			"code":"",
			"state":"passKey",
		}
		
		self.doors = [
			
		]
		self.sensors = {
			"leak":"Triggered",
			"fire":"Missing",
			"gaz":"Normal",
			"security":[
				{"type":"camera","name":"Front Door Cam","status":"Normal","enabled":True},
				{"type":"camera","name":"Yard Cam","status":"Normal","enabled":True},
				{"type":"pirSensor","name":"Hallway PIR","status":"Triggered","enabled":True},
				{"type":"door","name":"Front Door","status":"Normal","enabled":True},
				{"type":"door","name":"Back Door","status":"Normal","enabled":True},
				{"type":"window","name":"Master Bedroom Window","status":"Normal","enabled":True},
				{"type":"window","name":"Kid's Bedroom Window","status":"Normal","enabled":True},
			],
		}
		self.sensorTypes = {
			"camera":"images/Icons/video172.png",
			"pirSensor":"images/Icons/visible11.png",
			"door":"images/Icons/key170.png",
			"window":"images/Icons/image84.png",
		}
		self.sensorStatus = {
			"Normal":"",
			"Missing":"images/Icons/ghost7.png",
			"Triggered":"images/Icons/traffic20.png",
			"Disabled":"images/Icons/flash24.png",
		}
		
		self.gameOfLife = [
		]
		self.gameOfLifeDelay = 10
		
		self.confirmation = {
			"confirm":lambda:None,
			"cancel":lambda:None,
			"title":"Confirm",
			"message":"Please confirm",
		}
		
		self.CurrentPage = "home"
		self.pages = {
			"home":{
				"name":"Home",
				"background":pygame.image.load("images/Backgrounds/3x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("house"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.changePage("sarah"), 68,10, 48,48, icon="images/Icons/microphone83.png"),
					inputButton(self, [lambda:self.changePage("security"), lambda:self.updateSensors()], 126,10, 48,48, icon="images/Icons/key170.png"),
					inputButton(self, lambda:self.changePage("options"), 262,10, 48,48, icon="images/Icons/configuration20.png"),
					
					inputLabel(self, "{0}", [lambda:self.getTime()], 160, 70, fontSize=72, align=(0.5,0)),
					inputLabel(self, "{0}", [lambda:self.getDate()], 160, 150, fontSize=38, align=(0.5,0)),
					inputLabel(self, "{0}", [lambda:self.getFullDate()], 160, 185, fontSize=16, align=(0.5,0)),
					
				]
			},
			"house":{
				"name":"House",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.changePage("customActions"),lambda:self.scrollButtons(0, 3, absolute=True)], 146,10, 48,48, icon="images/Icons/code42.png"),
					#inputButton(self, lambda:self.changePage("multimedia"), 204,10, 48,48, icon="images/Icons/musical115.png"),
					inputButton(self, lambda:self.changePage("house"), 204,10, 48,48, icon="images/Icons/musical115.png"),
					inputButton(self, [lambda:self.changePage("rooms"),lambda:self.scrollButtons(0, 6, absolute=True)], 262,10, 48,48, icon="images/Icons/button10.png"),
					
					inputTextButton(self, [], 20,80, 110,40, "{0}", [lambda:self.presets[self.buttonScroll]["name"]], condition=lambda:self.buttonScroll < len(self.presets)),
					inputTextButton(self, [], 20,130, 110,40, "{0}", [lambda:self.presets[self.buttonScroll+2]["name"]], condition=lambda:self.buttonScroll+2 < len(self.presets)),
					inputTextButton(self, [], 20,180, 110,40, "{0}", [lambda:self.presets[self.buttonScroll+4]["name"]], condition=lambda:self.buttonScroll+4 < len(self.presets)),
					
					inputTextButton(self, [], 140,80, 110,40, "{0}", [lambda:self.presets[self.buttonScroll+1]["name"]], condition=lambda:self.buttonScroll+1 < len(self.presets)),
					inputTextButton(self, [], 140,130, 110,40, "{0}", [lambda:self.presets[self.buttonScroll+3]["name"]], condition=lambda:self.buttonScroll+3 < len(self.presets)),
					inputTextButton(self, [], 140,180, 110,40, "{0}", [lambda:self.presets[self.buttonScroll+5]["name"]], condition=lambda:self.buttonScroll+5 < len(self.presets)),
					
					inputButton(self, lambda:self.scrollButtons(-6, 6, self.presets), 260,80, 40,40, icon="images/Icons/up154.png"),
					inputButton(self, lambda:self.scrollButtons(6, 6, self.presets), 260,180, 40,40, icon="images/Icons/down102.png"),
				]
			},
			"rooms":{
				"name":"Rooms",
				"background":pygame.image.load("images/Backgrounds/1x2.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.scrollButtons(0, 1, absolute=True), lambda:self.changePage("house")], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.scrollButtons(-6), 204,10, 48,48, icon="images/Icons/left204.png"),
					inputButton(self, lambda:self.scrollButtons(6), 262,10, 48,48, icon="images/Icons/right204.png"),
					
					inputTextButton(self, [lambda:self.changePage("lights", self.buttonScroll),lambda:self.scrollButtons(0, 1, absolute=True)], 20,80, 135,40, "{0}", [lambda:self.rooms[self.buttonScroll]["name"]], condition=lambda:self.buttonScroll < len(self.rooms)),
					inputTextButton(self, [lambda:self.changePage("lights", self.buttonScroll+2),lambda:self.scrollButtons(0, 1, absolute=True)], 20,130, 135,40, "{0}", [lambda:self.rooms[self.buttonScroll+2]["name"]], condition=lambda:self.buttonScroll+2 < len(self.rooms)),
					inputTextButton(self, [lambda:self.changePage("lights", self.buttonScroll+4),lambda:self.scrollButtons(0, 1, absolute=True)], 20,180, 135,40, "{0}", [lambda:self.rooms[self.buttonScroll+4]["name"]], condition=lambda:self.buttonScroll+4 < len(self.rooms)),
					
					inputTextButton(self, [lambda:self.changePage("lights", self.buttonScroll+1),lambda:self.scrollButtons(0, 1, absolute=True)], 165,80, 135,40, "{0}", [lambda:self.rooms[self.buttonScroll+1]["name"]], condition=lambda:self.buttonScroll+1 < len(self.rooms)),
					inputTextButton(self, [lambda:self.changePage("lights", self.buttonScroll+3),lambda:self.scrollButtons(0, 1, absolute=True)], 165,130, 135,40, "{0}", [lambda:self.rooms[self.buttonScroll+3]["name"]], condition=lambda:self.buttonScroll+3 < len(self.rooms)),
					inputTextButton(self, [lambda:self.changePage("lights", self.buttonScroll+5),lambda:self.scrollButtons(0, 1, absolute=True)], 165,180, 135,40, "{0}", [lambda:self.rooms[self.buttonScroll+5]["name"]], condition=lambda:self.buttonScroll+5 < len(self.rooms)),
				
					inputLabel(self, "{0} of {1}", [lambda:self.buttonScroll//6+1,lambda:(len(self.rooms)-1)//6+1], 131, 40, fontSize=28, align=(0.5,0.5)),
				]
			},
			"lights":{
				"name":"Lights",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.changePage("rooms"),lambda:self.scrollButtons(0, 6, absolute=True)], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.changePage("lights"),lambda:self.scrollButtons(0, 1, absolute=True)], 146,10, 48,48, icon="images/Icons/lightbulb52.png"),
					inputButton(self, [lambda:self.changePage("temperature"),lambda:self.scrollButtons(0, 1, absolute=True)], 204,10, 48,48, icon="images/Icons/thermometer53.png"),
					inputButton(self, [lambda:self.changePage("outlets"),lambda:self.scrollButtons(0, 1, absolute=True)], 262,10, 48,48, icon="images/Icons/electrical28.png"),
				
					inputSlider(self, "lightSlider", lambda:self.commitValues(), 100, 0, 100, 1, 222,80, 20,100, vertical=True, reversed_=True, condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
					
					inputGrid(self, "RGBWheel", lambda:self.commitValues(), (50,50), 20,80, 100,100, image="images/HSV.png", circle=True, condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
					
					inputLabel(self, "{0}\n{1}%", [lambda:getHexFromRGB(getRGBFromColorWheel( \
						self.inputsValue["RGBWheel"][2], \
						self.inputsValue["RGBWheel"][3], \
						self.inputsValue["lightSlider"] \
						)),lambda:roundTo(self.inputsValue["lightSlider"])], 202, 80, fontSize=20, align=(1,0), condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
					
					inputButton(self, lambda:self.inputs[4].slide(-10,True,True), 252,80, 48,48, icon="images/Icons/up154.png", condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
					inputButton(self, lambda:self.inputs[4].slide(10,True,True), 252,132, 48,48, icon="images/Icons/down102.png", condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
					
					inputButton(self, [lambda:self.scrollButtons(-1, 1, self.rooms[self.currentRoom]["lights"]), lambda:self.sync(resetScroll=False)], 20,190, 30,30, icon="images/Icons/left204.png", condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
					inputButton(self, [lambda:self.scrollButtons(1, 1, self.rooms[self.currentRoom]["lights"]), lambda:self.sync(resetScroll=False)], 270,190, 30,30, icon="images/Icons/right204.png", condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0),
				
					inputLabel(self, "{0} ({1} of {2})", [lambda:self.rooms[self.currentRoom]["lights"][self.buttonScroll]["name"], lambda:self.buttonScroll+1,lambda:len(self.rooms[self.currentRoom]["lights"])], 160,205, align=(0.5,0.5), condition=lambda:len(self.rooms[self.currentRoom]["lights"])>0)
				]
			},
			"temperature":{
				"name":"Temperature",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.changePage("rooms"),lambda:self.scrollButtons(0, 6, absolute=True)], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.changePage("lights"),lambda:self.scrollButtons(0, 1, absolute=True)], 146,10, 48,48, icon="images/Icons/lightbulb52.png"),
					inputButton(self, [lambda:self.changePage("temperature"),lambda:self.scrollButtons(0, 1, absolute=True)], 204,10, 48,48, icon="images/Icons/thermometer53.png"),
					inputButton(self, [lambda:self.changePage("outlets"),lambda:self.scrollButtons(0, 1, absolute=True)], 262,10, 48,48, icon="images/Icons/electrical28.png"),
				
					inputSlider(self, "temperatureSlider", lambda:self.commitValues(), 20, 17, 23, 0.5, 222,80, 20,100, vertical=True, reversed_=True, condition=lambda:"temperature" in self.rooms[self.currentRoom]),
					
					inputLabel(self, "Humidity: {0}%\nCurrent: {1}°\nSet: {2}°", [lambda:float(self.rooms[self.currentRoom]["currentHumidity"]),lambda:float(self.rooms[self.currentRoom]["currentTemperature"]),lambda:float(self.inputsValue["temperatureSlider"])], 202, 80, fontSize=22, align=(1,0), condition=lambda:"temperature" in self.rooms[self.currentRoom]),
					
					inputButton(self, lambda:self.inputs[4].slide(-0.5,True,True), 252,80, 48,48, icon="images/Icons/up154.png", condition=lambda:"temperature" in self.rooms[self.currentRoom]),
					inputButton(self, lambda:self.inputs[4].slide(0.5,True,True), 252,132, 48,48, icon="images/Icons/down102.png", condition=lambda:"temperature" in self.rooms[self.currentRoom]),
					
				]
			},
			"outlets":{
				"name":"Outlets",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.scrollButtons(0, 6, absolute=True), lambda:self.changePage("rooms")], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.scrollButtons(0, 1, absolute=True), lambda:self.changePage("lights")], 146,10, 48,48, icon="images/Icons/lightbulb52.png"),
					inputButton(self, [lambda:self.changePage("temperature"),lambda:self.scrollButtons(0, 1, absolute=True)], 204,10, 48,48, icon="images/Icons/thermometer53.png"),
					inputButton(self, [lambda:self.scrollButtons(0, 1, absolute=True), lambda:self.changePage("outlets")], 262,10, 48,48, icon="images/Icons/electrical28.png"),
				
					inputButton(self, lambda:self.MQTTSend("sarah/house", "toggleOutlet,{0}".format(self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["serialNum"])), 20,80, 48,48, icon="images/Icons/flash24.png", condition=lambda:len(self.rooms[self.currentRoom]["outlets"])>0),
					inputButton(self, lambda:self.scrollButtons(-1, 1, self.rooms[self.currentRoom]["outlets"]), 20,172, 48,48, icon="images/Icons/left204.png", condition=lambda:len(self.rooms[self.currentRoom]["outlets"])>0),
					inputButton(self, lambda:self.scrollButtons(1, 1, self.rooms[self.currentRoom]["outlets"]), 252,172, 48,48, icon="images/Icons/right204.png", condition=lambda:len(self.rooms[self.currentRoom]["outlets"])>0),
					
					inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["name"],lambda:"ON" if self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["on"] else "OFF"], 78,80, fontSize=20, condition=lambda:len(self.rooms[self.currentRoom]["outlets"])>0),
					inputLabel(self, "Consumption: {0}", [lambda:self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["consumption"]], 20,138, fontSize=20, condition=lambda:len(self.rooms[self.currentRoom]["outlets"])>0),
					
					inputLabel(self, "{0} of {1}", [lambda:self.buttonScroll+1,lambda:len(self.rooms[self.currentRoom]["outlets"])], 160,196, fontSize=20, align=(0.5,0.5), condition=lambda:len(self.rooms[self.currentRoom]["outlets"])>0),
				]
			},
			"sarah":{
				"name":"Sarah",
				"background":pygame.image.load("images/Backgrounds/1x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.AIListen(), 262,10, 48,48, icon="images/Icons/microphone83.png"),
					
					inputGameOfLife(self, 20,80),
					
					inputLabel(self, "Status:\n{0}", [lambda:"{0}".format(str(self.AI.out)) if str(self.AI.out) else "Idle"], 160, 40, align=(0.5,0.5)),
					inputLabel(self, "{0}\n{1}", [lambda:"You said: {0}".format(str(self.AI.recognizedText)) if str(self.AI.recognizedText) else "", lambda:"Searching for: {0}".format(str(self.AI.currentQuery)) if str(self.AI.currentQuery) else ""], 20, 80, w=280, align=(0,0)),
					
				]
			},
			"sarahResults":{
				"name":"Sarah Results",
				"background":pygame.image.load("images/Backgrounds/1x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.changePage("sarah"),lambda:self.AIListen()], 262,10, 48,48, icon="images/Icons/microphone83.png"),
					
					inputGameOfLife(self, 20,80),
					
					inputLabel(self, "Status:\n{0}", [lambda:"{0}".format(str(self.AI.out)) if str(self.AI.out) else "Idle"], 160, 40, align=(0.5,0.5)),
					#inputLabel(self, "{0}", [lambda:"You said: {0}".format(str(self.AI.recognizedText)) if str(self.AI.recognizedText) else ""], 20, 80, w=280, align=(0,0)),
					inputImage(self, "sarahImage", 160,150,280,140, (0.5,0.5)),
				]
			},
			"security":{
				"name":"Security",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.scrollButtons(0, 3, absolute=True), lambda:self.updateSensors(), lambda:self.changePage("sensors")], 146,10, 48,48, icon="images/Icons/shield91.png"),
					inputButton(self, lambda:self.changePage("doors"), 204,10, 48,48, icon="images/Icons/key170.png"),
					inputButton(self, lambda:self.askConfirmation( \
						[lambda:self.changePage("security")], \
						[lambda:self.changePage("keypad"), lambda:self.serialThread.send("LockHouse")], \
						"Lock the house", "Do you want to put the house in locked mode?"), \
						262,10, 48,48, icon="images/Icons/locked55.png"),
					
					inputButton(self, lambda:None, 20,80, 40,40, icon="images/Icons/ink16.png"),
					inputButton(self, lambda:None, 20,130, 40,40, icon="images/Icons/tree108.png"),
					inputButton(self, lambda:None, 20,180, 40,40, icon="images/Icons/cloud301.png"),
					
					inputTextButton(self, [], 70,80, 180,40, "Water leak"),
					inputTextButton(self, [], 70,130, 180,40, "Fire"),
					inputTextButton(self, [], 70,180, 180,40, "Natural gaz"),
					
					inputImage(self, "waterLeakSensor", 260,80, 40,40),
					inputImage(self, "fireSensor", 260,130, 40,40),
					inputImage(self, "naturalGazSensor", 260,180, 40,40),
					
					
				]
			},
			"sensors":{
				"name":"Security Sensors",
				"background":pygame.image.load("images/Backgrounds/1x2.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("security"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.scrollButtons(-3, 3, self.sensors["security"]), lambda:self.updateSensors()], 204,10, 48,48, icon="images/Icons/left204.png"),
					inputButton(self, [lambda:self.scrollButtons(3, 3, self.sensors["security"]), lambda:self.updateSensors()], 262,10, 48,48, icon="images/Icons/right204.png"),
				
					inputImage(self, "sensor1", 20,80, 40,40, condition=lambda:len(self.sensors["security"])>self.buttonScroll),
					inputImage(self, "sensor2", 20,130, 40,40, condition=lambda:len(self.sensors["security"])>self.buttonScroll+1),
					inputImage(self, "sensor3", 20,180, 40,40, condition=lambda:len(self.sensors["security"])>self.buttonScroll+2),
					
					inputTextButton(self, [], 70,80, 180,40, "{0}", [lambda:self.sensors["security"][self.buttonScroll]["name"]], maxChar=21, condition=lambda:len(self.sensors["security"])>self.buttonScroll),
					inputTextButton(self, [], 70,130, 180,40, "{0}", [lambda:self.sensors["security"][self.buttonScroll+1]["name"]], maxChar=21, condition=lambda:len(self.sensors["security"])>self.buttonScroll+1),
					inputTextButton(self, [], 70,180, 180,40, "{0}", [lambda:self.sensors["security"][self.buttonScroll+2]["name"]], maxChar=21, condition=lambda:len(self.sensors["security"])>self.buttonScroll+2),
					
					inputImage(self, "sensor1Status", 260,80, 40,40, condition=lambda:len(self.sensors["security"])>self.buttonScroll),
					inputImage(self, "sensor2Status", 260,130, 40,40, condition=lambda:len(self.sensors["security"])>self.buttonScroll+1),
					inputImage(self, "sensor3Status", 260,180, 40,40, condition=lambda:len(self.sensors["security"])>self.buttonScroll+2),
					
					inputLabel(self, "{0} of {1}", [lambda:self.buttonScroll//3+1,lambda:(len(self.sensors["security"])-1)//3+1], 131, 40, fontSize=28, align=(0.5,0.5)),
				]
			},
			"doors":{
				"name":"Doors",
				"background":pygame.image.load("images/Backgrounds/1x0.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("security"), 10,10, 48,48, icon="images/Icons/house139.png"),
				]
			},
			"keypad":{
				"name":"Keypad",
				"background":pygame.image.load("images/Backgrounds/0x0.png").convert_alpha(),
				"inputs":[
					inputLabel(self, "{0}", [lambda:self.codeDigits()], 160, 40, fontSize=32, align=(0.5,0.5)),
					
					inputTextButton(self, lambda:self.codeDigit(1), 20,80, 48,40, "1"),
					inputTextButton(self, lambda:self.codeDigit(4), 20,130, 48,40, "4"),
					inputTextButton(self, lambda:self.codeDigit(7), 20,180, 48,40, "7"),
					
					inputTextButton(self, lambda:self.codeDigit(2), 78,80, 48,40, "2"),
					inputTextButton(self, lambda:self.codeDigit(5), 78,130, 48,40, "5"),
					inputTextButton(self, lambda:self.codeDigit(8), 78,180, 48,40, "8"),
					
					inputTextButton(self, lambda:self.codeDigit(3), 136,80, 48,40, "3"),
					inputTextButton(self, lambda:self.codeDigit(6), 136,130, 48,40, "6"),
					inputTextButton(self, lambda:self.codeDigit(9), 136,180, 48,40, "9"),
					
					inputTextButton(self, lambda:self.codeDigit(0), 194,80, 48,40, "0"),
					inputTextButton(self, lambda:self.codeConfirm(), 194,130, 106,90, "Enter"),
					
					inputTextButton(self, lambda:self.codeCancel(), 252,80, 48,40, "Back"),
				
				]
			},
			"customActions":{
				"name":"Custom Actions",
				"background":pygame.image.load("images/Backgrounds/1x2.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.scrollButtons(0, 6, absolute=True), lambda:self.changePage("house")], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.scrollButtons(-3, 3, self.customActions), 204,10, 48,48, icon="images/Icons/left204.png"),
					inputButton(self, lambda:self.scrollButtons(3, 3, self.customActions), 262,10, 48,48, icon="images/Icons/right204.png"),
				
					inputTextButton(self, lambda:self.triggerCustomActions(self.buttonScroll), 20,80, 230,40, "{0}", [lambda:self.customActions[self.buttonScroll]["name"]], maxChar=27, condition=lambda:len(self.customActions)>self.buttonScroll),
					inputButton(self, lambda:self.editCustomActions(self.buttonScroll), 260,80, 40,40, icon="images/Icons/configuration20.png", condition=lambda:len(self.customActions)>self.buttonScroll),
				
					inputTextButton(self, lambda:self.triggerCustomActions(self.buttonScroll+1), 20,130, 230,40, "{0}", [lambda:self.customActions[self.buttonScroll+1]["name"]], maxChar=27, condition=lambda:len(self.customActions)>self.buttonScroll+1),
					inputButton(self, lambda:self.editCustomActions(self.buttonScroll+1), 260,130, 40,40, icon="images/Icons/configuration20.png", condition=lambda:len(self.customActions)>self.buttonScroll+1),
				
					inputTextButton(self, lambda:self.triggerCustomActions(self.buttonScroll+2), 20,180, 230,40, "{0}", [lambda:self.customActions[self.buttonScroll+2]["name"]], maxChar=27, condition=lambda:len(self.customActions)>self.buttonScroll+2),
					inputButton(self, lambda:self.editCustomActions(self.buttonScroll+2), 260,180, 40,40, icon="images/Icons/configuration20.png", condition=lambda:len(self.customActions)>self.buttonScroll+2),
					
					inputLabel(self, "{0} of {1}", [lambda:self.buttonScroll//3+1,lambda:(len(self.customActions)-1)//3+1], 131, 40, fontSize=28, align=(0.5,0.5)),
				]
			},
			"customActionsInfo":{
				"name":"Custom Actions Info",
				"background":pygame.image.load("images/Backgrounds/1x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.deleteCustomAction(), 262,10, 48,48, icon="images/Icons/cross100.png"),
				]
			},
			"options":{
				"name":"Options",
				"background":pygame.image.load("images/Backgrounds/1x0.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					
					inputToggle(self, lambda:self.AIThread.keepListening, lambda:self.AIKeepListening(), 150,120,10),
					inputToggle(self, lambda:self.AI.keepListening, lambda:self.AIKeepTriggered(), 150,150,10),
					inputToggle(self, lambda:self.AI.isTriggered, lambda:self.AIIsTriggered(), 150,180,10),
					inputToggle(self, lambda:self.AI.canSearch, lambda:self.AICanSearch(), 150,210,10),
				
					inputLabel(self, "Sarah", [], 90, 80, align=(0.5,0)),
					inputLabel(self, "Autolisten", [], 20, 120, align=(0,0.5)),
					inputLabel(self, "Autotrigger", [], 20, 150, align=(0,0.5)),
					inputLabel(self, "Triggered", [], 20, 180, align=(0,0.5)),
					inputLabel(self, "Search", [], 20, 210, align=(0,0.5)),
					
				]
			},
			"confirm":{
				"name":"Confirm",
				"background":pygame.image.load("images/Backgrounds/1x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.cancelConfirmation(), 10,10, 48,48, icon="images/Icons/dislike15.png"),
					inputButton(self, lambda:self.confirmConfirmation(), 262,10, 48,48, icon="images/Icons/like77.png"),
					
					inputLabel(self, "{0}", [lambda:self.confirmation["title"]], 160, 40, align=(0.5,0.5)),
					inputLabel(self, "{0}", [lambda:self.confirmation["message"]], 160, 80, w=280,align=(0.5,0)),
				]
			},
		}
		self.MySQL.load()
		self.changePage("home")
	
	def changePage(self, page, room=None, syncAllInputs=True):
		self.inputs = self.pages[page]["inputs"]
		self.CurrentPage = page
		if room != None:
			self.changeRoom(room)
		self.sync(syncAllInputs)
			
	def changeRoom(self, room, syncAllInputs=True):
		self.currentRoom = room
		self.sync(syncAllInputs)
		
	def scrollButtons(self, n, numButtons=6, buttons=None, absolute=False):
		if not buttons:
			buttons = self.rooms
		if absolute:
			self.buttonScroll = 0
		self.buttonScroll = max(min(self.buttonScroll+n,len(buttons)-1),0)//numButtons*numButtons
		print(self.buttonScroll)
	
	def preset(self, num):
		print(num)
		return
	
	def getTime(self):
		h = str(datetime.datetime.now().hour)
		m = str(datetime.datetime.now().minute)
		s = str(datetime.datetime.now().second)
		if len(h) == 1:
			h = "0"+h
		if len(m) == 1:
			m = "0"+m
		if len(s) == 1:
			s = "0"+s
		return "{0}:{1}:{2}".format(h, m, s)
		
	def getDate(self):
		d = str(datetime.datetime.now().day)
		m = str(datetime.datetime.now().month)
		y = str(datetime.datetime.now().year)
		if len(d) == 1:
			d = "0"+d
		if len(m) == 1:
			m = "0"+m
		return "{0}/{1}/{2}".format(d, m, y)
		
	def getFullDate(self):
		wd = str(calendar.day_name[datetime.datetime.now().weekday()])
		d = str(datetime.datetime.now().day)
		m = str(calendar.month_name[datetime.datetime.now().month])
		y = str(datetime.datetime.now().year)
		if 4 <= datetime.datetime.now().day <= 20 or 24 <= datetime.datetime.now().day <= 30:
			suffix = "th"
		else:
			suffix = ["st", "nd", "rd"][(int(d) % 10) - 1]
		return "{0}, {1} the {2}{3} {4}".format(wd, m, d, suffix, y)
		
	def codeDigits(self):
		if self.passCode["state"] == "passKey":
			return ("*" * len(self.passCode["code"]))[0:18]
		else:
			return self.passCode["code"][0:18]
		
	def codeDigit(self, digit):
		self.passCode["code"] = self.passCode["code"] + str(digit)
		
	def codeCancel(self):
		if self.passCode["state"] == "passKey":
			self.passCode["code"] = self.passCode["code"][0:-1]
			
	def codeConfirm(self):
		if self.passCode["state"] == "passKey":
			if self.passCode["code"]:
				self.serial.send(bytes("UnlockHouse {0}".format(self.passCode["code"]), 'utf-8'))
				self.passCode["code"] = ""
				
				#disarm the system
				#self.MQTTSend("sarah/house", "-1,disarm,1")
				
				#Bad idea to send a disarm signal over the network, The
				#security system control panel will be connected through
				#serial
	def run(self):
		self.clock.tick(30)
		#pygame.draw.rect(self.screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))
		if pygame.mouse.get_pressed()[0]:
			if self.mousePressed == False:
				self.mousePressed = True
				self.mouseDown()
		else:
			if self.mousePressed == True:
				self.mousePressed = False
				self.mouseUp()
		
		self.update()
		self.draw()
				
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.keepRunning = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				self.keepRunning = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				print("Space")
				
	def mouseDown(self):
		x, y = pygame.mouse.get_pos()
		print("Mouse down",x,y)
		self.mousePressedPos = (x, y)
		for inp in self.inputs:
			inp.mouseDown(x,y)
		
	def mouseUp(self):
		x, y = pygame.mouse.get_pos()
		print("Mouse up",x,y)
		self.mouseDrag = (x-self.mousePressedPos[0], y-self.mousePressedPos[1])
		print("Dragged",self.mouseDrag)
		self.mouseReleasedPos = (x, y)
		for inp in self.inputs:
			inp.mouseUp(x,y)
		
	def update(self):
		#self.inputs[0].slide(-1)
		for inp in self.inputs:
			inp.update()
		self.updateGameOfLife()
		#serialCom = self.serial.receive()
		#if serialCom:
		#	print(serialCom)
		serialCom = self.serialThread.pop()
		if serialCom:
			print(serialCom)
		
	def draw(self):
		#print("draw")
		self.screen.fill((0,0,0))
		#pygame.draw.rect(self.screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))
		if "background" in self.pages[self.CurrentPage]:
			self.screen.blit(self.pages[self.CurrentPage]["background"], (0,0))
		else:
			self.screen.fill((0,0,0))
		for inp in self.inputs:
			inp.draw()
			
	def commitValues(self):
		room = self.rooms[self.currentRoom]
		if "temperature" in room:
			room["temperature"] = self.inputsValue["temperatureSlider"]
		colorWheel = self.inputsValue["RGBWheel"]
		
		roomColor = getRGBFromColorWheel(colorWheel[2],colorWheel[3],self.inputsValue["lightSlider"])
		#print(roomColor)
		if len(room["lights"]) > self.buttonScroll:
			room["lights"][self.buttonScroll]["lightR"] = roomColor[0]
			room["lights"][self.buttonScroll]["lightG"] = roomColor[1]
			room["lights"][self.buttonScroll]["lightB"] = roomColor[2]
		print(roomColor, colorWheel)
		
		if "temperature" in room:
			self.MQTTSend("sarah/house", "temperature,{0},{1}".format(
				str(room["heaterSerialNum"]), str(room["temperature"])))
		if  len(room["lights"]) > self.buttonScroll:
			self.MQTTSend("sarah/house", "light,{0},{1},{2},{3}".format(
				str(room["lights"][self.buttonScroll]["serialNum"]),
				str(room["lights"][self.buttonScroll]["lightR"]),
				str(room["lights"][self.buttonScroll]["lightG"]),
				str(room["lights"][self.buttonScroll]["lightB"])))
		
		self.MQTTSend("sarah/house", "-1,musicVolume,{0}".format(str(self.inputsValue["musicVolumeSlider"])))
		
	def sync(self, syncAllInputs=True, resetScroll=True):
		room = self.rooms[self.currentRoom]
		if "temperature" in room:
			self.inputsValue["temperatureSlider"] = room["temperature"]
		colorWheel = self.inputsValue["RGBWheel"]
		if resetScroll:
			self.buttonScroll = 0
		if len(room["lights"]) > 0:
			roomColor = colorsys.rgb_to_hsv(float(room["lights"][self.buttonScroll]["lightR"]), float(room["lights"][self.buttonScroll]["lightG"]), float(room["lights"][self.buttonScroll]["lightB"]))
		else: roomColor = (0,0,0)
		#print(roomColor)
		h = roomColor[0]*(math.pi*2)
		if h > math.pi:
			h = -math.pi*2+h
		s = roomColor[1]*50
		nx = math.cos(h)*s+50
		ny = math.sin(h)*s+50
		self.inputsValue["RGBWheel"] = (nx, ny, h, roomColor[1]*50)
		self.inputsValue["lightSlider"] = roomColor[2]/255*100
		if syncAllInputs:
			for inp in self.inputs:
				inp.sync()
				
	def AIKeepListening(self):
		self.AIThread.keepListening = not self.AIThread.keepListening
		
	def AIKeepTriggered(self):
		self.AI.keepListening = not self.AI.keepListening
		
	def AIIsTriggered(self):
		self.AI.isTriggered = not self.AI.isTriggered
		
	def AICanSearch(self):
		self.AI.canSearch = not self.AI.canSearch
		
	def AIListen(self):
		if not self.AIThread.listen:
			if self.AI.keepListening:
				self.AI.isTriggered = True
			self.AIThread.listen = True
			self.generateGameOfLife(datetime.datetime.now())
		else:
			self.AI.stopTalking()
			
		
			
	def MQTTReceive(self, client, userdata, msg):
		print(msg.topic+" "+str(msg.payload))
		#for i in msg.payload.decode("utf-8").split(";"):
			#print(i)
			#command = i.split(",")
			#if int(command[0]) >= 0:
				#if command[1] == "temperature":
					#self.rooms[int(command[0])]["temperature"] = min(max(float(command[2]), 17), 23)
				#if command[1] == "lightR":
					#if len(command) > 3:
						#self.rooms[int(command[0])]["lights"][int(command[3])]["lightR"] = min(max(float(command[2]), 0), 255)
					#else:
						#for i in range(0, len(self.rooms[int(command[0])]["lights"])):
							#self.rooms[int(command[0])]["lights"][i]["lightR"] = min(max(float(command[2]), 0), 255)
				#if command[1] == "lightG":
					#if len(command) > 3:
						#self.rooms[int(command[0])]["lights"][int(command[3])]["lightG"] = min(max(float(command[2]), 0), 255)
					#else:
						#for i in range(0, len(self.rooms[int(command[0])]["lights"])):
							#self.rooms[int(command[0])]["lights"][i]["lightG"] = min(max(float(command[2]), 0), 255)
				#if command[1] == "lightB":
					#if len(command) > 3:
						#self.rooms[int(command[0])]["lights"][int(command[3])]["lightB"] = min(max(float(command[2]), 0), 255)
					#else:
						#for i in range(0, len(self.rooms[int(command[0])]["lights"])):
							#self.rooms[int(command[0])]["lights"][i]["lightB"] = min(max(float(command[2]), 0), 255)
				#if command[1] == "outletOn":
					#self.turnOutletOn(int(command[0]), int(command[2]), commit=False)
				#if command[1] == "outletOff":
					#self.turnOutletOff(int(command[0]), int(command[2]), commit=False)
				#if command[1] == "outletConsumption":
					#self.setOutletConsumption(int(command[0]), int(command[2]), float(command[3]))
			#else:
				#if command[1] == "musicVolume":
					#self.inputsValue["musicVolumeSlider"] = int(command[2])
					##self.sync(syncAllInputs=True,resetScroll=False)
				#if command[1] == "musicStatus":
					#if int(command[2]) == 0:
						#self.music["status"] = "Stopped"
						#self.music["playing"] = False
					#elif int(command[2]) == 1:
						#self.music["status"] = "Playing"
						#self.music["playing"] = True
					#elif int(command[2]) == 2:
						#self.music["status"] = "Paused"
						#self.music["playing"] = False
					##self.sync(syncAllInputs=True,resetScroll=False)
				#if command[1] == "musicLoop":
					#self.music["loop"] = int(command[2]) == 1
					##self.sync(syncAllInputs=True)
				#if command[1] == "musicShuffle":
					#self.music["shuffle"] = int(command[2]) == 1
					##self.sync(syncAllInputs=True,resetScroll=False)
				#if command[1] == "musicTitle":
					#t = str(command[2])
					#for i in range(3, len(command)):
						#t = t+","+str(command[i])
					#self.music["title"] = str(t)
					##self.sync(syncAllInputs=True,resetScroll=False)
				#if command[1] == "musicArtist":
					#t = str(command[2])
					#for i in range(3, len(command)):
						#t = t+","+str(command[i])
					#self.music["title"] = str(t)
					##self.sync(syncAllInputs=True,resetScroll=False)
				#if command[1] == "musicAlbum":
					#t = str(command[2])
					#for i in range(3, len(command)):
						#t = t+","+str(command[i])
					#self.music["title"] = str(t)
					##self.sync(syncAllInputs=True,resetScroll=False)
					
		
		command = msg.payload.decode("utf-8").split(",")
		if command[0] == "light":
			if len(command) == 5:
				ser = command[1]
				r = command[2]
				g = command[3]
				b = command[4]
				
				light = self.findSerialNum(ser)
				if light:
					light["lightR"] = min(max(float(r), 0), 255)
					light["lightG"] = min(max(float(g), 0), 255)
					light["lightB"] = min(max(float(b), 0), 255)
		elif command[0] == "temperature":
			if len(command) == 3:
				ser = command[1]
				temp = command[2]
				
				heater = self.findSerialNum(ser)
				if heater:
					heater["temperature"] = min(max(float(temp), 17), 23)
		elif command[0] == "currentTemperature":
			if len(command) == 4:
				ser = command[1]
				temp = command[2]
				humidity = command[3]
				
				heater = self.findSerialNum(ser)
				if heater:
					heater["currentTemperature"] = temp
					heater["currentHumidity"] = humidity
		elif command[0] == "outlet":
			if len(command) == 3:
				ser = command[1]
				state = command[2]
				
				outlet = self.findSerialNum(ser)
				if outlet:
					outlet["on"] = state
		elif command[0] == "toggleOutlet":
			if len(command) == 2:
				ser = command[1]
				
				outlet = self.findSerialNum(ser)
				if outlet:
					outlet["on"] = not outlet["on"]
		elif command[0] == "outletConsumption":
			if len(command) == 3:
				ser = command[1]
				consumption = command[2]
				
				outlet = self.findSerialNum(ser)
				if outlet:
					outlet["consumption"] = consumption
				
				
		self.sync(syncAllInputs=True,resetScroll=False)
		
	def MQTTSend(self, topic, msg):
		self.MQTT.client.publish(topic, msg)
		
	def findSerialNum(self, ser):
		if ser[0:2] == "LI":
			for room in self.rooms:
				for light in room["lights"]:
					if ser == light["serialNum"]:
						return light
		elif ser[0:2] == "HE":
			for room in self.rooms:
				if "heaterSerialNum" in room:
					if ser == room["heaterSerialNum"]:
						return room
		elif ser[0:2] == "OU":
			for room in self.rooms:
				for outlet in room["outlets"]:
					if ser == outlet["serialNum"]:
						return outlet
	
	def toggleOutlet(self, room, outlet, commit=True):
		self.rooms[room]["outlets"][outlet]["on"] = not self.rooms[room]["outlets"][outlet]["on"]
		if commit:
			if self.rooms[room]["outlets"][outlet]["on"]:
				self.MQTTSend("sarah/house", "{0},outletOn,{1}".format(room,outlet))
			else:
				self.MQTTSend("sarah/house", "{0},outletOff,{1}".format(room,outlet))
				
	def setOutletConsumption(self, room, outlet, consumption=0):
		self.rooms[room]["outlets"][outlet]["consumption"] = consumption
		
	def createCustomAction(self, name, action, conditions, schedule):
		self.customActions = self.customActions + [
			{
				"name":name,
				"action":action,
				"conditions":eval("lambda:"+str(conditions)),
				"schedule":schedule,
			},
		]
		
	def triggerCustomActions(self, num):
		return
		
	def editCustomActions(self, num):
		return
		
	def generateGameOfLife(self, seed):
		width = 28
		height = 14
		random.seed(seed)
		self.gameOfLife = []
		for y in range(0,height+1):
			self.gameOfLife = self.gameOfLife + [[]]
			for x in range(0,width+1):
				self.gameOfLife[y] = self.gameOfLife[y] + [random.randint(0, 1) == 1]
		
	def updateGameOfLife(self):
		if self.gameOfLifeDelay > 0:
			self.gameOfLifeDelay = self.gameOfLifeDelay-1
			return
		self.gameOfLifeDelay = 1
		
		newGameOfLife = self.gameOfLife.copy()
		if self.AIThread.listen:
			for y, row in enumerate(self.gameOfLife):
				for x, cell in enumerate(row):
					neighbours = 0
					
					if x > 0:
						if self.gameOfLife[y] [x-1]:
							neighbours = neighbours+1
						if y > 0:
							if self.gameOfLife[y-1] [x-1]:
								neighbours = neighbours+1
						if y < len(self.gameOfLife)-1:
							if self.gameOfLife[y+1] [x-1]:
								neighbours = neighbours+1
					if x < len(row)-1:
						if self.gameOfLife[y] [x+1]:
							neighbours = neighbours+1
						if y > 0:
							if self.gameOfLife[y-1] [x+1]:
								neighbours = neighbours+1
						if y < len(self.gameOfLife)-1:
							if self.gameOfLife[y+1] [x+1]:
								neighbours = neighbours+1
					if y > 0:
						if self.gameOfLife[y-1] [x]:
							neighbours = neighbours+1
					if y < len(self.gameOfLife)-1:
						if self.gameOfLife[y+1] [x]:
							neighbours = neighbours+1
						
					if neighbours > 3:
						newGameOfLife[y] [x] = False
					elif neighbours < 2:
						newGameOfLife[y] [x] = False
					if neighbours == 3:
						newGameOfLife[y] [x] = True
			self.gameOfLife = newGameOfLife
		else:
			self.gameOfLife = []
			
	def askConfirmation(self, cancelAction=[], confirmAction=[], title="", message=""):
		self.confirmation["cancel"] = cancelAction
		self.confirmation["confirm"] = confirmAction
		self.confirmation["title"] = title
		self.confirmation["message"] = message
		self.changePage("confirm")
		
	def cancelConfirmation(self):
		for i in self.confirmation["cancel"]:
			i()
	def confirmConfirmation(self):
		for i in self.confirmation["confirm"]:
			i()
			
	def updateSensors(self):
		self.inputsValue["waterLeakSensor"] = self.sensorStatus[self.sensors["leak"]]
		self.inputsValue["fireSensor"] = self.sensorStatus[self.sensors["fire"]]
		self.inputsValue["naturalGazSensor"] = self.sensorStatus[self.sensors["gaz"]]
		
		if len(self.sensors["security"])>self.buttonScroll:
			self.inputsValue["sensor1"] = self.sensorTypes[self.sensors["security"][self.buttonScroll]["type"]]
			self.inputsValue["sensor1Status"] = self.sensorStatus[self.sensors["security"][self.buttonScroll]["status"]]
		if len(self.sensors["security"])>self.buttonScroll+1:
			self.inputsValue["sensor2"] = self.sensorTypes[self.sensors["security"][self.buttonScroll+1]["type"]]
			self.inputsValue["sensor2Status"] = self.sensorStatus[self.sensors["security"][self.buttonScroll]["status"]]
		if len(self.sensors["security"])>self.buttonScroll+2:
			self.inputsValue["sensor3"] = self.sensorTypes[self.sensors["security"][self.buttonScroll+2]["type"]]
			self.inputsValue["sensor3Status"] = self.sensorStatus[self.sensors["security"][self.buttonScroll]["status"]]
		
		for inp in self.inputs:
			inp.sync()
		
	
class inputSlider():
	def __init__(self, class_, var, action=None, v=0, minVal=0, maxVal=100, increments=1, x=0, y=0, w=0, h=0, vertical=False, reversed_=False, color=(127,127,127), cursorColor=(255,255,255), activeCursorColor=(127,127,255), condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.var = var
		self.action = action
		self.value = v - minVal
		if reversed_:
			self.value = maxVal - v
		self.min = minVal
		self.max = maxVal - minVal
		self.increments = increments
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.vertical = vertical
		self.reversed = reversed_
		self.color = color
		self.cursorColor = cursorColor
		self.activeCursorColor = activeCursorColor
		self.active = False
		self.condition = condition
	def slide(self, amount=0, commit=False, act=False):
		self.value = max(min(roundTo(self.value+amount, self.increments), self.max), 0)
		if commit:
			self.commit()
			if act and self.action:
				self.action()
	def slideTo(self, amount=0, commit=False, act=False):
		self.value = max(min(roundTo(amount, self.increments), self.max), 0)
		if commit:
			self.commit()
			if act and self.action:
				self.action()
	def commit(self):
		if self.reversed:
			self.class_.inputsValue[self.var] = (self.max-self.value)+self.min
		else:
			self.class_.inputsValue[self.var] = self.value+self.min
		if self.class_.autoCommit:
			if self.action:
				self.action()
	def sync(self):
		if not self.condition():
			return
		if self.reversed:
			self.value = self.max-(self.class_.inputsValue[self.var]-self.min)
		else:
			self.value = self.class_.inputsValue[self.var]-self.min
	def getVal(self):
		val = self.value+self.min
		if self.reversed:
			val = (self.max-self.value)+self.min
		return val
	def draw(self):
		if not self.condition():
			return
		color = self.cursorColor
		if self.active:
			color = self.activeCursorColor
		pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x, self.y, self.w, self.h))
		if self.vertical:
			y = (self.value/self.max)*self.h+self.y
			pygame.draw.rect(self.screen, color, pygame.Rect(self.x-5, y-5, self.w+10, 10))
		else:
			x = (self.value/self.max)*self.w+self.x
			pygame.draw.rect(self.screen, color, pygame.Rect(x-5, self.y-5, 10, self.h+10))
	def update(self):
		if not self.condition():
			return
		if self.active:
			x, y = pygame.mouse.get_pos()
			if self.vertical:
				self.slideTo(((y-self.y)/self.h)*self.max)
			else:
				self.slideTo(((x-self.x)/self.w)*self.max)
			self.commit()
	def mouseInside(self, x, y):
		if boxCollision(self.x-5, self.y-5, self.x+self.w+5, self.y+self.h+5, x, y):
			return True
		return False
	def mouseDown(self, x, y):
		if not self.condition():
			return
		if self.mouseInside(x, y):
			self.active = True
	def mouseUp(self, x, y):
		if self.active:
			self.active = False
			self.commit()
			if self.action:
				self.action()
				
			
class inputButton():
	def __init__(self, class_, action=None, x=0, y=0, w=0, h=0, icon=None, activeIcon=None, condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.action = action
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.icon = None
		self.activeIcon = None
		if icon:
			self.icon = pygame.image.load(icon).convert_alpha()
			self.icon = pygame.transform.smoothscale(self.icon,(self.w,self.h))
		if activeIcon:
			self.activeIcon = pygame.image.load(activeIcon).convert_alpha()
			self.activeIcon = pygame.transform.smoothscale(self.activeIcon,(self.w,self.h))
		self.active = False
		self.condition = condition
	def draw(self):
		if not self.condition():
			return
		if self.icon:
			if self.active and self.activeIcon:
				self.screen.blit(self.activeIcon, (self.x, self.y))
			else:
				self.screen.blit(self.icon, (self.x, self.y))
	def update(self):
		if not self.condition():
			return
		return
	def mouseInside(self, x, y):
		if boxCollision(self.x, self.y, self.x+self.w, self.y+self.h, x, y):
			return True
		return False
	def mouseDown(self, x, y):
		if not self.condition():
			return
		if self.mouseInside(x, y):
			self.active = True
	def mouseUp(self, x, y):
		if self.active:
			self.active = False
			if self.mouseInside(x, y):
				if self.action:
					if isinstance(self.action, types.LambdaType):
						self.action()
					else:
						for i in self.action:
							i()
	def sync(self):
		if not self.condition():
			return
		return


class inputTextButton():
	def __init__(self, class_, action=None, x=0, y=0, w=0, h=0, text="", dynamic=False, font_="fonts/Inconsolata.otf", fontSize=16, color=(255,255,255), activeColor=(127,127,255), maxChar=None, condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.action = action
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.text = ""
		self.func = text
		self.dynamic = dynamic
		self.font = pygame.font.Font(font_,fontSize)
		self.color = color
		self.activeColor = activeColor
		self.align = (0.5,0.5)
		self.maxChar = maxChar
		self.active = False
		self.updateText = True
		self.condition = condition
	def draw(self):
		if not self.condition():
			return
		color = self.color
		if self.active:
			color = self.activeColor
		pygame.draw.rect(self.screen, color, pygame.Rect(self.x, self.y, self.w, self.h))
		pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(self.x+1, self.y+1, self.w-2, self.h-2))
		if self.maxChar:
			text = self.font.render(self.text[0:self.maxChar], 1, color)
		else:
			text = self.font.render(self.text, 1, color)
		textSize = text.get_rect()
		self.screen.blit(text, (self.x-(textSize.width*self.align[0])+self.w/2,self.y-(textSize.height*self.align[1])+self.h/2))
	def update(self):
		if not self.condition():
			return
		if self.updateText:
			if self.dynamic:
				self.sync()
			else:
				self.text = self.func
	def mouseInside(self, x, y):
		if boxCollision(self.x, self.y, self.x+self.w, self.y+self.h, x, y):
			return True
		return False
	def mouseDown(self, x, y):
		if not self.condition():
			return
		if self.mouseInside(x, y):
			self.active = True
	def mouseUp(self, x, y):
		if self.active:
			self.active = False
			if self.mouseInside(x, y):
				if self.action:
					if isinstance(self.action, types.LambdaType):
						self.action()
					else:
						for i in self.action:
							i()
	def sync(self):
		if not self.condition():
			return
		if self.dynamic:
			vals = enumerate(self.dynamic)
			v = []
			for i in vals:
				v = v + [i[1]()]
			self.text = str(self.func.format(*v))

class inputGrid():
	def __init__(self, class_, var, action=None, v=(0,0), x=0, y=0, w=0, h=0, color=(127,127,127), cursorColor=(255,255,255), activeCursorColor=(127,127,255), image=None, circle=False, condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.var = var
		self.action = action
		self.v = v
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.color = color
		self.cursorColor = cursorColor
		self.activeCursorColor = activeCursorColor
		self.image = None
		if image:
			self.image = pygame.image.load(image).convert_alpha()
			self.image = pygame.transform.smoothscale(self.image,(self.w,self.h))
		self.circle = circle
		self.active = False
		self.condition = condition
	def commit(self):
		self.class_.inputsValue[self.var] = self.v
		if self.class_.autoCommit:
			if self.action:
				self.action()
	def sync(self):
		if not self.condition():
			return
		self.v = self.class_.inputsValue[self.var]
		self.slideTo(self.v[0], self.v[1])
	def draw(self):
		if not self.condition():
			return
		color = self.cursorColor
		if self.active:
			color = self.activeCursorColor
		if self.image:
			self.screen.blit(self.image, (self.x, self.y))
		else:
			pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x, self.y, self.w, self.h))
		#pygame.draw.rect(self.screen, color, pygame.Rect(self.x+self.v[0]-5, self.y+self.v[1]-5, 10,10))
		pygame.draw.circle(self.screen, (0,0,0), (round(self.x+self.v[0]), round(self.y+self.v[1])), 7)
		pygame.draw.circle(self.screen, color, (round(self.x+self.v[0]), round(self.y+self.v[1])), 6)
	def update(self):
		if not self.condition():
			return
		if self.active:
			x, y = pygame.mouse.get_pos()
			self.slideTo(x-self.x, y-self.y)
			self.commit()
	def slideTo(self, x, y, commit=False, act=False):
		angle = math.atan2((y-self.h/2), (x-self.w/2))
		if self.circle:
			dist = min(math.hypot(x-self.w/2, y-self.h/2), min(self.w/2, self.h/2))
		else:
			dist = math.hypot(x-self.x-self.w/2, y-self.y-self.h/2)
		nx = math.cos(angle)*dist+self.w/2
		ny = math.sin(angle)*dist+self.h/2
		self.v = (nx, ny, angle, dist)
		if commit:
			self.commit()
			if act and self.action:
				self.action()
	def mouseInside(self, x, y):
		if boxCollision(self.x-5, self.y-5, self.x+self.w+5, self.y+self.h+5, x, y):
			return True
		return False
	def mouseDown(self, x, y):
		if not self.condition():
			return
		if self.mouseInside(x, y):
			self.active = True
	def mouseUp(self, x, y):
		if self.active:
			self.active = False
			self.commit()
			if self.action:
				self.action()
			
class inputLabel():
	def __init__(self, class_, text="", dynamic=False, x=0, y=0, font_="fonts/Inconsolata.otf", fontSize=16, color=(255,255,255), activeColor=(127,127,255), align=(0,0), w=None, h=0, maxChar=None, condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.text = ""
		self.x = x
		self.y = y
		self.font = pygame.font.Font(font_,fontSize)
		self.color = color
		self.activeColor = activeColor
		self.func = text
		self.dynamic = dynamic
		self.align = align
		self.width = w
		self.height = self.font.get_linesize()+h
		self.maxChar = maxChar
		#print(self.height)
		self.active = False
		self.updateText = True
		self.condition = condition
	def update(self):
		if not self.condition():
			return
		if self.updateText:
			if self.dynamic:
				self.sync()
			else:
				self.text = self.func
	def draw(self):
		if not self.condition():
			return
		color = self.color
		if self.active:
			color = self.activeColor
		totalHeight=0
		lines = self.wrapText(self.width)
		for line in lines:
			totalHeight = totalHeight+self.height
		for i, v in enumerate(self.wrapText(self.width)):
			if self.maxChar:
				text = self.font.render(v[0:self.maxChar], 1, color)
			else:
				text = self.font.render(v, 1, color)
			textSize = text.get_rect()
			self.screen.blit(text, (self.x-(textSize.width*self.align[0]),self.y-(totalHeight*self.align[1])+(i*self.height)))
	def mouseDown(self, x, y):
		return
	def mouseUp(self, x, y):
		return
	def sync(self):
		if not self.condition():
			return
		if self.dynamic:
			vals = enumerate(self.dynamic)
			v = []
			for i in vals:
				v = v + [i[1]()]
			self.text = str(self.func.format(*v))
	def wrapText(self,width=None,wrapOnSpace=True):
		wrapedText = []
		textLine = ""
		if not width:
			width = 0
			for t in self.text.split("\n"):
				width = max(self.font.size(t)[0], width)
		for nt, t in enumerate(self.text.split("\n")):
			for i, v in enumerate(t):
				if self.font.size(textLine + v)[0] > width:
					if v == " ":
						wrapedText = wrapedText + [textLine]
						textLine = ""
					else:
						if wrapOnSpace:
							spaceSep = re.search("(.*) (.*?)$", textLine)
							if spaceSep:
								wrapedText = wrapedText + [spaceSep.group(1)]
								textLine = spaceSep.group(2) + v
							else:
								wrapedText = wrapedText + [textLine]
								textLine = v
						else:
							wrapedText = wrapedText + [textLine]
							textLine = v
				else:
					textLine = textLine + v
			wrapedText = wrapedText + [textLine]
			textLine = ""
		return wrapedText

class inputToggle():
	def __init__(self, class_, var, action, x=0, y=0, r=10, color=(127,127,127), cursorColor=(255,255,255), activeColor=(127,127,255), condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.var = var
		self.action = action
		self.x = x
		self.y = y
		self.r = r
		self.color = color
		self.cursorColor = cursorColor
		self.activeColor = activeColor
		self.active = False
		self.toggledOn = False
		self.condition = condition
	def draw(self):
		if not self.condition():
			return
		color = self.cursorColor
		if self.active:
			color = self.activeColor
		pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x-self.r, self.y-self.r, 2*self.r, 2*self.r))
		pygame.draw.circle(self.screen, self.color, (self.x-self.r, self.y), self.r)
		pygame.draw.circle(self.screen, self.color, (self.x+self.r, self.y), self.r)
		pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(self.x-self.r+1, self.y-self.r+1, 2*self.r-2, 2*self.r-2))
		pygame.draw.circle(self.screen, (0,0,0), (self.x-self.r, self.y), self.r-1)
		pygame.draw.circle(self.screen, (0,0,0), (self.x+self.r, self.y), self.r-1)
		
		if self.toggledOn:
			pygame.draw.circle(self.screen, color, (self.x+self.r, self.y), self.r-3)
		else:
			pygame.draw.circle(self.screen, color, (self.x-self.r, self.y), self.r-3)
	def update(self):
		if not self.condition():
			return
		self.toggledOn = self.var() is True
	def sync(self):
		if not self.condition():
			return
		return
	def mouseInside(self, x, y):
		if boxCollision(self.x-self.r*2, self.y-self.r, self.x+self.r*2, self.y+self.r, x, y):
			return True
		return False
	def mouseDown(self, x, y):
		if not self.condition():
			return
		if self.mouseInside(x, y):
			self.active = True
	def mouseUp(self, x, y):
		if self.active:
			self.active = False
			if self.mouseInside(x, y):
				if self.action:
					self.action()
			
class inputImage():
	def __init__(self, class_, var, x=0, y=0, w=0, h=0, align=(0,0), condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.var = var
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.align = align
		self.condition = condition
		self.image = None
	def draw(self):
		if not self.condition():
			return
		if self.image:
			width, height = self.image.get_size()
			if not self.image.get_locked():
				self.screen.blit(self.image, (self.x-(width*self.align[0]),(self.y-(height*self.align[1]))))
	def update(self):
		if not self.condition():
			return
	def sync(self):
		if not self.condition():
			return
		if self.class_.inputsValue[self.var]:
			try:
				self.image = pygame.image.load(self.class_.inputsValue[self.var]).convert_alpha()
				self.image = aspectScale(self.image, self.w,self.h)
			except Exception as e:
				print(e)
		else:
			self.image = None
	def mouseDown(self, x, y):
		return
	def mouseUp(self, x, y):
		return
		
class inputGameOfLife():
	def __init__(self, class_, x=0, y=0, r=5, color=(32,32,32), condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.game = class_.gameOfLife
		self.x = x
		self.y = y
		self.r = r
		self.color = color
		self.condition = condition
	def draw(self):
		if not self.condition():
			return
		for y, row in enumerate(self.game):
			for x, cell in enumerate(row):
				if cell:
					pygame.draw.circle(self.screen, self.color, (self.x + x*self.r*2, self.y + y*self.r*2), self.r)
	def update(self):
		if not self.condition():
			return
		self.game = self.class_.gameOfLife
	def sync(self):
		if not self.condition():
			return
	def mouseDown(self, x, y):
		return
	def mouseUp(self, x, y):
		return
		

def boxCollision(x1, y1, x2, y2, xC, yC):
	if xC >= x1 and xC <= x2 and yC >= y1 and yC <= y2:
		return True
	return False
	
def circleCollision(x, y, r, xC, yC):
	if (xC-x)^2+(yC-y)^2 <= r:
		return True
	return False
	
def roundTo(x, n=1):
	return math.floor(x/n+0.5)*n
	
def getRGBFromColorWheel(a,d,l):
	h = ((math.pi*2+a)%(math.pi*2))/(math.pi*2)
	s = d*0.02
	v = l/100*255
	return colorsys.hsv_to_rgb(h, s, v)

def getHexFromRGB(c):
	r = str(format(int(c[0]), "x"))
	g = str(format(int(c[1]), "x"))
	b = str(format(int(c[2]), "x"))
	if len(r) == 1:
		r = "0"+r
	if len(g) == 1:
		g = "0"+g
	if len(b) == 1:
		b = "0"+b
	f = "#{0}{1}{2}".format(r, g, b)
	return f
	
def aspectScale(img, w, h):
	ix,iy = img.get_size()
	sx = ix/w
	sy = iy/h
	ax = ix/iy
	ay = iy/ix
	if sx >= sy:
		nx = w
		ny = ay*w
	else:
		nx = ax*h
		ny = h
	#print(nx, ny)
	return pygame.transform.smoothscale(img, (int(nx),int(ny)))
	

if __name__ == "__main__":
	sarah = SARaH()
	#print(getHexFromRGB(getRGBFromColorWheel(0,50,100)))
	#print(aspectScale(pygame.image.load("images/Backgrounds/1x1.png").convert_alpha(), 160, 240))
	#sarah.generateGameOfLife("Hello world")
	while sarah.keepRunning:
		sarah.run()
		
