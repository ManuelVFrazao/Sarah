import socket
import math
import colorsys
import types
import datetime
import threading
import calendar
import math
import re

import pygame

import sarahAI
import sarahMQTT

class SARaH:
	def __init__(self):
		pygame.init()
		#self.screen = pygame.display.set_mode((320, 240),(pygame.FULLSCREEN))
		self.screen = pygame.display.set_mode((320, 240))
		self.keepRunning = True
		#pygame.mouse.set_visible(False)
		self.mousePressed = False
		self.mousePressPos = (0,0)
		self.mouseReleasedPos = (0,0)
		self.mouseDrag = (0,0)
		self.clock = pygame.time.Clock()
		self.autoCommit = False
		
		self.AI = sarahAI.SarahAI()
		self.AIThread = sarahAI.aiThread(self.AI)
		self.AIThread.daemon = True
		self.AIThread.start()
		
		self.MQTT = sarahMQTT.SarahMQTT()
		self.MQTT.client.on_message = self.MQTTReceive
		
		self.AI.mqtt = sarahAI.aiMqtt(self.MQTT.client, "sarah/house")
		
		self.passCode = {
			"code":"",
			"unlockCode":"1234",
			"state":"armed",
			"attempts":0,
		}
		
		self.rooms = [
			{"name":"Kitchen","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":0,"numOutlets":8},
			{"name":"Living Room","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":0,"numOutlets":2},
		]
		
		self.currentRoom = 0
		self.inputsValue = {
			"lightSlider":100,
			"temperatureSlider":20.0,
			"RGBWheel":(0,0, 0,0),
		}
		self.inputs = []
		
		self.CurrentPage = 0
		self.pages = [
			{
				"name":"Home",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage(1), 10,50, 74,74, icon="images/house139.png"),
					inputButton(self, lambda:self.changePage(5), 10,134, 74,74, icon="images/microphone83.png"),
					
					inputButton(self, lambda:self.changePage(10), 123,50, 74,74, icon="images/key170.png"),
					inputButton(self, lambda:self.changePage(5), 123,134, 74,74, icon="images/circular264.png"),
					
					inputButton(self, lambda:self.changePage(10), 236,50, 74,74, icon="images/musical115.png"),
					inputButton(self, lambda:self.changePage(5), 236,134, 74,74, icon="images/code42.png"),
					
					inputLabel(self, "{0}\n{1}", [lambda:self.getTime(),lambda:self.getDate()], 40,4),
					
					inputButton(self, lambda:self.changePage(8), 4,4, 32,32, icon="images/monthly5.png"),
					inputButton(self, lambda:self.changePage(7), 284,4, 32,32, icon="images/configuration20.png"),
				]
			},
			{
				"name":"Rooms",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					
					inputButton(self, lambda:self.changePage(2, 0), 10,50, 128,32),
					inputLabel(self, "{0}", [lambda:self.rooms[0]["name"]], 74,66, color=(0,0,0), align=(0.5,0.5)),
					
					inputButton(self, lambda:self.changePage(2, 1), 182,50, 128,32),
					inputLabel(self, "{0}", [lambda:self.rooms[1]["name"]], 246,66, color=(0,0,0), align=(0.5,0.5)),
				]
			},
			{
				"name":"Light",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputSlider(self, "lightSlider", lambda:self.commitValues(), 100, 0, 100, 1, 248,50, 20,100, vertical=True, reversed_=True),
					inputGrid(self, "RGBWheel", lambda:self.commitValues(), (50,50), 10,92, 100,100, image="images/HSV.png", circle=True),
					
					#inputLabel(self, "{0}", [lambda:getHexFromRGB(getRGBFromColorWheel( \
					#	self.inputsValue["RGBWheel"][2], \
					#	self.inputsValue["RGBWheel"][3], \
					#	self.inputsValue["lightSlider"] \
					#	))], 52, 58, align=(0,0.5)),
					#inputLabel(self, "{0}%", [lambda:roundTo(self.inputsValue["lightSlider"])], 52, 74, align=(0,0.5)),
					inputLabel(self, "{0}\n{1}%", [lambda:getHexFromRGB(getRGBFromColorWheel( \
						self.inputsValue["RGBWheel"][2], \
						self.inputsValue["RGBWheel"][3], \
						self.inputsValue["lightSlider"] \
						)),lambda:roundTo(self.inputsValue["lightSlider"])], 52, 50, align=(0,0)),
						
					inputButton(self, lambda:self.inputs[1].slideTo(50,50,True,True), 10,50, 32,32, color=(255,255,255)),
					inputButton(self, lambda:self.inputs[0].slide(-10,True,True), 278,50, 32,32, color=(255,255,255), icon="images/up154.png"),
					inputButton(self, lambda:self.inputs[0].slide(10,True,True), 278,118, 32,32, color=(255,255,255), icon="images/down102.png"),
					
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputButton(self.screen, None, 44,4, 32,32),
					inputButton(self, lambda:self.changePage(2), 84,4, 32,32, icon="images/lightbulb52.png"),
					inputButton(self, lambda:self.changePage(3), 124,4, 32,32, icon="images/thermometer53.png"),
					inputButton(self, lambda:self.changePage(4), 164,4, 32,32, icon="images/electrical28.png"),
					
					#inputLabel(self, "{0}", [lambda:self.rooms[self.currentRoom]["name"]], 316, 4, align=(1,0)),
					#inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["name"],lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
			{
				"name":"Temperature",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputSlider(self, "temperatureSlider", lambda:self.commitValues(), 20, 17, 23, 0.5, 248,50, 20,100, vertical=True, reversed_=True),
					
					inputLabel(self, "Current: {0}", [lambda:float(self.rooms[self.currentRoom]["currentTemperature"])], 238, 75, fontSize=32, align=(1,0.5)),
					inputLabel(self, "Set: {0}", [lambda:float(self.inputsValue["temperatureSlider"])], 238, 125, fontSize=32, align=(1,0.5)),
					
					inputButton(self, lambda:self.inputs[0].slide(-0.5,True,True), 278,50, 32,32, color=(255,255,255), icon="images/up154.png"),
					inputButton(self, lambda:self.inputs[0].slide(0.5,True,True), 278,118, 32,32, color=(255,255,255), icon="images/down102.png"),
				
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputButton(self.screen, None, 44,4, 32,32),
					inputButton(self, lambda:self.changePage(2), 84,4, 32,32, icon="images/lightbulb52.png"),
					inputButton(self, lambda:self.changePage(3), 124,4, 32,32, icon="images/thermometer53.png"),
					inputButton(self, lambda:self.changePage(4), 164,4, 32,32, icon="images/electrical28.png"),
					
					#inputLabel(self, "{0}", [lambda:self.rooms[self.currentRoom]["name"]], 316, 4, align=(1,0)),
					#inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["name"],lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
			{
				"name":"Outlets",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,0), 10,50, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=1),
					inputLabel(self, "1a\n{0}", [lambda:self.getOutletText(self.currentRoom,0)], 26,66, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=1),
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,1), 10,92, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=2),
					inputLabel(self, "1b\n{0}", [lambda:self.getOutletText(self.currentRoom,1)], 26,108, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=2),
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,2), 10,134, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=3),
					inputLabel(self, "2a\n{0}", [lambda:self.getOutletText(self.currentRoom,2)], 26,150, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=3),
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,3), 10,176, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=4),
					inputLabel(self, "2b\n{0}", [lambda:self.getOutletText(self.currentRoom,3)], 26,192, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=4),
					
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,4), 52,50, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=5),
					inputLabel(self, "3a\n{0}", [lambda:self.getOutletText(self.currentRoom,4)], 68,66, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=5),
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,5), 52,92, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=6),
					inputLabel(self, "3b\n{0}", [lambda:self.getOutletText(self.currentRoom,5)], 68,108, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=6),
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,6), 52,134, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=7),
					inputLabel(self, "4a\n{0}", [lambda:self.getOutletText(self.currentRoom,6)], 68,150, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=7),
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom,7), 52,176, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=8),
					inputLabel(self, "4b\n{0}", [lambda:self.getOutletText(self.currentRoom,7)], 68,192, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=8),
					
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputButton(self.screen, None, 44,4, 32,32),
					inputButton(self, lambda:self.changePage(2), 84,4, 32,32, icon="images/lightbulb52.png"),
					inputButton(self, lambda:self.changePage(3), 124,4, 32,32, icon="images/thermometer53.png"),
					inputButton(self, lambda:self.changePage(4), 164,4, 32,32, icon="images/electrical28.png"),
					
					#inputLabel(self, "{0}", [lambda:self.rooms[self.currentRoom]["name"]], 316, 4, align=(1,0)),
					#inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["name"],lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
			{
				"name":"Sarah",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
				
				
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					inputButton(self, lambda:self.AIListen(), 84,4, 32,32, icon="images/microphone83.png"),
					inputButton(self, lambda:self.changePage(6), 124,4, 32,32, icon="images/two374.png"),
					
					inputLabel(self, "{0}", [lambda:"Status: {0}".format(str(self.AI.out)) if str(self.AI.out) else ""], 10, 50, align=(0,0)),
					inputLabel(self, "{0}", [lambda:"You said: {0}".format(str(self.AI.recognizedText)) if str(self.AI.recognizedText) else ""], 10, 82, align=(0,0), w=300),
					
					
					#inputLabel(self, "SARaH", False, 316, 4, align=(1,0)),
					#inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					inputLabel(self, "SARaH\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
			{
				"name":"SarahOptions",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
				
				
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					inputButton(self, lambda:self.changePage(5), 84,4, 32,32, icon="images/microphone83.png"),
					
					inputButton(self, lambda:self.AIKeepListening(), 10,50, 32,32, icon="images/right204.png"),
					inputButton(self, lambda:self.AIKeepTriggered(), 10,92, 32,32, icon="images/right204.png"),
					inputButton(self, lambda:self.AIIsTriggered(), 10,134, 32,32, icon="images/right204.png"),
					
					inputLabel(self, "Autolisten:\n{0}", [lambda:str(self.AIThread.keepListening)], 52, 50, align=(0,0)),
					inputLabel(self, "Autotrigger:\n{0}", [lambda:str(self.AI.keepListening)], 52, 92, align=(0,0)),
					inputLabel(self, "Triggered:\n{0}", [lambda:str(self.AI.isTriggered)], 52, 134, align=(0,0)),
					
					#inputLabel(self, "SARaH", False, 316, 4, align=(1,0)),
					#inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					inputLabel(self, "SARaH\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
			{
				"name":"Config",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
				
				
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					
					
					inputLabel(self, "Options\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
			{
				"name":"Calendar",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
				
					inputLabel(self, "{0}", [lambda:self.getTime()], 160, 50, fontSize=72, align=(0.5,0)),
					inputLabel(self, "{0}", [lambda:self.getDate()], 160, 130, fontSize=38, align=(0.5,0)),
					inputLabel(self, "{0}", [lambda:self.getFullDate()], 160, 165, fontSize=18, align=(0.5,0)),
				
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					
					
					inputButton(self, lambda:self.changePage(9), 284,4, 32,32, icon="images/configuration20.png"),
				]
			},
			{
				"name":"CalendarOptions",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					inputButton(self, lambda:self.changePage(8), 284,4, 32,32, icon="images/monthly5.png"),
				]
			},
			{
				"name":"Security",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					inputLabel(self, "Security\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
					
					inputButton(self, lambda:self.changePage(11), 10,50, 32,32, icon="images/nine19.png"),
				]
			},
			{
				"name":"Keypad",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputLabel(self, "{0}\n{1}", [lambda:self.getTime(),lambda:self.codeDigits()], 160, 4, align=(0.5,0)),
					
					inputButton(self, lambda:self.codeDigit(1), 10,50, 67,53),
					inputButton(self, lambda:self.codeDigit(2), 88,50, 67,53),
					inputButton(self, lambda:self.codeDigit(3), 165,50, 67,53),
					
					inputButton(self, lambda:self.codeDigit(4), 10,113, 67,53),
					inputButton(self, lambda:self.codeDigit(5), 88,113, 67,53),
					inputButton(self, lambda:self.codeDigit(6), 165,113, 67,53),
					
					inputButton(self, lambda:self.codeDigit(7), 10,176, 67,53),
					inputButton(self, lambda:self.codeDigit(8), 88,176, 67,53),
					inputButton(self, lambda:self.codeDigit(9), 165,176, 67,53),
					
					inputButton(self, lambda:self.codeCancel(), 243,50, 67,53, color=(255,0,0)),
					inputButton(self, lambda:self.codeDigit(0), 243,113, 67,53),
					inputButton(self, lambda:self.codeConfirm(), 243,176, 67,53, color=(0,255,0)),
				]
			},
			{
				"name":"Music",
				"background":pygame.image.load("images/background.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					inputLabel(self, "Music\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				]
			},
		]
		self.changePage(0)
	
	def changePage(self, page=0, room=None):
		self.inputs = self.pages[page]["inputs"]
		self.CurrentPage = page
		if room != None:
			self.changeRoom(room)
		self.sync(syncAllInputs=True)
			
	def changeRoom(self, room):
		self.currentRoom = room
		self.sync(syncAllInputs=True)
	
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
		if self.passCode["state"] == "armed":
			return "*" * len(self.passCode["code"])
		else:
			return self.passCode["code"]
		
	def codeDigit(self, digit):
		self.passCode["code"] = self.passCode["code"] + str(digit)
		
	def codeCancel(self):
		if self.passCode["state"] == "armed":
			self.passCode["code"] = ""
			
	def codeConfirm(self):
		if self.passCode["state"] == "armed":
			if self.passCode["code"] == self.passCode["unlockCode"]:
				self.passCode["code"] = ""
				self.passCode["state"] = "normal"
				
				#disarm the system
				#self.MQTTSend("sarah/house", "room=-1,disarm=1")
				
				#Bad idea to send a disarm signal over the network, The
				#security system control panel will be connected through
				#serial
				
				self.changePage(0)
			else:
				self.passCode["code"] = ""
				self.passCode["attempts"] = self.passCode["attempts"] + 1
		
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
		
	def draw(self):
		#print("draw")
		#pygame.draw.rect(self.screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))
		if "background" in self.pages[self.CurrentPage]:
			self.screen.blit(self.pages[self.CurrentPage]["background"], (0,0))
		else:
			self.screen.fill((0,0,0))
		for inp in self.inputs:
			inp.draw()
			
	def commitValues(self):
		room = self.rooms[self.currentRoom]
		room["temperature"] = self.inputsValue["temperatureSlider"]
		colorWheel = self.inputsValue["RGBWheel"]
		
		roomColor = getRGBFromColorWheel(colorWheel[2],colorWheel[3],self.inputsValue["lightSlider"])
		#print(roomColor)
		room["lightR"] = roomColor[0]
		room["lightG"] = roomColor[1]
		room["lightB"] = roomColor[2]
		print(roomColor, colorWheel)
		
		mqttMsg = "{0},temperature,{1};{0},lightR,{2};{0},{0},lightG,{3};{0},lightB,{4}".format(
			self.currentRoom, str(room["temperature"]), str(room["lightR"]), str(room["lightG"]), str(room["lightB"]))
		
		print(mqttMsg)
		self.MQTTSend("sarah/house", mqttMsg)
		
	def sync(self, syncAllInputs=False):
		room = self.rooms[self.currentRoom]
		self.inputsValue["temperatureSlider"] = room["temperature"]
		colorWheel = self.inputsValue["RGBWheel"]
		roomColor = colorsys.rgb_to_hsv(float(room["lightR"]), float(room["lightG"]), float(room["lightB"]))
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

	def toggle(self, var, x, y, default=None, sync=None, commit=False):
		if self.inputsValue[var] == x:
			self.inputsValue[var] = y
		elif self.inputsValue[var] == y:
			self.inputsValue[var] = x
		else:
			if default is not None:
				self.inputsValue[var] = default
		if commit:
			self.commitValues()
		if sync:
			self.sync(True)
			
	def AIKeepListening(self):
		self.AIThread.keepListening = not self.AIThread.keepListening
		
	def AIKeepTriggered(self):
		self.AI.keepListening = not self.AI.keepListening
		
	def AIIsTriggered(self):
		self.AI.isTriggered = not self.AI.isTriggered
		
	def AIListen(self):
		if not self.AIThread.listen:
			if self.AI.keepListening:
				self.AI.isTriggered = True
			self.AIThread.listen = True
		else:
			self.AI.stopTalking()
			
	def MQTTReceive(self, client, userdata, msg):
		print(msg.topic+" "+str(msg.payload))
		for i in msg.payload.decode("utf-8").split(";"):
			print(i)
			command = i.split(",")
			if int(command[0]) >= 0:
				if command[1] == "temperature":
					self.rooms[int(command[0])]["temperature"] = min(max(float(command[2]), 17), 23)
				if command[1] == "lightR":
					self.rooms[int(command[0])]["lightR"] = min(max(float(command[2]), 0), 255)
				if command[1] == "lightG":
					self.rooms[int(command[0])]["lightG"] = min(max(float(command[2]), 0), 255)
				if command[1] == "lightB":
					self.rooms[int(command[0])]["lightB"] = min(max(float(command[2]), 0), 255)
				if command[1] == "outletOn":
					self.turnOutletOn(int(command[0]), int(command[2]), commit=False)
				if command[1] == "outletOff":
					self.turnOutletOff(int(command[0]), int(command[2]), commit=False)
				if command[1] == "outletToggle":
					self.toggleOutlet(int(command[0]), int(command[2]), commit=False)
		self.sync(syncAllInputs=True)
		
		
	def MQTTSend(self, topic, msg):
		self.MQTT.client.publish(topic, msg)
		
	def isOutletOn(self, room, outlet):
		return (self.rooms[room]["outlets"]%(2**(outlet+1)))/(2**outlet) >= 1
	
	def turnOutletOn(self, room, outlet, commit=True):
		if not self.isOutletOn(room, outlet):
			self.rooms[room]["outlets"] = self.rooms[room]["outlets"]+(2**outlet)
			if commit:
				self.MQTTSend("sarah/house", "{0},outletOn,{1}".format(room,outlet))
				
	def turnOutletOff(self, room, outlet, commit=True):
		if self.isOutletOn(room, outlet):
			self.rooms[room]["outlets"] = self.rooms[room]["outlets"]-(2**outlet)
			if commit:
				self.MQTTSend("sarah/house", "{0},outletOff,{1}".format(room,outlet))
	
	def toggleOutlet(self, room, outlet, commit=True):
		if self.isOutletOn(room, outlet):
			self.turnOutletOff(room, outlet)
			if commit:
				self.MQTTSend("sarah/house", "{0},outletOff,{1}".format(room,outlet))
		else:
			self.turnOutletOn(room, outlet)
			if commit:
				self.MQTTSend("sarah/house", "{0},outletOn,{1}".format(room,outlet))
	
	def getOutletText(self, room, outlet):
		if self.isOutletOn(room, outlet):
			return "On"
		else:
			return "Off"
	
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
	def __init__(self, class_, action=None, x=0, y=0, w=0, h=0, color=(255,255,255), activeColor=(127,127,255), textColor=(0,0,0), icon=None, condition=lambda:True):
		self.class_ = class_
		self.screen = class_.screen
		self.action = action
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.color = color
		self.activeColor = activeColor
		self.icon = None
		if icon:
			self.icon = pygame.image.load(icon).convert_alpha()
			self.icon = pygame.transform.smoothscale(self.icon,(self.w,self.h))
		self.active = False
		self.condition = condition
	def draw(self):
		if not self.condition():
			return
		color = self.color
		if self.active:
			color = self.activeColor
		pygame.draw.rect(self.screen, color, pygame.Rect(self.x, self.y, self.w, self.h))
		if self.icon:
			self.screen.blit(self.icon, (self.x, self.y))
	def update(self):
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
		return

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
		self.v = self.class_.inputsValue[self.var]
		self.slideTo(self.v[0], self.v[1])
	def draw(self):
		if not self.condition():
			return
		color = self.cursorColor
		if self.active:
			color = self.activeCursorColor
		pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x, self.y, self.w, self.h))
		if self.image:
			self.screen.blit(self.image, (self.x, self.y))
		#pygame.draw.rect(self.screen, color, pygame.Rect(self.x+self.v[0]-5, self.y+self.v[1]-5, 10,10))
		pygame.draw.circle(self.screen, (0,0,0), (round(self.x+self.v[0]), round(self.y+self.v[1])), 7)
		pygame.draw.circle(self.screen, color, (round(self.x+self.v[0]), round(self.y+self.v[1])), 6)
	def update(self):
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
	def __init__(self, class_, text="", dynamic=False, x=0, y=0, font_="fonts/Inconsolata.otf", fontSize=16, color=(255,255,255), activeColor=(127,127,255), align=(0,0), w=None, h=0, condition=lambda:True):
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
		#print(self.height)
		self.active = False
		self.updateText = True
		self.condition = condition
	def update(self):
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
			text = self.font.render(v, 1, self.color)
			textSize = text.get_rect()
			self.screen.blit(text, (self.x-(textSize.width*self.align[0]),self.y-(totalHeight*self.align[1])+(i*self.height)))
	def mouseDown(self, x, y):
		return
	def mouseUp(self, x, y):
		return
	def sync(self):
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
							wrapedText = wrapedText + [spaceSep.group(1)]
							textLine = spaceSep.group(2) + v
						else:
							wrapedText = wrapedText + [textLine]
							textLine = v
				else:
					textLine = textLine + v
			wrapedText = wrapedText + [textLine]
			textLine = ""
		return wrapedText
			

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

if __name__ == "__main__":
	sarah = SARaH()
	#print(getHexFromRGB(getRGBFromColorWheel(0,50,100)))
	while sarah.keepRunning:
		sarah.run()
		
