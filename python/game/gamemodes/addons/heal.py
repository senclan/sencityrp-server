NAME 	= "Heal"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
COMMANDS = {
	"heal": ["Will heal you and your vehicle."],
	"autoheal": ["Will toggle automatic healing."]
}

import bf2
from game.gamemodes.sbxErrorHandling import ExceptionOutput

class Addon:

	def __init__(self, core):
		self.core = core

	def onPlayerConnect(self, playerObject):
		playerObject.autoheal = False

	def onGameStatusChanged(self, status):
		for p in self.core.getAllPlayers():
			p.autoheal = False

	def chat_autoheal(self, p, params):
		if p.autoheal:
			p.autoheal = False
			p.sendMsg("AUTOHEAL_OFF")
		else:
			p.autoheal = True
			p.sendMsg("AUTOHEAL_ON")

	def chat_heal(self, p, params):
		if p.isAlive():
			try:
				if p.getVehicle() == p.getDefaultVehicle():
					p.getDefaultVehicle().setDamage(999999999)
				else:
					p.getVehicleRoot().setDamage(999999999)
			except: pass

	def rcon_autoheal(self, p, params):
		self.chat_autoheal(p, params)

	def rcon_heal(self, p, params):
		self.chat_heal(p, params)

	def tickFrame(self):
		self.autoheal()

	def autoheal(self):
		for p in self.core.getAlivePlayers():
			if p.autoheal:
				if p.isAlive():
					try:
						if p.getVehicle() == p.getDefaultVehicle():
							p.getDefaultVehicle().setDamage(999999999)
						else:
							p.getVehicleRoot().setDamage(999999999)
					except: pass