import serial

class SarahSerial():
	def __init__(self, port='/dev/tty.usbserial', baud=9600):
		try:
			self.serial = serial.Serial(port, baud)
		except Exception as e:
			print("can't open serial: {0}".format(e))
	
	def send(self, data):
		if self.serial:
			self.serial.write(data)
		

if __name__ == "__main__":
	SarahSer = SarahSerial()
