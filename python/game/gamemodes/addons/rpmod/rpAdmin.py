import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput
class Admin:

	def loadAdmins(self):
		try:
			loadAdmin = open(self.rpModSettingsDir + "Admins.txt", "r")
			for info in loadAdmin:
				info = info.replace("\n", "")
				info = info.replace("\r", "")
				pInfo = info.split(" = ")
				self.admins[str(pInfo[0])] = int(pInfo[1])
			loadAdmin.close()
			self.setAdmins()
			print "Admins loaded"
		except:
			print "Failed Loading Admins"
			ExceptionOutput()
	
	def saveAdmins(self, p, level):
		try:
			name = self.getName(p)
			saveAdmin = open(self.rpModSettingsDir + "Admins.txt", "a")
			saveAdmin.write(str(name) + " = " + str(level) + "\n")
			saveAdmin.close()
			self.loadAdmins()
		except:
			print "Failed Saving Admins Admins"
			ExceptionOutput()
	
	def setAdmins(self):
		for p in self.core.getAllPlayers():
			if self.admins.has_key(str(self.getName(p))):
				p.level = int(self.admins[str(self.getName(p))])
			else:
				p.level = 1
				
	def setAdmin(self, p):
		if self.admins.has_key(str(self.getName(p))):
			p.level = int(self.admins[str(self.getName(p))])
		else:
			p.level = 1
	
	def rp_loadadmin(self, p, params):
		try:
			self.loadAdmins()
			p.sendMsg("Loaded Admins")
		except:
			p.sendMsg("Unable to Load Admins")
			ExceptionOutput()
	
	def rp_saveadmin(self, p, params):
		name = params[0]
		pl = self.getPlayerName(name)[0]
		level = int(params[1])
		try:
			self.saveAdmins(pl, level)
			p.sendMsg("Admin Added")
		except:
			p.sendMsg("Unable to Save Admin")
			ExceptionOutput()
	
	
		
	def rp_change(self, p, params):
		self.maxObjects = int(params[0])
		p.sendMsg("Changed")

	def rp_mtp(self, p, params):
		pl = self.getPlayerName(str(params[0]))[0]
		p.setPosition(pl.getPosition())
	
	def rp_addpos(self, p, params):
		if not self.players[self.getName(p)].has_key("positions"):
			self.players[self.getName(p)]["positions"] = {}
			
		self.players[self.getName(p)]["positions"][str(params[0])] = p.getPosition()
		p.sendMsg("Position Set")
	
	def rp_getpos(self, p, params):
		p.setPosition(self.players[self.getName(p)]["positions"][str(params[0])])
		p.sendMsg("Moved")