import paho.mqtt.client as mqtt
import time

class SarahMQTT():
	def __init__(self, host="localhost", port=1883, keepalive=60, start=True, topic="sarah/house"):
		self.client = mqtt.Client()
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		
		self.topic = topic

		self.client.connect(host, port, keepalive)
		
		if start:
			self.client.loop_start()

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		client.subscribe(self.topic)

	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic+" "+str(msg.payload))

if __name__ == "__main__":
	SarahMqtt = SarahMQTT()
	while True:
		time.sleep(1)
		print("...")
