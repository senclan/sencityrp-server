NAME 	= "Cookie"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
COMMANDS = {
	"cookie": ["Gives you a free internet cookie each round."]
}

import bf2

class Addon:

	def __init__(self, core):
		self.core = core
		self.nomnomnom = False
		self.nomnomname = ""

	def onPlayerConnect(self, playerObject):
		playerObject.cookie = False

	def onGameStatusChanged(self, status):
		for p in self.core.getAllPlayers():
			p.cookie = False
		self.nomnomnom = False
		self.nomnomname = ""

	def chat_cookie(self, p, params):
		if p.cookie == True:
			p.sendMsg("You already ate a cookie :0")
		if p.cookie == False and self.nomnomnom == False:
			p.sendMsg("Whee :3 Cookie")
			p.cookie = True
		if p.cookie == False and self.nomnomnom == True:
			p.sendMsg(str(self.nomnomname) + " ate your cookie :0!")

	def chat_nomnomnom(self, p, params):
		name = p.getName().split(" ")[-1]
		if name == "Bullace" or name == "Elxx":
			if self.nomnomnom == False:
				self.core.sendMsg(str(name) + " ate all the cookies! Noes D:")
				self.nomnomnom = True
				self.nomnomname = name