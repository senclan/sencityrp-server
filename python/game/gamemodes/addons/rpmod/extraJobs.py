import host
class extraJobs:
	
	def extraInit(self):
		self.taxiJobs = {}
	def extraTickSec(self):
		try:
			for tJob in self.taxiJobs:
				self.taxiJobs[str(tJob)] += 1
		except:
			print "Error adding time"
			ExceptionOutput()
		for delivP in self.core.getAllPlayers():
			if self.players[self.getName(delivP)].has_key("delivery"):
				self.players[self.getName(delivP)]["delivery"]["timer"] += 1

	#Taxi Driver
	def rp_job_startmeter(self, p, params, value):
		self.taxiJobs[str(p.getProfileId())] = 0
		p.sendMsg("Meter Started")
	
	def rp_job_stopmeter(self, p, params, value):
		p.sendMsg("Meter Stopped")
		time = self.taxiJobs[str(p.getProfileId())]
		del self.taxiJobs[str(p.getProfileId())]
		p.sendMsg("Time spent: " + str(time) + " Seconds at .50 per second is " + str(time*.5) + " Dollars")
		
		
	
	#Drugs
	
	def rp_drugs(self, p, params):
		cmd = params[0]
		params.remove(params[0])
		if str(cmd) == "pickup":
			if self.getPos(p):
				if str(self.getPos(p)[0]) == "getdrugs":
					if self.drugJobs.has_key(str(self.getPos(p)[0])):
						if self.drugJobs[str(self.getPos(p)[0])]["1"]["amount"] - 1 >= 0:
							if self.players[str(self.getName(p))].has_key("drugs"):
								if self.players[str(self.getName(p))]["drugs"]["status"] == 1:
									p.sendMsg("you already have drugs")
									return
								if self.players[str(self.getName(p))]["drugs"]["amount"] < 4:
									if self.players[str(self.getName(p))]["bank"] - 100 >= 0:										
										self.drugJobs[str(self.getPos(p)[0])]["1"]["amount"] -= 1
										self.players[str(self.getName(p))]["bank"] -= 100
										self.players[str(self.getName(p))]["drugs"]["amount"] += 1
										self.players[str(self.getName(p))]["drugs"]["status"] = 0
										p.sendMsg("You now have the drugs")
									else:
										p.sendMsg("You dont have enough money")
								else:
									p.sendMsg("You already have too  many")
							else:
								if self.players[str(self.getName(p))]["bank"] - 100 >= 0:		
									self.drugJobs[str(self.getPos(p)[0])]["1"]["amount"] -= 1
									self.players[str(self.getName(p))]["bank"] -= 100
									self.players[str(self.getName(p))]["drugs"] = {"amount":1, "Status":0}
									self.players[str(self.getName(p))]["drugs"]["status"] = 0
									p.sendMsg("You now have the drugs")
						else:
							p.sendMsg("There are no more drugs, please wait until more drugs have been made")
					else:
						self.setupdrugs(p, None)
						params.insert(0, cmd)
						self.rp_drugs(p, params)
				else:
					p.sendMsg("not in getdrugs area")
			else:
				p.sendMsg("Not in an area")
		try:
			if str(cmd) == "filter":
				if self.getPos(p):
					if self.getPos(p)[0] == "drugrun1" and self.getPos(p)[1] == "1" or self.getPos(p)[0] == "drugrun2" and self.getPos(p)[1] == "1":
						if self.players[self.getName(p)].has_key("drugs"):
							if self.players[self.getName(p)]["drugs"]["status"] == 0:
								self.players[self.getName(p)]["drugs"]["status"] = 1
								p.sendMsg("drugs have been filtered, please take them to the final destination")
							elif self.players[self.getName(p)]["drugs"]["status"] == 1:
								p.sendMsg("drugs already have been filtered")
						else:
							p.sendMsg("No drugs found")
					else:
						p.sendMsg("Not at filter place")
				else:
					p.sendMsg("not in an area")
		except:
			p.sendMsg("rut Row")
			ExceptionOutput()
		
		if str(cmd) == "dropoff":
			if self.getPos(p):
				if self.getPos(p)[0] == "drugrun1" and self.getPos(p)[1] == "2" or self.getPos(p)[0] == "drugrun2" and self.getPos(p)[1] == "2":
					if self.players[self.getName(p)].has_key("drugs"):
						if self.players[self.getName(p)]["drugs"]["status"] == 1:
							self.players[self.getName(p)]["drugs"]["status"] = -1
							amount = self.players[self.getName(p)]["drugs"]["amount"] * 100
							amount += self.players[self.getName(p)]["drugs"]["amount"] * 100
							self.players[self.getName(p)]["bank"] += amount
							self.players[self.getName(p)]["drugs"]["amount"] = 0
							p.sendMsg("Drugs have been dropped off! You have been paid ")
		if str(cmd) == "info":
			p.sendMsg("Amount: " + str(self.players[self.getName(p)]["drugs"]["amount"]) + " Status: " + str(self.players[self.getName(p)]["drugs"]["status"]))
	
	
	def setupdrugs(self, p, params):
		p.sendMsg("Attempting")
		self.drugJobs["getdrugs"] = {"1":{"amount":10}}
		p.sendMsg("Setup")
	