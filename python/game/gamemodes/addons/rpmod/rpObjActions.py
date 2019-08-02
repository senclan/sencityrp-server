import host
class objActions:

	def buy(self, p, object):
		name = p.getName().split(" ")[-1]
		object = object.replace("_mp", "")
		if self.objPrices.has_key(str(object)):
			if self.players.has_key(name):
				if self.players[str(name)]["bank"] - self.objPrices[str(object)] > 0:
					self.players[str(name)]["bank"] -= self.objPrices[str(object)]
					return True
				else: return False
		return True
	
	
	
	def createObject(self, p, params):
		if len(p.objects) > self.maxObjects:
			p.sendMsg("You've hit your max objects")
			return False
		if len(params) == 2:
			if params[1] == 1: return True
		if self.players[str(p.getName().split(" ")[-1])].has_key("jailed"):
			return False
		if params or p.lastTemplate:
			if not params:
				object = p.lastTemplate
			else:
				object = params[0]
				if str(object) in self.disabledObjects:
					print str(object) + " is Disabled"
					return False
				else:
					print str(object) + " is not disabled"
			for vehObject in self.core.settings.vehicles:
				if object == vehObject:
					if not self.createVehicle(p, object): return False
			return True
		else:
			p.sendMsg("No Object Selected")
			return False
	
	def createdObject(self, p, object):
		for vehObject in self.core.settings.vehicles:
			if object == vehObject:
				self.createdVehicle(p, object)
	
	
	def grabObject(self, p, o):
		for vehObject in self.core.settings.vehicles:
			if o.templateName == vehObject:
				if p.level < 20:
					return False
		return True