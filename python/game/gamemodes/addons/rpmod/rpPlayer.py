import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput
class players:
	
	
	def playerTickSec(self):
		#hunger
		try:
			for checkTime in self.core.getAlivePlayers():
				name = checkTime.getName().split(" ")[-1]
				if self.players[str(name)].has_key("timetillhungery"):
					if int(self.players[str(name)]["timetillhungery"]) == 100:
						checkTime.sendMsg("You have 100 Seconds before you need to eat or you will start to die")
					
					if int(self.players[str(name)]["timetillhungery"]) == 10:
						checkTime.sendMsg("You have 10 Seconds before you need to eat or you will start to die")
					
					if int(self.players[str(name)]["timetillhungery"]) == 1:
						checkTime.sendMsg("Your now dieing due to not eating, get to a restaurant and eat asap")
		except:
			print "Unable to run Hunger Notifier"
			ExceptionOutput()
			
		try:
			for hp in self.core.getAlivePlayers():
				name = hp.getName().split(" ")[-1]
				if not self.players[str(name)].has_key("timetillhungery"):
					self.players[str(name)]["timetillhungery"] = int(self.settings["timetillhungery"])
				self.players[str(name)]["timetillhungery"] -= 1
				if self.players[str(name)]["timetillhungery"] <= 0:
					self.players[str(name)]["timetillhungery"] = 0
					if hp.getVehicle() == hp.getDefaultVehicle():
						damage = hp.getDefaultVehicle()
					else:
						damage = hp.getVehicleRoot()
					health = damage.getDamage()
					
					
					if health - 1 < 0:
						self.rp_kill(None, [name])
						self.players[str(name)]["timetillhungery"] = int(self.settings["timetillhungery"])
					else:
						damage.setDamage(health-1)
		except:
			print "Unable to run timetohungery"
			ExceptionOutput()

	def onPlayerSpawn(self, playerObject, soldierObject):
		p = playerObject
		if p.rpFirstSpawn == 0:
			p.rpFirstSpawn = 1
		else:
			self.players[str(p.getName().split(" ")[-1])]["bank"] -= 50
		p.getVehicleRoot().setPosition((37.0, 36.0, -163.0))
		name = p.getName().split(" ")[-1]
		self.players[str(name)]["timetillhungery"] = int(self.settings["timetillhungery"])
		
		if self.players[str(name)].has_key("jailed"):
			p.getVehicleRoot().setPosition(self.jailPos[self.players[str(name)]["jailed"]][1])


	def onPlayerConnect(self, playerObject):
		playerObject.rpFirstSpawn = 0
		playerObject.timeToKill = 2
		self.setAdmin(playerObject)
		try:
			self.playerConnectLogin(playerObject)
		except:
			print "Unable to load " + playerObject.getName() + "s profile"
		
	def onPlayerDisconnect(self, p):
		try:
			if self.players[self.getName(p)].has_key("objects"):
				numOfObjs = 0
				for obj in self.players[self.getName(p)]["objects"]:
					numOfObjs += self.players[str(p.getName())]["objects"][str(obj)]
				msg = str(p.getName()) + "(" + str(p.getProfileId()) + ") Number of objects spawned total " + str(numOfObjs)
				self.log("/logs/disconnectInfo.txt", str(msg))
				for object in self.players[str(p.getName())]["objects"]:
					msg = str(object) + " = " + str(self.players[str(p.getName())]["objects"][str(object)])
					self.log("/logs/desconnectInfo.txt", str(msg))
				print "Logged"
			self.rp_quitjob(p, None)
		except:
			ExceptionOutput()
	
	def onPlayerSpawnKit(self, playerObject):
		try:
			if self.jobs[self.players[self.getName(playerObject)]["job"]].has_key("kit"):
				spawnKit = "RP_" + str(self.jobs[self.players[self.getName(playerObject)]["job"]]["kit"])
				print str(spawnKit)
			else:
				spawnKit = "RP_Player"
				print str(spawnKit + "!")
		except:
			spawnKit = "RP_Player"
			print str(spawnKit)
			ExceptionOutput()
		print str(spawnKit)
		return str(spawnKit)
		
		
		
		
		