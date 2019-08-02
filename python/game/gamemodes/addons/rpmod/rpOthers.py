import host
class othersCodes:

	def rp_hunger(self, p, params):
		name = p.getName().split(" ")[-1]
		p.sendMsg("Time Untill you need to eat: " + str(self.players[str(name)]["timetillhungery"]) + " seconds")
	
	
	def rp_job_feed(self, p, params, value):
		pl = self.getPlayerName(params[0])[0]
		pos2 = self.getPos(pl)
		if pos2:
			if pos2[0] != "Restaurant Owner" and pos2[1] != self.getPos(p)[1]:
				p.sendMsg("You can only feed people that are at your Restaurant.")
				return
		else:
			p.sendMsg("You can only feed people that are at your Restaurant")
			return
		name = pl.getName().split(" ")[-1]
		pl.getDefaultVehicle().setDamage(int(self.settings["defaulthealth"]))
		self.players[str(name)]["timetillhungery"] = int(self.settings["timetillhungery"])
		pl.sendMsg("Has Eaten")
	
	def rp_eat(self, p, params):
		name = p.getName().split(" ")[-1]
		pos = self.getPos(p)
		if pos:
			if pos[0] == "Gas Station Attendant":
				if self.players[name]["snacks"] == 0:
					self.players[str(name)]["timetillhungery"] += 200
					p.getDefaultVehicle().setDamage(p.getDefaultVehicle().getDamage() + 20.0)
					self.players[name]["snacks"] = 1
					p.sendMsg("Eat a snack")
					return
		if self.jobs["Restaurant Owner"]["numingroup"] != 0: return
		if pos:
			if pos[0] == "Restaurant Owner":
				self.rp_job_feed(p, [name], 1)
				return
		p.sendMsg("You must be at a Restaurant to eat")