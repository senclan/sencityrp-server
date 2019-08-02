import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput
class vehicles:

	def vehicleTickSec(self):
		pass
	
	def vehicleTickHalfSec(self):
		self.setVehicleMiles()
	
	def vehicleTickFrame(self):
		try:
			for veh in self.core.objects:
				if veh.templateName in self.core.settings.vehicles:
					veh = veh.root
					if hasattr(veh, "drivelock"):
						if veh.drivelock == 1:
							vehicle = veh.getOccupyingPlayers()
							if len(vehicle) != 0:
								player = self.getPlayerName(str(self.getName(vehicle[0])))[0]
								player.getVehicleRoot().setPosition(veh.lastPos)
								player.getVehicleRoot().setRotation(veh.lastRot)
					else:
						veh.drivelock = 0
						veh.drivelockName = ""
						print "Fixed Car Lock"
		except:
			print "Error locking Vehicles"
			ExceptionOutput()

	def setVehicleMiles(self):
		if len(self.core.objects) == 0: return
		for veh in self.core.objects:
			for vehName in self.core.settings.vehicles:
				if not self.defaultGas.has_key(str(vehName)):
					continue
				if vehName == veh.templateName:
					veh = veh.root
					try:
						vehicle = veh.getOccupyingPlayers()
						if veh.gasoline <= 0 and len(vehicle) != 0:
							if len(vehicle) != 0:
								player = self.getPlayerName(str(vehicle[0].getName().split(" ")[-1]))[0]
								player.getVehicleRoot().setPosition(player.getVehicleRoot().getVehicleRoot().lastPos)
								player.getVehicleRoot().setRotation(player.getVehicleRoot().getVehicleRoot().lastRot)
								try:
									if player.OOG == 0:
										player.sendMsg("Your out of gas")
										player.OOG = 1
								except:
										player.OOG = 0
						elif veh.lastPos != veh.getPosition():
							veh.lastPos = veh.getPosition()
							veh.lastRot = veh.getRotation()
							veh.mileage += 0.01
							veh.gasoline -= self.defaultGas[vehName]["GPF"]
					except:
						veh.lastPos = veh.getPosition()
						veh.lastRot = veh.getRotation()
						veh.mileage = 0.0
						veh.gasoline = self.defaultGas[vehName]["Tank"]
		
	def rp_gas(self, p, params):
		veh = p.getVehicleRoot()
		if hasattr(veh, "gasoline"):
			gas = veh.gasoline
			if gas < 0:
				gas = 0
			p.sendMsg("Gas Status: " + str(round(gas, 1)) + " / " + str(self.defaultGas[str(veh.templateName)]["Tank"]) + " gallons left in tank")
		
	def rp_refill(self, p, params):
		name = p.getName().split(" ")[-1]
		limited = 0
		amount = params[0]
		veh = p.getVehicleRoot()
		vehname = veh.templateName
		pos = self.getPos(p)
		if pos:
			if not str(pos[0]) == "Gas Station Attendant":
				limited = 1
		else:
			limited = 1
		if limited == 1:
			try:
				if self.players[str(name)]["job"] == "Gas Station Attendant":
					if veh.gasoline == 0:
						p.sendMsg("Since you are not at your job, you cannot fill it any higher")
						return
					else:
						amount = (float(self.defaultGas[str(vehname)]["Tank"]) * .20)
				else:
					p.sendMsg("Your not at a gas station")
					return
			except:
				ExceptionOutput()
		if veh:
			if str(amount) == "full":
				amount = self.defaultGas[str(veh.templateName)]["Tank"] - veh.gasoline
			gasoline = float(amount) + veh.gasoline
			if float(amount) + veh.gasoline <= self.defaultGas[str(veh.templateName)]["Tank"]:
				if (float(amount) + veh.gasoline) * self.gasPrice <= self.players[str(p.getName().split(" ")[-1])]["bank"]:
					self.players[str(p.getName().split(" ")[-1])]["bank"] -= float(amount*self.gasPrice)
					veh.gasoline = gasoline
					p.sendMsg("You have been charged " + str(float(amount*self.gasPrice)))
				else:
						p.sendMsg("You don't have enough money")
			else:
				p.sendMsg("You have entered too much to fill, if you want to fill the tank type /refill full")
			p.sendMsg("Vehicle Refuled")
		else:
			p.sendMsg("Unable to find Vehicle")
			
	def rp_job_repair(self, p, params, value):
		try:
			veh = p.getVehicle()
			name = veh.templateName
			if self.vehicleHealth.has_key(str(name)):
				limited = 0
				pos = self.getPos(p)
				if pos:
					if pos[0] != "Mechanic":
						limited = 1
				else:
					limited = 1
				if limited == 1:
					if veh.getDamage() >= float(self.vehicleHealth[str(name)]) * .40:
						p.sendMsg("Since you are not at your job, you canont repair it any higher")
						return
					else:
						amount = float(self.vehicleHealth[str(name)]) * .40
				else:
					amount = float(self.vehicleHealth[str(name)])
				veh.setDamage(float(amount))
				p.sendMsg("Vehicle Repaired")
			else:
				p.sendMsg("Vehicle not found")
		except:
			p.sendMsg("Rut Row, Vehicle not fixed... TELL MIKE!!!!!!!!!!!!!!!!!!")
			ExceptionOutput()
			
			
			
	
	def createVehicle(self, p, vehicle):
		name = p.getName().split(" ")[-1]
		if name in self.carInfo:
			p.sendMsg("Vehicle: " + str(vehicle) + " Cost: " + str(self.objPrices[str(vehicle)]) + " Gas Tank: " + str(self.defaultGas[str(vehicle)]["Tank"]) + " Gal")
			self.carInfo.remove(name)
			return False
		if self.buyCarOwner == str(name):
			if self.buyCarVehicle == str(vehicle):
				pos = self.getPos(p)
				if pos:
					if pos[0] == "SpawnCar":
						if self.objPrices.has_key(str(vehicle)):
							if self.players[str(name)]["bank"] - self.objPrices[str(vehicle)] > 0:
								cost = self.players[str(name)]["bank"] - self.objPrices[str(vehicle)]
								self.players[str(name)]["bank"] -= self.objPrices[str(vehicle)]
								self.payJob("Car Salesman", 50)
								p.sendMsg("Vehicle Bought!")
								return True
							else:
								p.sendMsg("You don't have enough money for this vehicle")
								return False
						else:
							p.sendMsg("Vehicle not found")
							return False
				p.sendMsg("Your not in the Spawn Area")
				return False
			else:
				if self.buyCarVehicle == "":
					p.sendMsg("The Car Salesman hasn't selected the car for you to buy")
				else:
					p.sendMsg("Wrong Vehicle, vehicle bought was " + str(self.buyCarVehicle))
		if self.players[str(name)]["job"] == "Car Salesman" and self.buyCarOwner != "":
			self.buyCarVehicle = str(vehicle)
			p.sendMsg("Vehicle " + str(vehicle) + " was selected for user " + str(self.buyCarOwner))
			return False
		return False
	
	def createdVehicle(self, p, object):
		print "Created: " + str(object)
		name = p.getName().split(" ")[-1]
		if self.buyCarOwner != "":
			self.buyCarOwner = ""
			self.buyCarVehicle = ""
	
	def rp_carinfo(self, p, params):
		name = p.getName().split(" ")[-1]
		if name in self.carInfo:
			return
		else:
			self.carInfo.append(str(name))
			
	def rp_job_sellcar(self, p, params, value):
		pl = self.getPlayerName(params[0])[0]
		name = pl.getName().split(" ")[-1]
		if pl:
			if self.buyCarOwner != "":
				p.sendMsg("You must finish your last car sale, before selling to another. Type /closesale to close the last sale")
				return				
			self.buyCarOwner = str(name)
			self.buyCarVehicle = ""
			p.sendMsg("Your now selling a vehicle to " + str(self.buyCarOwner) + " please click on a vehicle to sell")
		else:
			p.sendMsg("Player not found")

	def rp_job_closesale(self, p, params, value):
		if self.buyCarOwner == "":
			p.sendMsg("You don't have a sale open")
			return
		self.buyCarOwner = ""
		self.buyCarVehicle = ""
		p.sendMsg("Last Sale Closed!")
		
	def rp_lockcar(self, p, params):
		veh = p.getVehicleRoot()
		if veh.templateName in self.core.settings.vehicles:
			veh = veh
			if hasattr(veh, "drivelock"):
				veh.drivelock = 1
				veh.drivelockName = str(p.getName().split(" ")[-1])
				p.sendMsg("Vehicle Locked")
		else:
			p.sendMsg("Vehicle not found")
	
	def rp_unlockcar(self, p, params):
		veh = p.getVehicleRoot()
		if veh.templateName in self.core.settings.vehicles:
			veh = veh
			if veh.drivelockName == str(p.getName().split(" ")[-1]) or self.players[str(p.getName().split(" ")[-1])]["job"] == "Police Officer":
				veh.drivelock = 0
				veh.drivelockName = ""
				p.sendMsg("Vehicle Unlocked")
		else:
			p.sendMsg("Vehicle not found")