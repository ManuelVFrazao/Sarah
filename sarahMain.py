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
#import numpy as N
#import pygame.surfarray as surfarray

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
			{"name":"Kitchen","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"Blender","on":True,"consumption":0},{"name":"TV","on":False,"consumption":0}]},
			{"name":"Living Room","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Master bedroom","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Kid bedroom","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Guest room","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Basement","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Garage","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Attic","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
			{"name":"Backyard","lightR":127,"lightG":127,"lightB":127,"temperature":20.0,"currentTemperature":19.5,"outlets":[{"name":"TV","on":True,"consumption":0}]},
		]
		
		self.currentRoom = 0
		self.inputsValue = {
			"lightSlider":100,
			"temperatureSlider":20.0,
			"RGBWheel":(0,0, 0,0),
			"musicVolumeSlider":50
		}
		self.inputs = []
		
		self.presets = [
			
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
		
		self.music = {
			"status":"Stopped",
			"playing":False,
			"title":"The quick brown fox jumps over the lazy dog",
			"artist":"The quick brown fox jumps over the lazy dog",
			"album":"The quick brown fox jumps over the lazy dog",
			"shuffle":False,
			"loop":False,
		}
		
		self.CurrentPage = "home"
		self.pages = {
			#{
				#"name":"Home",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputButton(self, lambda:self.changePage(1), 10,50, 74,74, icon="images/house139.png"),
					#inputButton(self, lambda:self.changePage(5), 10,134, 74,74, icon="images/microphone83.png"),
					
					#inputButton(self, lambda:self.changePage(10), 123,50, 74,74, icon="images/key170.png"),
					#inputButton(self, lambda:self.changePage(5), 123,134, 74,74, icon="images/circular264.png"),
					
					#inputButton(self, lambda:self.changePage(10), 236,50, 74,74, icon="images/musical115.png"),
					#inputButton(self, lambda:self.changePage(5), 236,134, 74,74, icon="images/code42.png"),
					
					#inputLabel(self, "{0}\n{1}", [lambda:self.getTime(),lambda:self.getDate()], 40,4),
					
					#inputButton(self, lambda:self.changePage(8), 4,4, 32,32, icon="images/monthly5.png"),
					#inputButton(self, lambda:self.changePage(7), 284,4, 32,32, icon="images/configuration20.png"),
				#]
			#},
			#{
				#"name":"Rooms",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					
					#inputButton(self, lambda:self.changePage(2, 0), 10,50, 128,32),
					#inputLabel(self, "{0}", [lambda:self.rooms[0]["name"]], 74,66, color=(0,0,0), align=(0.5,0.5)),
					
					#inputButton(self, lambda:self.changePage(2, 1), 182,50, 128,32),
					#inputLabel(self, "{0}", [lambda:self.rooms[1]["name"]], 246,66, color=(0,0,0), align=(0.5,0.5)),
				#]
			#},
			#{
				#"name":"Light",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputSlider(self, "lightSlider", lambda:self.commitValues(), 100, 0, 100, 1, 248,50, 20,100, vertical=True, reversed_=True),
					#inputGrid(self, "RGBWheel", lambda:self.commitValues(), (50,50), 10,92, 100,100, image="images/HSV.png", circle=True),
					
					##inputLabel(self, "{0}", [lambda:getHexFromRGB(getRGBFromColorWheel( \
					##	self.inputsValue["RGBWheel"][2], \
					##	self.inputsValue["RGBWheel"][3], \
					##	self.inputsValue["lightSlider"] \
					##	))], 52, 58, align=(0,0.5)),
					##inputLabel(self, "{0}%", [lambda:roundTo(self.inputsValue["lightSlider"])], 52, 74, align=(0,0.5)),
					#inputLabel(self, "{0}\n{1}%", [lambda:getHexFromRGB(getRGBFromColorWheel( \
						#self.inputsValue["RGBWheel"][2], \
						#self.inputsValue["RGBWheel"][3], \
						#self.inputsValue["lightSlider"] \
						#)),lambda:roundTo(self.inputsValue["lightSlider"])], 52, 50, align=(0,0)),
						
					#inputButton(self, lambda:self.inputs[1].slideTo(50,50,True,True), 10,50, 32,32, color=(255,255,255)),
					#inputButton(self, lambda:self.inputs[0].slide(-10,True,True), 278,50, 32,32, color=(255,255,255), icon="images/up154.png"),
					#inputButton(self, lambda:self.inputs[0].slide(10,True,True), 278,118, 32,32, color=(255,255,255), icon="images/down102.png"),
					
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					##inputButton(self.screen, None, 44,4, 32,32),
					#inputButton(self, lambda:self.changePage(2), 84,4, 32,32, icon="images/lightbulb52.png"),
					#inputButton(self, lambda:self.changePage(3), 124,4, 32,32, icon="images/thermometer53.png"),
					#inputButton(self, lambda:self.changePage(4), 164,4, 32,32, icon="images/electrical28.png"),
					
					##inputLabel(self, "{0}", [lambda:self.rooms[self.currentRoom]["name"]], 316, 4, align=(1,0)),
					##inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					#inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["name"],lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			#{
				#"name":"Temperature",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputSlider(self, "temperatureSlider", lambda:self.commitValues(), 20, 17, 23, 0.5, 248,50, 20,100, vertical=True, reversed_=True),
					
					#inputLabel(self, "Current: {0}", [lambda:float(self.rooms[self.currentRoom]["currentTemperature"])], 238, 75, fontSize=32, align=(1,0.5)),
					#inputLabel(self, "Set: {0}", [lambda:float(self.inputsValue["temperatureSlider"])], 238, 125, fontSize=32, align=(1,0.5)),
					
					#inputButton(self, lambda:self.inputs[0].slide(-0.5,True,True), 278,50, 32,32, color=(255,255,255), icon="images/up154.png"),
					#inputButton(self, lambda:self.inputs[0].slide(0.5,True,True), 278,118, 32,32, color=(255,255,255), icon="images/down102.png"),
				
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					##inputButton(self.screen, None, 44,4, 32,32),
					#inputButton(self, lambda:self.changePage(2), 84,4, 32,32, icon="images/lightbulb52.png"),
					#inputButton(self, lambda:self.changePage(3), 124,4, 32,32, icon="images/thermometer53.png"),
					#inputButton(self, lambda:self.changePage(4), 164,4, 32,32, icon="images/electrical28.png"),
					
					##inputLabel(self, "{0}", [lambda:self.rooms[self.currentRoom]["name"]], 316, 4, align=(1,0)),
					##inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					#inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["name"],lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			#{
				#"name":"Outlets",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,0), 10,50, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=1),
					#inputLabel(self, "1a\n{0}", [lambda:self.getOutletText(self.currentRoom,0)], 26,66, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=1),
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,1), 10,92, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=2),
					#inputLabel(self, "1b\n{0}", [lambda:self.getOutletText(self.currentRoom,1)], 26,108, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=2),
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,2), 10,134, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=3),
					#inputLabel(self, "2a\n{0}", [lambda:self.getOutletText(self.currentRoom,2)], 26,150, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=3),
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,3), 10,176, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=4),
					#inputLabel(self, "2b\n{0}", [lambda:self.getOutletText(self.currentRoom,3)], 26,192, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=4),
					
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,4), 52,50, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=5),
					#inputLabel(self, "3a\n{0}", [lambda:self.getOutletText(self.currentRoom,4)], 68,66, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=5),
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,5), 52,92, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=6),
					#inputLabel(self, "3b\n{0}", [lambda:self.getOutletText(self.currentRoom,5)], 68,108, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=6),
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,6), 52,134, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=7),
					#inputLabel(self, "4a\n{0}", [lambda:self.getOutletText(self.currentRoom,6)], 68,150, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=7),
					#inputButton(self, lambda:self.toggleOutlet(self.currentRoom,7), 52,176, 32,32, condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=8),
					#inputLabel(self, "4b\n{0}", [lambda:self.getOutletText(self.currentRoom,7)], 68,192, align=(0.5,0.5), color=(0,0,0), condition=lambda:self.rooms[self.currentRoom]["numOutlets"]>=8),
					
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					##inputButton(self.screen, None, 44,4, 32,32),
					#inputButton(self, lambda:self.changePage(2), 84,4, 32,32, icon="images/lightbulb52.png"),
					#inputButton(self, lambda:self.changePage(3), 124,4, 32,32, icon="images/thermometer53.png"),
					#inputButton(self, lambda:self.changePage(4), 164,4, 32,32, icon="images/electrical28.png"),
					
					##inputLabel(self, "{0}", [lambda:self.rooms[self.currentRoom]["name"]], 316, 4, align=(1,0)),
					##inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					#inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["name"],lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			#{
				#"name":"Sarah",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
				
				
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputButton(self, lambda:self.AIListen(), 84,4, 32,32, icon="images/microphone83.png"),
					#inputButton(self, lambda:self.changePage(6), 124,4, 32,32, icon="images/two374.png"),
					
					#inputLabel(self, "{0}", [lambda:"Status: {0}".format(str(self.AI.out)) if str(self.AI.out) else ""], 10, 50, align=(0,0)),
					#inputLabel(self, "{0}", [lambda:"You said: {0}".format(str(self.AI.recognizedText)) if str(self.AI.recognizedText) else ""], 10, 82, align=(0,0), w=300),
					
					
					##inputLabel(self, "SARaH", False, 316, 4, align=(1,0)),
					##inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					#inputLabel(self, "SARaH\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			#{
				#"name":"SarahOptions",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
				
				
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputButton(self, lambda:self.changePage(5), 84,4, 32,32, icon="images/microphone83.png"),
					
					#inputButton(self, lambda:self.AIKeepListening(), 10,50, 32,32, icon="images/right204.png"),
					#inputButton(self, lambda:self.AIKeepTriggered(), 10,92, 32,32, icon="images/right204.png"),
					#inputButton(self, lambda:self.AIIsTriggered(), 10,134, 32,32, icon="images/right204.png"),
					
					#inputLabel(self, "Autolisten:\n{0}", [lambda:str(self.AIThread.keepListening)], 52, 50, align=(0,0)),
					#inputLabel(self, "Autotrigger:\n{0}", [lambda:str(self.AI.keepListening)], 52, 92, align=(0,0)),
					#inputLabel(self, "Triggered:\n{0}", [lambda:str(self.AI.isTriggered)], 52, 134, align=(0,0)),
					
					##inputLabel(self, "SARaH", False, 316, 4, align=(1,0)),
					##inputLabel(self, "{0}", [lambda:self.getTime()], 316, 24, align=(1,0)),
					#inputLabel(self, "SARaH\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			#{
				#"name":"Config",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
				
				
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					
					
					#inputLabel(self, "Options\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			#{
				#"name":"Calendar",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
				
					#inputLabel(self, "{0}", [lambda:self.getTime()], 160, 50, fontSize=72, align=(0.5,0)),
					#inputLabel(self, "{0}", [lambda:self.getDate()], 160, 130, fontSize=38, align=(0.5,0)),
					#inputLabel(self, "{0}", [lambda:self.getFullDate()], 160, 165, fontSize=18, align=(0.5,0)),
				
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					
					
					#inputButton(self, lambda:self.changePage(9), 284,4, 32,32, icon="images/configuration20.png"),
				#]
			#},
			#{
				#"name":"CalendarOptions",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputButton(self, lambda:self.changePage(8), 284,4, 32,32, icon="images/monthly5.png"),
				#]
			#},
			#{
				#"name":"Security",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputLabel(self, "Security\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
					
					#inputButton(self, lambda:self.changePage(11), 10,50, 32,32, icon="images/nine19.png"),
				#]
			#},
			#{
				#"name":"Keypad",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputLabel(self, "{0}\n{1}", [lambda:self.getTime(),lambda:self.codeDigits()], 160, 4, align=(0.5,0)),
					
					#inputButton(self, lambda:self.codeDigit(1), 10,50, 67,53),
					#inputButton(self, lambda:self.codeDigit(2), 88,50, 67,53),
					#inputButton(self, lambda:self.codeDigit(3), 165,50, 67,53),
					
					#inputButton(self, lambda:self.codeDigit(4), 10,113, 67,53),
					#inputButton(self, lambda:self.codeDigit(5), 88,113, 67,53),
					#inputButton(self, lambda:self.codeDigit(6), 165,113, 67,53),
					
					#inputButton(self, lambda:self.codeDigit(7), 10,176, 67,53),
					#inputButton(self, lambda:self.codeDigit(8), 88,176, 67,53),
					#inputButton(self, lambda:self.codeDigit(9), 165,176, 67,53),
					
					#inputButton(self, lambda:self.codeCancel(), 243,50, 67,53, color=(255,0,0)),
					#inputButton(self, lambda:self.codeDigit(0), 243,113, 67,53),
					#inputButton(self, lambda:self.codeConfirm(), 243,176, 67,53, color=(0,255,0)),
				#]
			#},
			#{
				#"name":"Music",
				#"background":pygame.image.load("images/background.png").convert_alpha(),
				#"inputs":[
					#inputButton(self, lambda:self.changePage(0), 4,4, 32,32, icon="images/house139.png"),
					#inputLabel(self, "Music\n{0}", [lambda:self.getTime()], 316, 4, align=(1,0)),
				#]
			#},
			"home":{
				"name":"Home",
				"background":pygame.image.load("images/Backgrounds/3x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("house"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.changePage("sarah"), 68,10, 48,48, icon="images/Icons/microphone83.png"),
					inputButton(self, lambda:self.changePage("home"), 126,10, 48,48, icon="images/Icons/key170.png"),
					inputButton(self, lambda:self.changePage("home"), 262,10, 48,48, icon="images/Icons/configuration20.png"),
					
					inputLabel(self, "{0}", [lambda:self.getTime()], 160, 70, fontSize=72, align=(0.5,0)),
					inputLabel(self, "{0}", [lambda:self.getDate()], 160, 150, fontSize=38, align=(0.5,0)),
					inputLabel(self, "{0}", [lambda:self.getFullDate()], 160, 185, fontSize=18, align=(0.5,0)),
					
				]
			},
			"house":{
				"name":"House",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, [lambda:self.changePage("customActions"),lambda:self.scrollButtons(0, 3, absolute=True)], 146,10, 48,48, icon="images/Icons/code42.png"),
					inputButton(self, lambda:self.changePage("multimedia"), 204,10, 48,48, icon="images/Icons/musical115.png"),
					inputButton(self, [lambda:self.changePage("rooms"),lambda:self.scrollButtons(0, 6, absolute=True)], 262,10, 48,48, icon="images/Icons/button10.png"),
					
					inputTextButton(self, lambda:self.changePage("house"), 20,80, 200,48, "Hello world")
				]
			},
			"rooms":{
				"name":"Rooms",
				"background":pygame.image.load("images/Backgrounds/1x2.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("house"), 10,10, 48,48, icon="images/Icons/house139.png"),
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
					inputButton(self, lambda:self.changePage("lights"), 146,10, 48,48, icon="images/Icons/lightbulb52.png"),
					inputButton(self, lambda:self.changePage("temperature"), 204,10, 48,48, icon="images/Icons/thermometer53.png"),
					inputButton(self, lambda:self.changePage("outlets"), 262,10, 48,48, icon="images/Icons/electrical28.png"),
				
					inputSlider(self, "lightSlider", lambda:self.commitValues(), 100, 0, 100, 1, 222,80, 20,100, vertical=True, reversed_=True),
					
					inputGrid(self, "RGBWheel", lambda:self.commitValues(), (50,50), 20,80, 100,100, image="images/HSV.png", circle=True),
					
					inputLabel(self, "{0}\n{1}%", [lambda:getHexFromRGB(getRGBFromColorWheel( \
						self.inputsValue["RGBWheel"][2], \
						self.inputsValue["RGBWheel"][3], \
						self.inputsValue["lightSlider"] \
						)),lambda:roundTo(self.inputsValue["lightSlider"])], 202, 80, fontSize=20, align=(1,0)),
					
					inputButton(self, lambda:self.inputs[4].slide(-10,True,True), 252,80, 48,48, icon="images/Icons/up154.png"),
					inputButton(self, lambda:self.inputs[4].slide(10,True,True), 252,132, 48,48, icon="images/Icons/down102.png"),
					
				]
			},
			"temperature":{
				"name":"Temperature",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.changePage("rooms"),lambda:self.scrollButtons(0, 6, absolute=True)], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.changePage("lights"), 146,10, 48,48, icon="images/Icons/lightbulb52.png"),
					inputButton(self, lambda:self.changePage("temperature"), 204,10, 48,48, icon="images/Icons/thermometer53.png"),
					inputButton(self, lambda:self.changePage("outlets"), 262,10, 48,48, icon="images/Icons/electrical28.png"),
				
					inputSlider(self, "temperatureSlider", lambda:self.commitValues(), 20, 17, 23, 0.5, 222,80, 20,100, vertical=True, reversed_=True),
					
					inputLabel(self, "Current: {0}\nSet: {1}", [lambda:float(self.rooms[self.currentRoom]["currentTemperature"]),lambda:float(self.inputsValue["temperatureSlider"])], 202, 80, fontSize=28, align=(1,0)),
					
					inputButton(self, lambda:self.inputs[4].slide(-0.5,True,True), 252,80, 48,48, icon="images/Icons/up154.png"),
					inputButton(self, lambda:self.inputs[4].slide(0.5,True,True), 252,132, 48,48, icon="images/Icons/down102.png"),
					
				]
			},
			"outlets":{
				"name":"Outlets",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, [lambda:self.changePage("rooms"),lambda:self.scrollButtons(0, 6, absolute=True)], 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.changePage("lights"), 146,10, 48,48, icon="images/Icons/lightbulb52.png"),
					inputButton(self, lambda:self.changePage("temperature"), 204,10, 48,48, icon="images/Icons/thermometer53.png"),
					inputButton(self, lambda:self.changePage("outlets"), 262,10, 48,48, icon="images/Icons/electrical28.png"),
				
					inputButton(self, lambda:self.toggleOutlet(self.currentRoom, self.buttonScroll, commit=True), 20,80, 48,48, icon="images/Icons/electrical28.png"),
					inputButton(self, lambda:self.scrollButtons(-1, 1, self.rooms[self.currentRoom]["outlets"]), 20,172, 48,48, icon="images/Icons/left204.png"),
					inputButton(self, lambda:self.scrollButtons(1, 1, self.rooms[self.currentRoom]["outlets"]), 252,172, 48,48, icon="images/Icons/right204.png"),
					
					inputLabel(self, "{0}\n{1}", [lambda:self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["name"],lambda:"ON" if self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["on"] else "OFF"], 78,80, fontSize=20),
					inputLabel(self, "Consumption: {0}", [lambda:self.rooms[self.currentRoom]["outlets"][self.buttonScroll]["consumption"]], 20,138, fontSize=20),
					
					inputLabel(self, "{0} of {1}", [lambda:self.buttonScroll+1,lambda:len(self.rooms[self.currentRoom]["outlets"])], 160,196, fontSize=20, align=(0.5,0.5)),
				]
			},
			"sarah":{
				"name":"Sarah",
				"background":pygame.image.load("images/Backgrounds/1x1.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.AIListen(), 262,10, 48,48, icon="images/Icons/microphone83.png"),
					
					inputLabel(self, "Status:\n{0}", [lambda:"{0}".format(str(self.AI.out)) if str(self.AI.out) else "Idle"], 160, 40, align=(0.5,0.5)),
					inputLabel(self, "{0}", [lambda:"You said: {0}".format(str(self.AI.recognizedText)) if str(self.AI.recognizedText) else ""], 20, 80, w=280, align=(0,0)),
					
				]
			},
			"multimedia":{
				"name":"Multimedia",
				"background":pygame.image.load("images/Backgrounds/1x3.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("house"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.changePage("music"), 146,10, 48,48, icon="images/Icons/musical115.png"),
					inputButton(self, lambda:self.scrollButtons(-6), 204,10, 48,48, icon="images/Icons/left204.png"),
					inputButton(self, lambda:self.scrollButtons(6), 262,10, 48,48, icon="images/Icons/right204.png"),
				]
			},
			"music":{
				"name":"Music",
				"background":pygame.image.load("images/Backgrounds/1x2.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("multimedia"), 10,10, 48,48, icon="images/Icons/house139.png"),
					inputButton(self, lambda:self.inputs[3].slide(-10,True,True), 204,10, 48,48, icon="images/Icons/down102.png"),
					inputButton(self, lambda:self.inputs[3].slide(10,True,True), 262,10, 48,48, icon="images/Icons/up154.png"),
				
					inputSlider(self, "musicVolumeSlider", lambda:self.commitValues(), 100, 0, 100, 1, 78,20, 106,20, vertical=False, reversed_=False),
					inputLabel(self, "Volume: {0}%", [lambda:self.inputsValue["musicVolumeSlider"]], 78,50),
					
					inputButton(self, [lambda:self.setMusicShuffle(1)], 20,172, 48,48, icon="images/Icons/shuffle21.png", condition=lambda:self.music["shuffle"]==False),
					inputButton(self, [lambda:self.setMusicShuffle(0)], 20,172, 48,48, icon="images/Icons/shuffle21.png", condition=lambda:self.music["shuffle"]==True),
					
					inputButton(self, [lambda:self.setMusicLoop(1)], 78,172, 48,48, icon="images/Icons/actualization.png", condition=lambda:self.music["loop"]==False),
					inputButton(self, [lambda:self.setMusicLoop(0)], 78,172, 48,48, icon="images/Icons/actualization.png", condition=lambda:self.music["loop"]==True),
					
					inputButton(self, [lambda:self.setMusicSeek(-1)], 136,172, 48,48, icon="images/Icons/rewind43.png"),
					
					inputButton(self, [lambda:self.setMusicStatus(1)], 194,172, 48,48, icon="images/Icons/arrow626.png", condition=lambda:self.music["playing"]==False),
					inputButton(self, [lambda:self.setMusicStatus(2)], 194,172, 48,48, icon="images/Icons/pause43.png", condition=lambda:self.music["playing"]==True),
					
					inputButton(self, [lambda:self.setMusicSeek(1)], 252,172, 48,48, icon="images/Icons/fast41.png"),
					
					inputLabel(self, "{0}\n{1}\n{2}", [lambda:self.music["title"],lambda:self.music["artist"],lambda:self.music["album"]], 20,80, fontSize=28, maxChar=20)
					
				]
			},
			"mediaRemote":{
				"name":"Remote",
				"background":pygame.image.load("images/Backgrounds/1x0.png").convert_alpha(),
				"inputs":[
					inputButton(self, lambda:self.changePage("home"), 10,10, 48,48, icon="images/Icons/house139.png"),
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
					inputButton(self, lambda:self.changePage("house"), 10,10, 48,48, icon="images/Icons/house139.png"),
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
		}
		self.changePage("home")
	
	def changePage(self, page, room=None):
		self.inputs = self.pages[page]["inputs"]
		self.CurrentPage = page
		if room != None:
			self.changeRoom(room)
		self.sync(syncAllInputs=True)
			
	def changeRoom(self, room):
		self.currentRoom = room
		self.sync(syncAllInputs=True)
		
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
				#self.MQTTSend("sarah/house", "-1,disarm,1")
				
				#Bad idea to send a disarm signal over the network, The
				#security system control panel will be connected through
				#serial
				
				self.changePage("home")
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
		self.MQTTSend("sarah/house", "-1,musicVolume,{0}".format(str(self.inputsValue["musicVolumeSlider"])))
		
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
				if command[1] == "outletConsumption":
					self.setOutletConsumption(int(command[0]), int(command[2]), float(command[3]))
			else:
				if command[1] == "musicVolume":
					self.inputsValue["musicVolumeSlider"] = int(command[2])
					self.sync(syncAllInputs=True)
				if command[1] == "musicStatus":
					if int(command[2]) == 0:
						self.music["status"] = "Stopped"
						self.music["playing"] = False
					elif int(command[2]) == 1:
						self.music["status"] = "Playing"
						self.music["playing"] = True
					elif int(command[2]) == 2:
						self.music["status"] = "Paused"
						self.music["playing"] = False
					self.sync(syncAllInputs=True)
				if command[1] == "musicLoop":
					self.music["loop"] = int(command[2]) == 1
					self.sync(syncAllInputs=True)
				if command[1] == "musicShuffle":
					self.music["shuffle"] = int(command[2]) == 1
					self.sync(syncAllInputs=True)
				if command[1] == "musicTitle":
					t = str(command[2])
					for i in range(3, len(command)):
						t = t+","+str(command[i])
					self.music["title"] = str(t)
					self.sync(syncAllInputs=True)
				if command[1] == "musicArtist":
					t = str(command[2])
					for i in range(3, len(command)):
						t = t+","+str(command[i])
					self.music["title"] = str(t)
					self.sync(syncAllInputs=True)
				if command[1] == "musicAlbum":
					t = str(command[2])
					for i in range(3, len(command)):
						t = t+","+str(command[i])
					self.music["title"] = str(t)
					self.sync(syncAllInputs=True)
		self.sync(syncAllInputs=True)
		
	def MQTTSend(self, topic, msg):
		self.MQTT.client.publish(topic, msg)
		
	def turnOutletOn(self, room, outlet, commit=True):
		self.rooms[room]["outlets"][outlet]["on"] = True
		if commit:
			self.MQTTSend("sarah/house", "{0},outletOn,{1}".format(room,outlet))
			
	def turnOutletOff(self, room, outlet, commit=True):
		self.rooms[room]["outlets"][outlet]["on"] = False
		if commit:
			self.MQTTSend("sarah/house", "{0},outletOff,{1}".format(room,outlet))
				
	def toggleOutlet(self, room, outlet, commit=True):
		self.rooms[room]["outlets"][outlet]["on"] = not self.rooms[room]["outlets"][outlet]["on"]
		if commit:
			if self.rooms[room]["outlets"][outlet]["on"]:
				self.MQTTSend("sarah/house", "{0},outletOn,{1}".format(room,outlet))
			else:
				self.MQTTSend("sarah/house", "{0},outletOff,{1}".format(room,outlet))
				
	def setOutletConsumption(self, room, outlet, consumption=0):
		self.rooms[room]["outlets"][outlet]["consumption"] = consumption
		
	def setMusicStatus(self, status):
		self.MQTTSend("sarah/house", "-1,musicStatus,{0}".format(status))
		
	def setMusicLoop(self, loop):
		self.MQTTSend("sarah/house", "-1,musicLoop,{0}".format(loop))
		
	def setMusicShuffle(self, shuffle):
		self.MQTTSend("sarah/house", "-1,musicShuffle,{0}".format(shuffle))
	
	def setMusicSeek(self, seek):
		self.MQTTSend("sarah/house", "-1,musicSeek,{0}".format(seek))
		
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
		
