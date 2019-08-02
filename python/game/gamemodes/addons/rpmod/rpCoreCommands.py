import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput
class coreCmd:
			
	def chat_rp(self, p, params):
		if self.rpdisabled:
			p.sendMsg("RP Disabled, An admin needs to enable it with @enablerp")
			return
		cmd = params[0]
		if self.players[str(p.getName().split(" ")[-1])].has_key("jailed") and str(cmd) != "amjailed":
			print str(p.getName()) + " - is in jail"
			pos = self.getPos(p)
			if pos:
				if pos[0] == "jailcell":
					if p.level < 18: return
				
		params.remove(params[0])
		if params == []:
			params = None
		contin = 0
		error = 0
		name = p.getName().split(" ")[-1]
		
		if hasattr(self, ('rp_job_' + str(cmd))):
			if self.jobs[str(self.players[str(name)]["job"])].has_key(str(cmd)):
				if self.comPermissions.has_key(cmd):
						if p.level >= self.comPermissions[cmd]:
							contin = 1
						else:
							p.sendMsg("Command Disallowed")
							contin = 0
				else:
					contin = 1
			else:
				contin = 0
				error = 1
				p.sendMsg("Job not Allowed")
		if contin == 1:
			execRpJobCommand = getattr(self, ('rp_job_' + str(cmd)))
			try:
				con = 0
				pl = self.getPos(p)
				if pl:
					if pl[0] == self.players[name]["job"]:
						con = 1
				if self.jobs[self.players[name]["job"]].has_key("freeroam"):
						con = 1
				
				if self.players[name]["job"] == "Mechanic":
					con = 1
				if con == 1:
					value = self.jobs[str(self.players[str(name)]["job"])][str(cmd)]
					execRpJobCommand(p, params, value)
					return
				p.sendMsg("You can only run that command when your at your job")
			except:
				#p.sendMsg("Error")
				ExceptionOutput()
				error = 1
		
		
		if contin == 0 and error == 0:
			if hasattr(self, ('rp_' + str(cmd))):
				if self.comPermissions.has_key(cmd):
					if p.level >= self.comPermissions[cmd]:
						contin = 1
					else:
						p.sendMsg("Command Disallowed")
						contin = 0
				else:
					contin = 1
			else:
				p.sendMsg("RP Command not Found. type /help")
				error = 1
			if contin == 1:
				execRpCommand = getattr(self, ('rp_' + str(cmd)))
				try:
					execRpCommand(p, params)
				except:
					#p.sendMsg("Error excecuting code")
					ExceptionOutput()
					error = 1
	
	
			

	def rp_kick(self, p, params):
		name = params[0]
		params.remove(params[0])
		self.rconcmd(str("admin.kickPlayer " + player.index))
		
	def rp_servername(self, p, params):
		name = " ".join(params)
		try:
			host.rcon_invoke("sv.serverName \"" + str(name) + "\"")
			self.core.sendMsg("Server Name: " + str(name))
		except:
			p.sendMsg("Unable to change server name...")
	
	
	def rp_bank(self, p, params):
		name = p.getName().split(" ")[-1]
		self.core.sendMsg(str(p.getName()) + "'s Bank Info: Ammount: " + str(self.players[str(name)]["bank"]) + " | Salary: " + str(self.jobs[self.players[str(name)]["job"]]["salary"]) + " | Job: " + str(self.players[str(name)]["job"]) + ".")
	
	def rp_kill(self, player, params):
		killp = params[0]
		p = self.getPlayerName(str(killp))[0]
		try:
			if p.getVehicle() == p.getDefaultVehicle():
				p.getDefaultVehicle().setDamage(0.0)
			else:
				p.getVehicleRoot().setDamage(0.1)
		except:
			p.sendMsg("Unable to kill player")
	
	def rp_jobs(self, p, params):
		if not params:
			joblist = []
			for jobs in self.jobs:
				joblist.append(jobs)
			list = self.printList(joblist)
			for item in list:
				self.core.sendMsg("Jobs: " + str(item))
			p.sendMsg("Type /jobs [job name] to see description")
			p.sendMsg("Type /selectjob [job name] to select that job")
		else:
			cmd = " ".join(params)
			if self.jobs.has_key(str(cmd)):
				if self.jobs[str(cmd)].has_key("description"):
					self.core.sendMsg("/jobs "  + str(cmd) + " - Description: " + str(self.jobs[str(cmd)]["description"]))
				if self.jobs[str(cmd)].has_key("salary"):
					self.core.sendMsg("/jobs "  + str(cmd) + " - Salary: " + str(self.jobs[str(cmd)]["salary"]))
				if self.jobs[str(cmd)].has_key("maxingroup"):
					self.core.sendMsg("/jobs "  + str(cmd) + " - Max Users: " + str(self.jobs[str(cmd)]["maxingroup"]))
			else:
				p.sendMsg("Command not Found")
		
	def rp_selectjob(self, p, params):
		if not params:
			self.rp_jobs(p, None)
		else:
			name = p.getName().split(" ")[-1]
			cmd = " ".join(params)
			if self.players[str(name)]["job"] != "Ped":
				p.sendMsg("You already have a job, type /quitjob to quit your current job")
				return
			if self.jobs.has_key(str(cmd)):
				if str(cmd) == "Police Officer":
					if p.level < 18:
						print str(p.getName()) + "Police Officer Disabled"
						return
				if int(self.jobs[str(cmd)]["numingroup"]) >= int(self.jobs[str(cmd)]["maxingroup"]):
					p.sendMsg("Max Users Reached")
				else:
					self.players[str(name)]["job"] = str(cmd)
					self.jobs[str(cmd)]["numingroup"] = int(self.jobs[str(cmd)]["numingroup"]) + 1
					p.sendMsg("is now a " + str(self.players[str(name)]["job"]))
			else:
				p.sendMsg("Job not found")
	def rp_quitjob(self, p, params):
		name = p.getName().split(" ")[-1]
		if self.players[str(name)]["job"] == "Ped":
			p.sendMsg("You don't have a job")
			return
		cJob = self.players[str(name)]["job"]
		self.jobs[str(cJob)]["numingroup"] = int(self.jobs[str(cJob)]["numingroup"]) - 1
		self.players[str(name)]["job"] = "Ped"
		p.sendMsg("You have left your job")
	
	def rp_quitjobp(self, p, params):
		pl = self.getPlayerName(str(params[0]))[0]
		self.rp_quitjob(pl, params)
	
	def rp_pay(self, p, params):
		name = p.getName().split(" ")[-1]
		to = self.getPlayerName(str(params[0]))[0]
		if not to:
			p.sendMsg("No Player Found")
			return
		toName = to.getName().split(" ")[-1]
		amount = params[1]
		if int(amount) < 1: return
		if int(amount) > 100000: return
		if (self.players[str(name)]["bank"] - int(amount)) > 0:
			self.players[toName]["bank"] += int(amount)
			self.players[str(name)]["bank"] -= int(amount)
			self.core.sendMsg(str(to.getName()) + " has received money from " + str(p.getName()))

		else:
			p.sendMsg("You don't have that much money")
	
	def rp_makemoney(self, p, params):
		try:
			pl = params[0]
			amount = int(params[1])
			player = self.getPlayerName(pl)[0]
			plName = player.getName().split(" ")[-1]
			self.players[plName]["bank"] += int(amount)
		except:
			print "ERROR MAKING MONEY"
			ExceptionOutput()
	
	
	def rp_door(self, p, params):
		action = params[0]
		plName = p.getName().split(" ")[-1]
		if action == "create":
			name = params[1]
			try:
				if p.grabObject:
					o = p.grabObject[0]
					if hasattr(o, "owner"):
						if p.getName() == o.owner.getName():
							if not self.doors.has_key(plName):
								self.doors[plName] = {}
							self.doors[plName][str(name)] = o
							p.sendMsg("Door: " + str(name) + " created!")
						else:
							p.sendMsg("You'r not the owner of this object")
				else:
					p.sendMsg("No Object Grabbed")
			except:
				p.sendMsg("Unable to create door")
		
		if action == "open":
			name = params[1]
			if self.doors.has_key(plName):
				if self.doors[plName].has_key(str(name)):
					pos = self.doors[plName][str(name)].getPosition()
					self.doors[plName][str(name)].setPosition((pos[0], pos[1]-1000, pos[2]))
				else:
					p.sendMsg("Door not found")
			else:
				p.sendMsg("No doors have been created")
		
		if action == "close":
			name = params[1]
			if self.doors.has_key(plName):
				if self.doors[plName].has_key(str(name)):
					pos = self.doors[plName][str(name)].getPosition()
					self.doors[plName][str(name)].setPosition((pos[0], pos[1]+1000, pos[2]))
				else:
					p.sendMsg("Door not found")
			else:
				p.sendMsg("No doors have been created")
		
		if action == "auto":
			name = params[1]
			if self.doors.has_key(plName):
				if self.doors[plName].has_key(str(name)):
					if not self.autodoors.has_key(plName):
						self.autodoors[plName] = {}
					if self.autodoors[plName].has_key(name):
						bf2.triggerManager.destroy(self.autodoors[plName][name][1])
					o = self.doors[plName][str(name)]
					p.sendMsg(str(o.root))
					door = bf2.triggerManager.createRadiusTrigger(o.root, self.doorauto, '<<PCO>>', 1.0, (p,[name, self.doors[plName][str(name)]]))
					self.autodoors[plName][name] = []
					self.autodoors[plName][name].append(0)
					self.autodoors[plName][name].append(door)
					p.sendMsg("Door has been made auto")
				
				else:
					p.sendMsg("Door not found")
			else:
				p.sendMsg("No doors have been created")
			
			
		if action == "notauto":
			name = params[1]
			if self.doors.has_key(plName):
				if self.doors[plName].has_key(str(name)):
					if self.autodoors[plName].has_key(name):
						bf2.triggerManager.destroy(self.autodoors[plName][name][1])
						del self.autodoors[plName][name]
						p.sendMsg("Door now does not open automaticaly")
					else:
						p.sendMsg("Door not found in auto list")
				else:
					p.sendMsg("Door has not been created")
			else:
				p.sendMsg("No doors have been created")
		if action == "viewauto":
			p.sendMsg(str(self.autodoors[plName]))
	
	def doorauto(self, p, params):
		p.sendMsg("door being triggered" + str(params))
		plname = p.getName().split(" ")[-1]
		name = params[0]
		doorTrig = params[1]
		if self.autodoors[plname][name][0] == 0:
			self.rp_door(p, ['open', name])
			self.autodoors[plname][name][0] = 1
		elif self.autodoors[plname][name][0] == 1:
			self.rp_door(p, ['close', name])
			self.autodoors[plname][name][0] = 0
		else:
			p.sendMsg("Auto Door not found")
			
	def rp_loadsettings(self, p, params):
		self.rpinit()
		self.loadSettings()
		for pl in self.core.getAllPlayers():
			self.playerConnectLogin(pl)
		self.loadedSettings = 1
	def rp_help(self, p, params):
		if not params:
			list = self.printList(self.commands)
			for item in list:
				self.core.sendMsg("Commands: " + str(item))
		else:
			cmd = params[0]
			if self.commands.has_key(str(cmd)):
				self.core.sendMsg("/" + str(cmd) + " - " + str(self.commands[str(cmd)]))
			else:
				p.sendMsg("Command not Found")
	
	def rp_status(self, p, params):
		self.core.sendMsg("Everyone is currently at " + str(self.status) + " with " + str(self.statusTimer/60) + " minutes left")
	
	def rp_injob(self, p, params):
		try:
			job = " ".join(params)
			injob = []
			if self.jobs.has_key(str(job)):
				for pl in self.core.getAllPlayers():
					name = pl.getName().split(" ")[-1]
					if self.players[str(name)]["job"] == str(job):
						injob.append(str(name))
				injob = self.printList(injob)
				for PlayerJob in injob:
					self.core.sendMsg("Job - " + str(PlayerJob))
		except:
			ExceptionOutput()
	
	def rp_getjob(self, p, params):
		player = params[0]
		pl = self.getPlayerName(player)[0]
		name = pl.getName().split(" ")[-1]
		pl.sendMsg("Has a job of " + str(self.players[str(name)]["job"]))
				
	
	def rp_jobhelp(self, p, params):
		if not params:
			list = self.printList(self.commands)
			for item in list:
				self.core.sendMsg("Commands: " + str(item))
		else:
			job = params[0]
			list = []
			if self.jobs.has_key(job):
				for code in self.jobs[job]:
					if self.commands.has_key(str(code)):
						list.append(code)
			for item in self.printList(list):
				self.core.sendMsg(str(job) + " - " + str(item))
			else:
				p.sendmsg("Job not found")

	
	def rp_buy(self, p, params):
		pos = self.getPos(p)
		name = p.getName().split(" ")[-1]
		if pos:
			if str(pos[0]) != "house" and str(pos[0]) != "apt":
				p.sendMsg("This place is not buyable")
				return
			if self.pos[str(pos[0])][str(pos[1])]["owner"] == "":
				if int(self.players[str(name)]["bank"]) - int(self.pos[str(pos[0])][str(pos[1])]["cost"]) > 0:
					self.pos[str(pos[0])][str(pos[1])]["owner"] = str(name)
					self.players[str(name)]["bank"] -= int(self.pos[str(pos[0])][str(pos[1])]["cost"])
					p.sendMsg("You have just bought " + str(pos[0]) + ":" + str(pos[1]))
				else:
					p.sendMsg("You don't have enough money for this " + str(pos[0]))
			else:
				p.sendMsg("This is already owned by " + str(self.pos[str(pos[0])][str(pos[1])]["owner"]))
		else:
			p.sendMsg("Your not in a buyable area")
	
	def rp_sell(self, p, params):
		pos = self.getPos(p)
		name = p.getName().split(" ")[-1]
		if pos:
			if str(pos[0]) != "house" and str(pos[0]) != "apt":
				p.sendMsg("This place is not buyable")
				return
			if self.pos[str(pos[0])][str(pos[1])]["owner"] == str(name):
				self.pos[str(pos[0])][str(pos[1])]["owner"] = ""
				amount = float(int(self.pos[str(pos[0])][str(pos[1])]["cost"]) * 0.75)
				self.players[str(name)]["bank"] += amount
				p.sendMsg("You just sold your house for " + str(amount))
			else:
				p.sendMsg("This is not your place")
		else:
			p.sendMsg("Your not in an area to be sold")
	
	def checkpos(self, p, params):
		pPos = p.getDefaultVehicle().getPosition()
		targetPos = self.pos[str(params[0])][str(params[1])]["value"]
		targetPos = (targetPos[0], targetPos[1], targetPos[2])
		radius = self.pos[str(params[0])][str(params[1])]["radius"]
		distance = self.pos[str(params[0])][str(params[1])]["height"]
		deltapos = (pPos[0]-targetPos[0],pPos[2]-targetPos[2])
		distsquared = deltapos[0]*deltapos[0]+deltapos[1]*deltapos[1]
		radiussquared = radius * radius
		if distsquared <= radiussquared and targetPos[1] - distance < pPos[1] and targetPos[1] + distance > pPos[1]:
			return params
		else:
			return None
	
	def getPos(self, p):
		for type in self.pos:
			for name in self.pos[str(type)]:
				place = self.checkpos(p, [str(type), name])
				if place:
					return place
		return ["None", -1]
		
	def rcon_chat(self, p, params):
		pid = p.index
		if len(params) < 2:
			host.rcon_feedback(pid, "You must \"type rcon chat playername message\"")
			return
		pl = self.getPlayerName(str(params[0]))[0]
		params.remove(params[0])
		if pl:
			plid = pl.index
			host.rcon_feedback(plid, "============ MESSAGE RECIEVED ============")
			host.rcon_feedback(plid, " ")
			message = " ".join(params)
			host.rcon_feedback(plid, "Sent by: " + str(p.getName()))
			host.rcon_feedback(plid, "Body: ")
			host.rcon_feedback(plid, "     " + str(message))
			host.rcon_feedback(plid, " ")
			host.rcon_feedback(plid, "==========================================")
			host.rcon_feedback(pid, "Mesage Sent")
			pl.sendMsg("Message Received, open console with the Tildy(Left to your !) or your End Button")