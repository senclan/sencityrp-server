import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput
class Settings:
	def rpinit(self):
		self.rpdisabled = 0
		self.commands = {
			"delivery":"[start/drop/help] allowes you to do a delivery job to random places.",
			"fish":"[start/stop/done/status] allows you to fish in the deep hole outside of SeN City",
			"startmeter":"If you have the taxi job, you can start and stop your meter",
			"stopmeter":"If you have the taxi job, you can start and stop your meter, this will display many things, including how much",
			"drugs":"[pickup/dropoff/filter/info] pickup, dropoff, and info are self explanitory, filter filters the drugs so you can drop them off",
			"bank":"Displays your bank information",
			"jobs":"Displays Jobs",
			"selectjob":"allows you to select a job in /jobs",
			"quitjob":"Allows you to quit your current job",
			"door":"[create/open/close/auto/notauto] [doorname] BETA this is still in the works",
			"help":"[command] If you dont know the command, just dont put anything after it and it will display them",
			"status":"Displays the current status",
			"injob":"[job name] Gets who is in a specific job",
			"getjob":"[player] Displays the job a player has",
			"jobhelp":"[job name] Without a job name it displays all jobs help command, with a job name displays that jobs commands",
			"buy":"allows you to buy a house or apartment",
			"sell":"Allows you to sell a house or apartment",
			"chat":"[player name] [Message] This is an rcon command, hit ~ or End to open rcon, then you can send a personal message to them",
			"arrest":"[player] Allows an officer to arrest a player",
			"unarrest":"[player] allows you to free a player",
			"amjailed":"Tells you whether or not you are jailed and for how long",
			"jailinfo":"Displays different jail info",
			"hunger":"Tells you how much longer you have before you NEED to eat",
			"feed":"[player] allows a restaurant job to feed a player",
			"eat":"allows you to either grab a snack from the gas station, or eat at a restaurant when no one works there",
			"gas":"Displays how much gas is left in your vehicle",
			"refill":"[amount/full] will either allow a gas station attendant to refill your vehicle, or a player refill their own vehicle if no one has the job",
			"repair":"Will repair the vehicle for you, unless there is a mechanic, then they will do it",
			"carinfo":"Once you type this, open your hud and click on a vehicle, if text pops up it will display its info",
			"sellcar":"[player] Allows a car salesman to sell a vehicle, after typing this, click on the vehicle to sell",
			"closesale":"Closes your current car sale incase player doesn't want to finish the sale",
			"lockcar":"Locks your vehicle from moving, like a car alarm, so people cant steel your vehicle",
			"unlockcar":"Unlocks your car"
		}
		self.comPermissions = {
			"servername":20,
			"loadsettings":20,
			"kill":20,
			"kick":20,
			"spawn":20,
			"makemoney":20,
			"quitjobp":20,
			"loadadmin":20,
			"saveadmin":20,
			"change":20,
			"mtp":20,
			"addpos":20,
			"getpos":20,
			
		}
		self.objPrices = {}
		self.players = {"TESTPLAYER":{"bank":500}}
		self.jobs = {}
		self.timers = {}
		self.saveAcc = 0
		self.status = "Home"
		self.statusTimer = 0
		self.doors = {}
		self.autodoors = {}
		self.vehicles = {}
		self.defaultGas = {}
		self.vehicleHealth = {}
		self.gasPrice = 3
		self.maxObjects = 30
		self.disabledObjects = []
		self.nextJail = 0
		self.loadedSettings = 0
		self.loadedserver = 0
		self.pos = {}
		self.buyCarOwner = ""
		self.buyCarVehicle = ""
		self.carInfo = []
		self.admins = {}
		self.extraInit()
		self.autoMessagesInit()
		self.rpModSettingsDir = host.sgl_getModDirectory() + "/python/game/gamemodes/addons/rpmod/settings/"
		
		
		#jail section
		self.jailPos = {
					"Jail 1":[0,(138.0, 37.0, 7.0)],
					"Jail 2":[0,(143.0, 37.0, 7.0)],
					"Jail 3":[0,(148.0, 38.0, 7.0)],
					"Jail 4":[0,(153.0, 38.0, 7.0)],
					"Jail 5":[0,(158.0, 37.0, 7.0)],
					"Jail 6":[0,(163.0, 38.0, 7.0)]
		}
		print "Loaded Default Settings"
		

	def loadSettings(self):
		try:
			svSettings = open(self.rpModSettingsDir + "settings.txt",'r')
			for setting in svSettings:
				setting = setting.replace("\n", "")
				setting = setting.replace("\r", "")
				if setting[0] == ";": continue
				if len(setting) == 0: continue
				name = setting.split("=")[0]
				value = setting.split("=")[1]
				self.settings[name] = value
			print "Server Settings Loaded"
			svSettings.close()
		except:
			print "Error loading Server Settings"
			ExceptionOutput()
		
		try:
			jobslist = open(self.rpModSettingsDir + "jobslist.txt",'r')
			
			jobName = ""
			jobVals = {}
			for job in jobslist:
				job = job.replace("\n", "")
				job = job.replace("\r", "")
				if job[0] == ";": continue
				if len(job) == 0: continue
				items = job.split(" | ")
				jobName = items[0]
				items.remove(items[0])
				vals = {}
				for item in items:
					name = item.split("=")[0]
					value = item.split("=")[1]
					jobVals[name] = value
				self.jobs[jobName] = {}
				self.jobs[jobName] = jobVals
				self.jobs[jobName]["numingroup"] = 0
				jobName = ""
				jobVals = {}
			print "Jobs List Loaded"
			jobslist.close()
		except:
			print "Error loading Jobs List"
			ExceptionOutput()
		
		try:
			self.core.settings.hpConstructionHealth = int(self.settings["hpConstructionHealth"])
			
			
			try:
				if self.settings.has_key("servername"):
					self.rconcmd(str("sv.serverName "+str(self.settings["servername"])))
					print "servername loaded"
			except: self.core.sendMsg("Unable to set setting servername")
			try:
				 if self.settings.has_key("playersneededtostart"):
					self.rconcmd(str("sv.numPlayersNeededToStart "+str(self.settings["playersneededtostart"])))
					print "playersneededtostart loaded"
			except:  self.core.sendMsg("Unable to set setting playersneededtostart")
			try: 
				if self.settings.has_key("spawntime"):
					self.rconcmd(str("sv.spawnTime "+str(self.settings["spawntime"])))
					print "spawntime loaded"
			except:  self.core.sendMsg("Unable to set setting spawntime")
			try:
				 if self.settings.has_key("mandowntime"):
					self.rconcmd(str("sv.manDownTime "+str(self.settings["mandowntime"])))
					print "mandowntime loaded"
			except:  self.core.sendMsg("Unable to set setting mandowntime")
			try:
				 if self.settings.has_key("timelimit"):
					self.rconcmd(str("sv.timeLimit "+str(self.settings["timelimit"])))
					print "timelimit loaded"
			except:  self.core.sendMsg("Unable to set setting timelimit")
		except:
			print "Unable to run load settings"
			ExceptionOutput()
		try:
			objectPrices = open(self.rpModSettingsDir + "objectprices.txt",'r')
			for setting in objectPrices:
				setting = setting.replace("\n", "")
				setting = setting.replace("\r", "")
				if setting[0] == ";": continue
				if len(setting) == 0: continue
				name = setting.split("=")[0]
				value = int(setting.split("=")[1])
				self.objPrices[name] = value
			print "Object Prices Loaded"
			objectPrices.close()
		except:
			print "Error loading Object Prices"

		try:
			vehiclegas = open(self.rpModSettingsDir + "vehiclegas.txt",'r')
			for setting in vehiclegas:
				setting = setting.replace("\n", "")
				setting = setting.replace("\r", "")
				if setting[0] == ";": continue
				if len(setting) == 0: continue
				name = setting.split("=")[0]
				value = setting.split("=")[1]
				tank = float(value.split(";")[0])
				mpg = float(value.split(";")[1])
				self.defaultGas[name] = {"Tank":float(tank), "GPF":float(mpg)}
				
			print "Vehicle Gas Limited Loaded"
			vehiclegas.close()
		except:
			print "Unable to load Vehicle Gas Limits"
		
		try:
			vehicledamage = open(self.rpModSettingsDir + "vehicledamage.txt",'r')
			for setting in vehicledamage:
				setting = setting.replace("\n", "")
				setting = setting.replace("\r", "")
				if setting[0] == ";": continue
				if len(setting) == 0: continue
				name = setting.split("=")[0]
				value = float(setting.split("=")[1])
				self.vehicleHealth[name] = value*6.0
			print "Default Damage Loaded"
			vehicledamage.close()
		except:
			print "Error loading Default Damage"
		
		try:
			gunz = open(self.rpModSettingsDir + "guns.txt",'r')
			for setting in gunz:
				setting = setting.replace("\n", "")
				setting = setting.replace("\r", "")
				if setting[0] == ";": continue
				if len(setting) == 0: continue
				host.rcon_invoke("objecttemplate.active "  + str(setting))
				host.rcon_invoke("objecttemplate.projectiletemplate Car_horn2_Projectile")
			print "Guns List Loaded"
			gunz.close()
		except:
			print "Error loading Guns"
		try:
			obj = open(self.rpModSettingsDir + "disabled.txt",'r')
			for setting in obj:
				setting = setting.replace("\n", "")
				setting = setting.replace("\r", "")
				if setting[0] == ";": continue
				if len(setting) == 0: continue
				self.disabledObjects.append(str(setting))
			print "Disabled List Loaded"
			obj.close()
		except:
			print "Error loading Disabled List"
		
		try:
			position = open(self.rpModSettingsDir + "positions.txt",'r')
			for line in position:
				line = line.replace("\n", "")
				line = line.replace("\r", "")
				if line[0] == ";": continue
				value = line.split("=")[-1]
				value = value.replace("(", "")
				value = value.replace(")", "")
				value = value.split(";")
				radius = int(value[1])
				height = int(value[2])
				value = value[0].split(", ")
				value[0] = float(value[0])
				value[1] = float(value[1])
				value[2] = float(value[2])
				name = line.split("=")[-0].split(";")[-0]
				type = line.split("=")[-0].split(";")[-1]
				if str(type) == "house" or str(type) == "apt":
					cost = 0
					if str(type) == "house":
						cost = 1200
					if str(type) == "apt":
						cost = 100
					if self.pos.has_key(str(type)):
						self.pos[str(type)][str(name)] = {"value":value, "cost":cost, "owner":"", "radius":radius, "height":height}
					else:
						self.pos[str(type)] = {}
						self.pos[str(type)][str(name)] = {"value":value, "cost":cost, "owner":"", "radius":radius, "height":height}
				else:
					if self.pos.has_key(str(type)):
						self.pos[str(type)][str(name)] = {"value":value, "radius":radius, "height":height}
					else:
						self.pos[str(type)] = {}
						self.pos[str(type)][str(name)] = {"value":value, "radius":radius, "height":height}

			position.close()
			print "Positions Loaded"
		except:
			print "Error loading Positions"
		
		try:
			self.deliveries = []
			for delivery in self.pos:
				if delivery.split("_")[0] == "delivery":
					self.deliveries.append(str(delivery.split("_")[1]))
					print "Setup Deliveries"
		except:
			print "Error loading Positions"
		self.loadAdmins()
	