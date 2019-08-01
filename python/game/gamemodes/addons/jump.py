NAME 	= "Jump"
VERSION = "1.0"
AUTHOR 	= "Elton 'Elxx' Muuga"
WEBSITE = "http://labs.elxx.net"
COMMANDS = {
	"ju": ["distance","Jump upwards a total of [distance] meters."]
}

class Addon:
	def __init__(self, core):
		self.core = core

	def chat_ju(self, p, params):
		if p.getVehicle() != p.getDefaultVehicle(): return
		y = float(params[0])
		pPos = p.getPosition()
		x = pPos[1] + float(y)
		if float(x) > 10000.0:
			x = 10000.0
		if float(x) < 0.0:
			x = 0.0
		p.setPosition((pPos[0],float(x),pPos[2]))

	def rcon_ju(self, p, params):
		self.chat_ju(p, params)