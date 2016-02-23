import serial
import threading
import time

class SarahSerial():
	def __init__(self, port='/dev/tty.usbserial', baud=9600):
	#def __init__(self, port='/dev/tty0', baud=9600):
		self.serial = None
		try:
			self.serial = serial.Serial(port, baud)
		except Exception as e:
			print("can't open serial: {0}".format(e))
			
	def send(self, data):
		if self.serial:
			self.serial.write(data)
		
	def receive(self):
		if self.serial:
			return self.serial.readline()
			
class SerialThread(threading.Thread):
	def __init__(self, serial_):
		threading.Thread.__init__(self)
		self.serial = serial_
		self.pool = ["serialThreadInitiated"]
		self.sendpool = []
		
	def run(self):
		while True:
			serialCom = self.serial.receive()
			if serialCom:
				self.pool = self.pool + [serialCom]
			if len(self.sendpool) > 0:
				self.serial.send(self.sendpool.pop(0))
			
	def pop(self):
		if len(self.pool) > 0:
			return self.pool.pop(0)
			
	def send(self, data):
		self.sendpool = self.sendpool + [data]
	
	

if __name__ == "__main__":
	SarahSer = SarahSerial()
