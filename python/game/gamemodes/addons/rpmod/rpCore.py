import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput

class rpCore:
	
	def coreTickSec(self):
		try:
			#auto kill to fix first spawn
			for kp in self.core.getAllPlayers():
				if kp.rpFirstSpawn == 1:
					if kp.timeToKill > 0:
						kp.timeToKill -= 1
					else:
						name = kp.getName().split(" ")[-1]
						kp.rpFirstSpawn = 2
						self.rp_kill(kp, [name])
		except:
			ExceptionOutput()
			
		if self.status == "Work":
			try:
				if self.salTimer > 0:
					self.salTimer -= 1
				else:
					for p in self.core.getAlivePlayers():
						self.players[self.getName(p)]["bank"] += int(self.jobs[self.players[str(self.getName(p))]["job"]]["salary"])
					self.salTimer = int(self.settings["salarytime"])
					self.core.sendMsg("§3§C1001EVERYONE GOT PAID")
			except:
				self.salTimer = 0
	def sendRcon(p, msgFrom, msgBody):
		plid = p.index
		host.rcon_feedback(plid, "============ MESSAGE RECIEVED ============")
		host.rcon_feedback(plid, " ")
		host.rcon_feedback(plid, "Sent by: " + str(msgFrom))
		host.rcon_feedback(plid, "Body: ")
		host.rcon_feedback(plid, "     " + str(msgBody))
		host.rcon_feedback(plid, " ")
		host.rcon_feedback(plid, "==========================================")
		p.sendMsg("Message Received, open console with the Tildy(Left to your 1) or your End Button")
	
	
	def coreTickHalfSec(self):
		pass
	
	def coreTickFrame(self):
		pass
	
	def rconcmd(self, command):
		try:
			host.rcon_invoke(str(command))
		except:
			self.core.sendMsg("Unable to execute rcon command")
			ExceptionOutput()

	def printList(self, oList):
		count = -0
		cCount = 0
		listTxt = ""
		allLists = []
		for cCode in oList:
			if count == -0:
				listTxt += " " + cCode
				count = 0
			else:
				listTxt += ", " + cCode
			if count < 9:
				count += 1
			else:
				allLists.append(listTxt)
				listTxt = ""
				count = 0
			cCount += 1
			numofcodes = len(oList)
			if cCount == numofcodes:
				allLists.append(listTxt)
		return allLists
				
	
	def getPlayerName(self, playerName):
		player = playerName.lower()
		foundPlayers = []
		found = 0
		if player == "*":
			return self.core.getAllPlayers()
		for p in self.core.getAllPlayers():
			if p.getName().lower().find(player) != -1:
				foundPlayers.append(p)
				found += 1

		if found == 0:
			return None
		else:
			return foundPlayers
	
	def payJob(self, job, amount):
		for p in self.core.getAlivePlayers():
			pos = self.getPos(p)
			name = p.getName().split(" ")[-1]
			if pos:
				if pos[0] == str(job):
					self.players[str(name)]["bank"] += amount
	
	def payPlayer(self, pFrom, pTo, amount):
		pFromName = self.getName(pFrom)
		if str(pTo) != "sencity":
			pToName = self.getName(pTo)
		else:
			pToName = "sencity"
		if self.players[str(pFromName)]["Bank"] - amount >= 0:
			self.players[str(pFromName)]["Bank"] -= amount
			if pToName != "sencity":
				self.players[str(pToName)]["Bank"] += amount
			return True
		else:
			return False
	
	def getName(self, p):
		return p.getName().split(" ")[-1]
	