NAME 	= "Mutiny"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
HIDDEN = 1
DESCRIPTION = "Will hide the commander button, if a player somehow still becomes commander he will be warned for 30 seconds and get kicked if he doesn't resign"
COMMANDS = {
	"commander": ["on/off","Toggles kicking commander and will show/hide commander application button."]
}
PERMISSIONS = {
	"chat": {
		"commander": 21
	}
}

import bf2
import host

class Addon:

	def __init__(self, core):
		self.core = core
		self.mutiny = True

	def onPlayerConnect(self, playerObject):
		playerObject.commander = 0

	def onGameStatusChanged(self, status):
		host.sh_setEnableCommander(0)
		for p in self.core.getAllPlayers():
			p.commander = 0

	def chat_commander(self, p, params):
		if params[0] == "on":
			self.mutiny = False
			host.sh_setEnableCommander(1)
		if params[0] == "off":
			self.mutiny = True
			host.sh_setEnableCommander(0)

	def tickOneSec(self):
		if self.mutiny == True:
			for p in self.core.getAllPlayers():
				if p.isCommander():
					p.commander += 1
					time = 30 - p.commander
					if p.commander <= 30 and p.commander >= 0:
						p.sendMsg("You have " + str(time) + " seconds to resign your commander position or you will be kicked! ***")
					if p.commander == 31:
						p.commander = 0
						host.rcon_invoke('PB_SV_Kick ' + str(p.getName()) + ' 0 Sorry but being a commander is forbidden.')
				else: p.commander = 0