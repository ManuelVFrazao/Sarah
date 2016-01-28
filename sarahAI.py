import time
import subprocess
import re
import threading
import calendar
import random
import datetime

import wolframalpha
import speech_recognition as sr

class SarahAI():
	def __init__(self, witaiKey="JNYZAMPZ7IFASATUY5PQSGDNGKV7HL5E", wolframalphaKey="TKRT9H-AV9W8WRR8V"):
		self.WolframClient = wolframalpha.Client(wolframalphaKey)
		self.recog = sr.Recognizer()
		self.mic = sr.Microphone()
		with self.mic as source:
			self.recog.adjust_for_ambient_noise(source)
			
		self.isTriggered = False
		self.keepListening = False
		self.talkProcess = None
		
		self.witAiKey = witaiKey
		
		self.out = ""
		self.recognizedText = ""
		
		self.mqtt = None
		
		self.rooms = [
			"Kitchen",
			"Living Room",
		]
		
		self.catchPhrases = {
			"hello":[
				"Hello",
				"Hi",
				"Hello there",
				"Hi there",
				"Hey there",
			],
			"thankYou":[
				"No problem",
				"My pleasure",
				"You're welcome",
			],
			"turnOnLight":[
				"Alright",
				"Very well",
				"Right away",
				"Will do",
				"I'll open the light",
				"I'll turn on the light",
				"Let there be light",
				"And then, there was light",
			],
			"turnOffLight":[
				"Alright",
				"Very well",
				"Right away",
				"Will do",
				"I'll close the light",
				"I'll turn off the light",
			],
			"setTemperature":[
				"Alright",
				"Very well",
				"Right away",
				"Will do",
				"I'll set the temperature",
			],
			"openDoor":[
				"Alright",
				"Very well",
				"Right away",
				"Will do",
				"I'll open the door",
			],
			
			
			"MyName":[
				"I am Sarah, an artificial intelligence for home automation",
				"My name is Sarah, I'm an artificial intelligence for home automation",
				"I am Sarah",
				"My name is Sarah",
			],
			"MyCreator":[
				"I was created by Manuel Verville-Frazao",
				"My creator is Manuel Verville-Frazao",
			],
			"MyAge":[
				"I was created in January 2016",
				"My creator started developing me in January 2016"
			],
		}
	
	def ask(self, query, tellAll=False):
		print("Searching for:", query)
		self.out = "Searching"
		res = self.WolframClient.query(query)
		
		if len(res.pods):
			#for idx,pod in enumerate(res.pods):
			result = []
			try:
				for pod in res.pods:
					#print(pod)
					if pod.text:
						#print(pod.title, pod.text)
						#self.say(pod.text)
						numSubpod = 0
						subpodText = ""
						for subpod in pod:
							subpodText = subpodText + " \n " +subpod.title + " | " + subpod.text
						result = result + [{"title":pod.title,"text":subpodText}]
			except:
				print("Error parsing")
				pass
			print(result)
			#self.out = str(result[0])
			self.out = "Outputing results"
			if tellAll:
				for r in result:
					self.say(r["title"] + ":" + r["text"])
			else:
				if len(result) >= 2:
					self.say(result[1]["text"])
				else:
					self.say(result[0]["text"])
		else:
			print( len(res.pods))
			self.out = "No results"
			self.say("No results")
	
	def listen(self):
		self.out = "Listening"
		#self.recog.listen_in_background(self.mic, self.analyse)
		#with sr.WavFile("test2.wav") as source:
		#	self.analyse(r, r.record(source))
		with self.mic as source:
			try:
				audio = self.recog.listen(source, 10)
				if audio:
					self.analyse(self.recog, audio)
			except:
				return
		
	def analyse(self, recognizer, audio):
		try:
		# for testing purposes, we're just using the default API key
		# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
		# instead of `r.recognize_google(audio)`
			self.out = "Analysing"
			result = recognizer.recognize_wit(audio, self.witAiKey, True)
			print("WIT.AI thinks you said " + str(result))
			self.testCommands(result)
		except sr.UnknownValueError:
			print("WIT.AI could not understand audio")
			self.say("Sorry, I did not understand")
		except sr.RequestError as e:
			print("Could not request results from WIT.AI; {0}".format(e))
			self.say("Sorry, I could not get results for your command because {0}".format(e))
				
	def formatResponse(self, res):
		res = re.sub("&quot;", "'", res)
		
		res = re.sub("\|\|", ' Or ', res)
		res = re.sub("\^_", ' repeating ', res)
		res = re.sub("\^", ' to the ', res)
		
		res = re.sub("\n", ' <break time="1000ms"/> ', res)
		res = re.sub("\|", ' <break time="500ms"/> ', res)
		res = re.sub("\(", ' <break time="500ms"/> ', res)
		res = re.sub("\)", ' <break time="500ms"/> ', res)
		res = re.sub(":", ' <break time="500ms"/> ', res)
		res = re.sub("_", ' <break time="100ms"/> ', res)
		print(res)
		return res
	
	def testCommands(self, command):
		if len(command["outcomes"]):
			_text = command["outcomes"][0]["_text"]
			intent = command["outcomes"][0]["intent"]
			confidence = command["outcomes"][0]["confidence"]
			entities = command["outcomes"][0]["entities"]
			print(_text, intent, confidence)
			self.recognizedText = _text
			print()
			
			if self.isTriggered or "TriggerWord" in entities:
				self.isTriggered = self.keepListening
				if intent == "StartListening":
					self.isTriggered = True
					self.say("I'm listening!")
				elif intent == "keepListening":
					self.isTriggered = True
					self.keepListening = True
					self.say("Will do")
				elif intent == "stopListening":
					self.isTriggered = False
					self.keepListening = False
					self.say("Alright")
				elif intent == "searchAbout":
					if "search_query" in entities:
						if "tellAll" in entities:
							#print("searchWolfram", entities["wolfram_search_query"][0]["value"])
							self.ask(entities["search_query"][0]["value"], True)
						else:
							self.ask(entities["search_query"][0]["value"])
				elif intent == "getMath":
					if "math_expression" in entities:
						self.ask(entities["math_expression"][0]["value"])
				elif intent == "getWeather":
					location = "Montreal"
					timeAndDate = {"date":"today","time":"now"}
					timeAndDate2 = None
					
					if "location" in entities:
						location = entities["location"][0]["value"]
					if "datetime" in entities:
						if entities["datetime"][0]["type"] == "value":
							if "value" in entities["datetime"][0]:
								timeAndDate = self.getDateFromWit(entities["datetime"][0]["value"], entities["datetime"][0]["grain"])
						elif entities["datetime"][0]["type"] == "interval":
							if "from" in entities["datetime"][0]:
								timeAndDate = self.getDateFromWit(entities["datetime"][0]["from"]["value"], entities["datetime"][0]["from"]["grain"])
							if "to" in entities["datetime"][0]:
								timeAndDate2 = self.getDateFromWit(entities["datetime"][0]["to"]["value"], entities["datetime"][0]["to"]["grain"])
							
					if timeAndDate2:
						q = "Weather {0} {1} {2} to {3} {4}".format(location, timeAndDate["date"], timeAndDate["time"], timeAndDate2["date"], timeAndDate2["time"])
					else:
						q = "Weather {0} {1} {2}".format(location, timeAndDate["date"], timeAndDate["time"])
					print(q)
					self.ask(q)
				elif intent == "setReminder":
					if "reminder" in entities:
						if "datetime" in entities:
							print("setReminder", entities["reminder"][0]["value"], entities["datetime"][0]["value"])
						else:
							print("setReminder", entities["reminder"][0]["value"])
				elif intent == "setTemperature":
					if "room" in entities and "temperature" in entities:
						#print("setTemperature", entities["room"][0]["value"], entities["temperature"][0]["value"])
						numRoom = self.getRoom(entities["room"][0]["value"])
						self.sendMqtt("{0},temperature,{1}".format(numRoom, entities["temperature"][0]["value"]))
						if float(entities["temperature"][0]["value"]) >= 21:
							print("Hot")
							self.say(self.pickCatchPhrase("setTemperature"))
						elif float(entities["temperature"][0]["value"]) <= 19:
							print("cold")
							self.say(self.pickCatchPhrase("setTemperature"))
						else:
							print("normal")
							self.say(self.pickCatchPhrase("setTemperature"))
				elif intent == "setLight":
					if "room" in entities and "on_off" in entities:
						#print("setLight", entities["room"][0]["value"], entities["on_off"][0]["value"])
						numRoom = self.getRoom(entities["room"][0]["value"])
						if entities["on_off"][0]["value"] == "on":
							self.sendMqtt("{0},lightR,255;{0},lightG,255;{0},lightB,255".format(numRoom))
							self.say(self.pickCatchPhrase("turnOnLight"))
						else:
							self.sendMqtt("{0},lightR,0;{0},lightG,0;{0},lightB,0".format(numRoom))
							self.say(self.pickCatchPhrase("turnOffLight"))
				elif intent == "openDoor":
					self.sendMqtt("-1,openDoor,1")
					self.say(self.pickCatchPhrase("openDoor"))
			else:
				if intent == "StartListening":
					self.isTriggered = True
					self.say("Yes?")

	def say(self, sentence, voice="mb-us1", speed=130, pitch=60): #voice="en-us+f4", speed=145
		#self.stopTalking()
		self.talkProcess = subprocess.Popen(["espeak", "-m", '"'+str(self.formatResponse(sentence))+'"', "-pho", "-v", str(voice), "-s", str(speed), "-p", str(pitch)])
		self.talkProcess.wait()
		self.talkProcess = None
		time.sleep(0.2)
		
	def stopTalking(self):
		if self.talkProcess:
			self.talkProcess.terminate()
			self.talkProcess = None
			
	def getDateFromWit(self, dateToConvert, grain="day"):
		convertedDate = {}
		convertedDate["date"] = re.search('(.+)T', dateToConvert).group(1)
		convertedDate["dateYear"] = re.search("^(.+?)\-.+$", convertedDate["date"]).group(1)
		convertedDate["dateMonth"] = re.search("^.+\-(.+?)\-.+$", convertedDate["date"]).group(1)
		convertedDate["dateMonthName"] = calendar.month_name[int(convertedDate["dateMonth"])]
		convertedDate["dateDay"] = re.search("^.+\-(.+?)$", convertedDate["date"]).group(1)
		
		convertedDate["time"] = re.search('T(.+)\.', dateToConvert).group(1)
		if grain != "hour" and  grain != "minute" and grain != "second":
			convertedDate["time"] = "12:00:00"
		
		return convertedDate
	
	def pickCatchPhrase(self, topic):
		random.seed(datetime.datetime.now())
		num = random.randint(0, len(self.catchPhrases[topic])-1)
		return self.catchPhrases[topic][num]
		
	def sendMqtt(self, command):
		print(self.mqtt, command)
		if self.mqtt:
			self.mqtt.send(command)
			
	def getRoom(self, roomName):
		roomNum = -1
		
		for i, v in enumerate(self.rooms):
			if v.lower() == roomName.lower():
				roomNum = i
				break
		
		return roomNum
			
class aiThread(threading.Thread):
	def __init__(self, ai):
		threading.Thread.__init__(self)
		self.listen = False
		self.keepListening = False
		self.ai = ai
		
	def run(self):
		while True:
			if self.listen:
				self.ai.listen()
				if (not self.keepListening) and (not self.ai.isTriggered):
					self.listen = False
			self.ai.out = ""
			self.ai.recognizedText = ""
			time.sleep(0.1)

class aiMqtt():
	def __init__(self, mqttClient, topic):
		self.mqttClient = mqttClient
		self.topic = topic
		
	def send(self, msg):
		self.mqttClient.publish(self.topic, msg)
				
if __name__ == "__main__":
	SarahAi = SarahAI()
	print(SarahAi.getDateFromWit('2016-01-18T00:00:00.000-05:00'))
	while True:
		SarahAi.listen()
		
