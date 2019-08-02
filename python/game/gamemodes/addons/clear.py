NAME 	= "Clear"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
COMMANDS = {
	"clear": ["Will reload the current map."]
}
PERMISSIONS = {
	"chat": {
		"clear": 21
	}
}
HIDDEN = 1

import host
import bf2
from game.gamemodes.sbxErrorHandling import ExceptionOutput

class Addon:
	def __init__(self, core):
		self.core = core
		self.remove_previous_map = False

	def onGameStatusChanged(self, status):
		if status == bf2.GameStatus.Playing and self.remove_previous_map == True:
			self.removemap()

	def removemap(self):
		cmid = int(host.rcon_invoke("mapList.currentMap"))
		host.rcon_invoke("mapList.remove " + str(cmid))
		self.remove_previous_map = False

	def chat_clear(self, p, params):
		cmid = int(host.rcon_invoke("mapList.currentMap"))
		host.rcon_invoke("mapList.insert " + str(cmid + 1) + " " + host.sgl_getMapName().lower() + " gpm_cq 64")
		self.remove_previous_map = True
		host.sgl_endGame(0,0)