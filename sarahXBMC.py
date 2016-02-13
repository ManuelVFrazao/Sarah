from xbmcjson import XBMC, PLAYER_VIDEO
#Login with default xbmc/xbmc credentials
#xbmc = XBMC("http://127.0.0.1:8080/jsonrpc")

#print(xbmc.GUI.ActivateWindow(window="weather"))
#print(xbmc.GUI.ShowNotification(title="Title", message="Hello notif"))
#print(xbmc.Application.SetVolume(volume=100))
#print(xbmc.Player.GetItem(playerid=1))

class SarahXBMC():
	def __init__(self):
		self.players = {}
		
	def newPlayer(self, ip, port="8080"):
		xbmc = XBMC("http://" + ip + ":" + port + "/jsonrpc")
		try:
			xbmc.JSONRPC.Ping()
		except Exception as e:
			print(e)
		else:
			self.players[ip] = xbmc
			
	def notify(self, player, title="", message=""):
		if player in self.players:
			self.players[player].GUI.ShowNotification(title=title, message=message)



if __name__ == "__main__":
	sarahXbmc = SarahXBMC()
	sarahXbmc.newPlayer("127.0.0.1", "8080")
	sarahXbmc.notify("127.0.0.1","hello","world")
