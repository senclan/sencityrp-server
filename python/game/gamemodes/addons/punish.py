NAME 	= "Punish"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
HIDDEN = 1
COMMANDS = {
	"punish": ["player ID","seconds","Will kill the player and set his spawntime to [seconds]"]
}
PERMISSIONS = {
	"chat": {
		"punish": 21
	}
}

import bf2

class Addon:

	def __init__(self, core):
		self.core = core

	def onPlayerConnect(self, playerObject):
		playerObject.punish = False
		playerObject.punishtime = 0
		playerObject.autoheal = False

	def onGameStatusChanged(self, status):
		for p in self.core.getAllPlayers():
			p.punish = False
			p.punishtime = 0
			p.autoheal = False

	def chat_punish(self, p, params):
		player = self.core.getPlayerByIndex(int(params[0]))
		player.punish = True
		player.punishtime = int(params[1])
		try:
			if player.autoheal == True:
				player.autoheal = False
			if player.getVehicle() == player.getDefaultVehicle():
				player.getDefaultVehicle().setDamage(0.1)
			else:
				player.getVehicleRoot().setDamage(0.1)
		except: pass

	def onPlayerDeath(self, playerObject, soldierObject):
		if playerObject.punish == True:
			playerObject.setTimeToSpawn(playerObject.punishtime)
			playerObject.punish = False