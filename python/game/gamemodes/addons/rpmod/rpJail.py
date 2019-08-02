import host

class jail:
	def rp_job_arrest(self, p, params, value):
		pl = params[0]
		pl = self.getPlayerName(str(pl))[0]
		player = pl.getName().split(" ")[-1]
		try:
			self.rp_kill(None, [str(player)])
		except:
			print "Unable to kill player"
		jail = self.getNextJail()
		if self.jailPos.has_key(str(jail)):
			if not self.players[str(player)].has_key("jailed"):
				self.jailPos[jail][0] += 1
			self.players[str(player)]["jailed"] = str(jail)
			self.players[str(player)]["jailtime"] = int(self.settings["jailtime"])
			self.core.sendMsg("Player " + str(pl.getName()) + " has been sent to jail")
			print "Player " + pl.getName() + " sent to jail " + jail
		else:
			p.sendMsg("Jail not found")
	
	def rp_job_unarrest(self, p, params, value):
		pl = params[0]
		pl = self.getPlayerName(str(pl))[0]
		player = pl.getName().split(" ")[-1]
		if self.players[str(player)].has_key("jailed"):
			self.jailPos[self.players[str(player)]["jailed"]][0] -= 1
			print "Player " + pl.getName() + " removed from jail " + self.players[str(player)]["jailed"]
			del self.players[str(player)]["jailed"]
			del self.players[str(player)]["jailtime"]
			try:
				self.rp_kill(None, [str(player)])
			except:
				print "Unable to kill player"
			self.core.sendMsg("Player " + str(pl.getName()) + " has been set free from jail")
		else:
			if p:
				p.sendMsg("Player not in a jail")
			else:
				self.core.sendMsg("Host - Player not in a jail")
	

	def rp_amjailed(self, p, params):
		name = p.getName().split(" ")[-1]
		if self.players[str(name)].has_key("jailed"):
			p.sendMsg("Yes, you are jailed for " + str(self.players[str(name)]["jailtime"]) + " more seconds")
		else:
			p.sendMsg("No, you are not jailed")
	
	def rp_jailinfo(self, p, params):
		jail = params[0]
		if self.jailPos.has_key(jail):
			self.core.sendMsg(str(jail) + " Info = Num. Players: " + str(self.jailPos[jail][0]))
		else:
			p.sendMsg("Jail not found")


	def getNextJail(self):
		lowestNum = 100
		jailName = ""
		print "Selecting Jail....."
		for jail in self.jailPos:
			if self.jailPos[jail][0] < lowestNum:
				lowestNum = self.jailPos[jail][0]
				jailName = jail
		if jailName == "":
			print "No jail selected"
			return None
		else:
			print "Jail: " + jailName + " Selected."
			return jailName
	