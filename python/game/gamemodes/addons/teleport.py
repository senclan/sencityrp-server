NAME 	= "Teleport"
VERSION = "1.0"
AUTHOR 	= "Elxx & Bullace"
WEBSITE = "http://labs.elxx.net & http://sandboxaddicted.com"
DESCRIPTION = "Allows you to save your current location and travel back to it later."
HIDDEN = 1

import bf2

class Addon:
	def __init__(self, core):
		self.core = core

	def onPlayerConnect(self, playerObject):
		playerObject.teleportLocations = {}

	def onGameStatusChanged(self, status):
		for p in self.core.getAllPlayers():
			p.teleportLocations = {}

	def rcon_btnTeleport(self, p, params):
		idx = int(params[0])
		if p.teleportLocations.has_key(idx) and p.getVehicle() and p.isAlive():
			try:
				if p.getVehicle() == p.getDefaultVehicle():
					p.getVehicle().setPosition((p.teleportLocations[idx][0][0],p.teleportLocations[idx][0][1] + 1.0,p.teleportLocations[idx][0][2]))
					#p.sendMsg("TELEPORTEDTOLOCATION_" + str(params[0]))
			except:
				ExceptionOutput()

	def rcon_btnSetTeleport(self, p, params):
		idx = int(params[0])
		if p.getVehicle() and p.isAlive():
			try:
				p.teleportLocations[idx] = [p.getVehicle().getPosition(),p.getVehicle().getRotation()]
				p.sendMsg("LOCATIONSAVEDAS_" + str(params[0]))
			except:
				ExceptionOutput()