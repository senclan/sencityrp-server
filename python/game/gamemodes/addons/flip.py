NAME 	= "Flip"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
COMMANDS = {
	"flip": ["Will reset your vehicles rotation when typing [@flip]"]
}

class Addon:

	def __init__(self, core):
		self.core = core

	def chat_flip(self, p, params):
		if p.getVehicle() != p.getDefaultVehicle():
			pRot = p.getVehicle().getRotation()
			p.getVehicle().setRotation((pRot[0],pRot[1],0.0))

	def rcon_flip(self, p, params):
		self.chat_flip(p, params)