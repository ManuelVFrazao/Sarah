import serial

class SarahSerial():
	def __init__(self):
		try:
			self.serial = serial.Serial('/dev/tty0')
		except Exception as e:
			print("can't open serial: {0}".format(e))
		

if __name__ == "__main__":
	SarahSer = SarahSerial()
