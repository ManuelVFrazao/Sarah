import pymysql

class SarahMySQL():
	def __init__(self, class_, host='localhost', port=3306, user='Sarah', passwd='SarahAI2016', db='Sarah'):
		self.class_ = class_
		
		self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)

		self.cur = self.conn.cursor()

		#cur.execute("INSERT INTO tblRooms (Name, Description) VALUES ('Master bedroom','')")
		#conn.commit()

		#cur.execute("SELECT Name FROM tblRooms")

		#print(cur.description)

		#print()

		#for row in cur:
		#	print(row)
	def close(self):
		self.cur.close()
		self.conn.close()
		
	def load(self):
		self.class_.rooms = []
		
		self.cur.execute("SELECT pkRooms, Name FROM tblRooms ORDER BY pkRooms")
		rooms = list(self.cur).copy()
		for row in rooms:
			pkRoom = row[0]
			room = {"name":row[1],"lights":[],"outlets":[]}
			
		
			self.cur.execute("SELECT SetTo, Current FROM tblHeaters WHERE fkRooms = {0} LIMIT 1".format(pkRoom))
			for temperature in self.cur:
				room["temperature"]=float(temperature[0])
				room["currentTemperature"]=float(temperature[1])
			
			
			self.cur.execute("SELECT Name, Red, Green, Blue FROM tblLights WHERE fkRooms = {0} ORDER BY pkLights".format(pkRoom))
			for light in self.cur:
				room["lights"] = room["lights"] + [{"name":light[0], "lightR":light[1], "lightG":light[2], "lightB":light[3]}]
			
			self.cur.execute("SELECT Name, IsOn, Consumption FROM tblOutlets WHERE fkRooms = {0} ORDER BY pkOutlets".format(pkRoom))
			for outlet in self.cur:
				room["outlets"] = room["outlets"] + [{"name":outlet[0], "on":outlet[1], "consumption":outlet[2]}]
			
			print(room)
			
			self.class_.rooms = self.class_.rooms + [room]
		
		self.class_.mediaDevices = []
		self.cur.execute("SELECT pkDevices, Name, SetTo FROM tblDevices ORDER BY pkDevices")
		devices = list(self.cur).copy()
		for row in devices:
			pkDevice = row[0]
			device = {"name":row[1], "setTo":row[2]}
			
			self.class_.mediaDevices = self.class_.mediaDevices + [device]
			
