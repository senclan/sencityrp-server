#******************************************************************************
# Name: Sandbox Core
# Author: Elton "Elxx" Muuga (http://elxx.net)
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************

import host
import re

import bf2
import bf2.Timer
import bf2.PlayerManager

from sbxObjectManager import sbxObject
from sbxPlayerManager import sbxPlayer
from sbxErrorHandling import ExceptionOutput

import sbxSettings

# Pick whether to send all debug messages to the server chat
GLOBAL_DEBUG = False

class sbxCore:
	def __init__(self):
		self.COREVERSION = "1.0.1"
		self.playerObject = sbxPlayer
		self.initSbx()
		self.registerHandlers()
		self.registerTimers()
		self.loadAddonsFromSettings()

	# initSbx() is called whenever the round is restarted
	def initSbx(self):
		self.settings = sbxSettings.sbxSettingsManager()
		self.settings.loadGameSettings()
		self.settings.loadAddonSettings()
		self.settings.loadUsers()
		self.settings.loadPermissions()
		self.spawnerTemplates = []
		self.objectCount = 0
		self.objects = []
		self.objectsOfTemplate = {}
		self.objectClasses = {}

		self.spawnQueue = {}
		self.identQueue = {}
		self.deleteQueue = {}

		self.players = {}
		self.offlineplayers = {}

		self.multiplayer = False

		self.initGame()

	def initGame(self):
		pass
	
	def die(self):
		self.unregisterTimers()
		self.unregisterHandlers()

	def registerTimers(self):
		self.timerFrame = bf2.Timer(self.ctickFrame, 0, 1)
		self.timerFrame.setRecurring(0.00001)
		self.timerHalfSec = bf2.Timer(self.ctickHalfSec, 0, 1)
		self.timerHalfSec.setRecurring(0.5)
		self.timerOneSec = bf2.Timer(self.ctickOneSec, 0, 1)
		self.timerOneSec.setRecurring(1.0)
	
	def unregisterTimers(self):
		self.timerFrame.destroy()
		self.timerFrame = None
		self.timerHalfSec.destroy()
		self.timerHalfSec = None
		self.timerOneSec.destroy()
		self.timerOneSec = None

	def ctickFrame(self, data):
		try: self.onObjectQueueTimer()
		except: pass
		try: self.tickFrame()
		except: pass #no exceptionoutput for this one because that would be brutal
		self.addonCallback("tickFrame")

	def tickFrame(self):
		pass

	def ctickHalfSec(self, data):
		try: self.tickHalfSec()
		except: ExceptionOutput()
		self.addonCallback("tickHalfSec")

	def tickHalfSec(self):
		pass

	def ctickOneSec(self, data):
		try: self.tickOneSec()
		except: ExceptionOutput()
		self.addonCallback("tickOneSec")

	def tickOneSec(self):
		pass

	def onObjectQueueTimer(self):

		#
		# Identification queue
		#
		for oName in self.identQueue:
			try:
				if self.identQueue[oName]:
					oInfo = self.identQueue[oName][0]
					oPos, oRot = oInfo[:2]
					objects = list(bf2.objectManager.getObjectsOfTemplate(oName))
					objects.reverse()
					o = None
					for x in objects:
						if not self.objectClasses.has_key(x):
							if x.isValid():
								if x.getPosition() != (0.0,0.0,0.0):
									o = x
									break
					if o:
						self.refactorIDs(oName)
						o_obj = sbxObject(o)
						info = self.identQueue[oName].pop(0)
						self.objects.append(o_obj)
						if not self.objectsOfTemplate.has_key(oName): self.objectsOfTemplate[oName] = []
						self.objectsOfTemplate[oName].append(o_obj)
						self.objectClasses[o] = o_obj
						self.dbg(o.templateName + " : " + str(o.oId))
						o.setPosition(oPos)
						o.setRotation(oRot)
						if o_obj.isValid():
							self.onObjectCreated(o_obj)
						else:
							self.dbg("Object invalid on " + str(oName))
					else:
						self.dbg("Object ident failed on " + str(oName))
						self.identQueue[oName].pop(0)
			except: ExceptionOutput()

		#
		# Spawn queue
		#
		for oName in self.spawnQueue:
			try:
				if self.spawnQueue[oName] and not self.identQueue[oName]:
					oInfo = self.spawnQueue[oName].pop(0)
					oPos, oRot, team = oInfo
					self.createObject(oName, oPos, oRot, team)
					self.identQueue[oName].append([oPos, oRot, team])
			except: ExceptionOutput()

		#
		# Delete queue
		#
		for oName in self.deleteQueue:
			try:
				if self.deleteQueue[oName]:
					self.deleteObject(self.deleteQueue[oName].pop(0))
			except: ExceptionOutput()

		#
		# Detect deleted dynamic objects
		#
		for template in self.settings.dynamic_objects:
			try:
				if self.objectsOfTemplate.has_key(template):
					for o in self.objectsOfTemplate[template]:
						if not o.isValid():
							self.deleteObject(o)
			except: ExceptionOutput()

	def onObjectCreated(self, o):
		print "Callback for a " + str(o.templateName)

	def refactorIDs(self, oName):
		tmpList = list(bf2.objectManager.getObjectsOfTemplate(oName))
		tmpList.reverse()
		objs = host.rcon_invoke("object.listObjectsofTemplate " + str(oName))
		objs = objs.split()
		reverseId = 0
		for o in tmpList:
			if not hasattr(o,"oId"):
				o.oId = objs[(reverseId * -10)-7]
			reverseId += 1

	def getObjID(self, template, index):
		tmp = host.rcon_invoke("object.listObjectsofTemplate " + str(template))
		list = tmp.split("\n")
		list.pop()
		item = list[index].split(" ")
		return item[3]
	
	def loadAddonsFromSettings(self):
		self.addons = []
		for id in self.settings.addons:
			self.loadAddon(id, True)
	
	def loadAddon(self, id, automatic=False):
		for a in self.addons:
			if a.id == id:
				self.sendMsg("Addon is already loaded: " + id)
				return
		try:
			a = __import__("game.gamemodes.addons." + id)
			a = getattr(a.gamemodes.addons, id)
			reload(a)
			if automatic and hasattr(a, "GAMEMODES"):
				if bf2.serverSettings.getGameMode().lower() not in a.GAMEMODES:
					print "Skipped loading " + id + " addon due to GAMEMODES constraint"
					return
			if automatic and hasattr(a, "LEVELS"):
				if bf2.serverSettings.getMapName().lower() not in a.LEVELS:
					print "Skipped loading " + id + " addon due to LEVELS constraint"
					return
			if hasattr(a, "PERMISSIONS"):
				for cat,items in a.PERMISSIONS.items():
					if not self.settings.permissions.has_key(cat): continue
					for cmd,perm in items.items():
						if not self.settings.permissions[cat].has_key(cmd):
							self.settings.permissions[cat][cmd] = perm
			a.obj = a.Addon(self)
			a.id = id
			self.addons.append(a)
			print "Loaded addon: " + id
			if not automatic:
				self.sendMsg("Loaded addon: " + id)
		except ImportError:
			self.dbg("Unable to load addon: " + id)
			if not automatic:
				self.sendMsg("Could not find " + id + ".py")
			ExceptionOutput()
		except SyntaxError:
			self.dbg("Unable to load addon: " + id)
			if not automatic:
				self.sendMsg("Could not load " + id + ".py due to a syntax error")
			ExceptionOutput()
		except:
			self.dbg("Unable to load addon: " + id)
			if not automatic:
				self.sendMsg("Unable to load addon: " + id)
			ExceptionOutput()
	
	def reloadAddon(self, id):
		for a in self.addons:
			if a.id == id:
				a.obj = None
				try: reload(a)
				except:
					ExceptionOutput()
					self.sendMsg("Unable to reload addon " + id + " due to a syntax error")
					return
				a.obj = a.Addon(self)
				a.id = id
				self.sendMsg("Reloaded addon: " + id)
	
	def unloadAddon(self, id):
		for a in list(self.addons):
			if a.id == id:
				self.addons.remove(a)
				del a
				self.sendMsg("Unloaded addon: " + id)
				return
		self.sendMsg("Could not find a loaded addon with the id '" + id + "'")
	
	def chat_loadaddon(self, p, params):
		for id in params:
			if id: self.loadAddon(id)
	
	def chat_unloadaddon(self, p, params):
		for id in params:
			if id: self.unloadAddon(id)
	
	def chat_reloadaddon(self, p, params):
		for id in params:
			if id: self.reloadAddon(id)
	
	def chat_reloadalladdons(self, p, params):
		for a in list(self.addons):
			self.reloadAddon(a.id)
	
	def chat_unloadalladdons(self, p, params):
		for a in list(self.addons):
			self.unloadAddon(a.id)
	
	def chat_listaddons(self, p, params):
		addon_list = []
		for a in self.addons:
			if not hasattr(a, "HIDDEN"):
				addon_list.append(a.id)
		p.sendMsg("Loaded addons: " + ", ".join(addon_list))
		p.sendMsg("Type @ainfo [addonname] to learn more about an addon")
	
	def chat_ainfo(self, p, params):
		id = params[0]
		for a in self.addons:
			if a.id == id:
				break
			else:
				a = None
		if not a:
			p.sendMsg("Addon not found.")
			return
		if hasattr(a, "HIDDEN"): return
		if len(params) == 1:
			info = ""
			if hasattr(a, "NAME"):
				info += a.NAME + " "
			if hasattr(a, "VERSION"):
				info += str(a.VERSION) + " "
			if hasattr(a, "AUTHOR"):
				info += " - Created by " + a.AUTHOR
			if hasattr(a, "WEBSITE"):
				info += " (" + a.WEBSITE + ")"
			if info:
				p.sendMsg(info)
			else:
				p.sendMsg("No information provided about this addon.")
			if hasattr(a, "DESCRIPTION"):
				p.sendMsg(a.DESCRIPTION)
			if hasattr(a, "COMMANDS"):
				commandlist = []
				for c in a.COMMANDS:
					if self.settings.checkPermission(p, "chat", c):
						commandlist.append(c)
				if commandlist:
					p.sendMsg("Available commands: " + ", ".join(commandlist))
					p.sendMsg("Type @ainfo " + id + " [command] to learn more about a command.")
		elif len(params) == 2:
			command = params[1]
			if not hasattr(a, "COMMANDS"): return
			if a.COMMANDS.has_key(command):
				if len(a.COMMANDS[command]) == 2:
					p.sendMsg("@" + command + " " + a.COMMANDS[command][0] + " - " + a.COMMANDS[command][1])
				else:
					p.sendMsg("@" + command + " " + a.COMMANDS[command][0])
			else:
				p.sendMsg("This command does not exist.")

	def addonCallback(self, func, *args):
		r = False
		for a in self.addons:
			if hasattr(a, "obj"):
				if hasattr(a.obj, func):
					try:
						method = getattr(a.obj, func)
						result = method(*args)
						if result:
							r = True
					except:
						print "addonCallback failed:", a.id, func
						ExceptionOutput()
		return r

	##################
	# Event Handlers #
	##################

	def registerHandlers(self):
		# Set up event handlers
		host.gpmevents.registerHandler('GameStatusChanged',self.coreGameStatusChanged)
		host.gpmevents.registerHandler('PlayerDeath', self.corePlayerDeath)
		host.gpmevents.registerHandler('PlayerKilled', self.corePlayerKilled)
		host.gpmevents.registerHandler('PlayerSpawn', self.corePlayerSpawn)
		host.gpmevents.registerHandler('PickupKit', self.corePickupKit)
		host.gpmevents.registerHandler('DropKit', self.coreDropKit)
		host.gpmevents.registerHandler('EnterVehicle', self.coreEnterVehicle)
		host.gpmevents.registerHandler('ExitVehicle', self.coreExitVehicle)
		host.gpmevents.registerHandler('VehicleDestroyed', self.coreVehicleDestroyed)
		host.gpmevents.registerHandler('PlayerConnect', self.corePlayerConnect)
		host.gpmevents.registerHandler('PlayerDisconnect', self.corePlayerDisconnect)
		host.gpmevents.registerHandler('ChatMessage', self.coreChatMessage)
		host.gpmevents.registerHandler('RemoteCommand', self.coreRemoteCommand)
		host.gpmevents.registerHandler('TimeLimitReached', self.coreTimeLimitReached)

	def unregisterHandlers(self):
		host.gpmevents.unregisterHandler('GameStatusChanged')
		host.gpmevents.unregisterHandler('PlayerDeath')
		host.gpmevents.unregisterHandler('PlayerKilled')
		host.gpmevents.unregisterHandler('PlayerSpawn')
		host.gpmevents.unregisterHandler('PickupKit')
		host.gpmevents.unregisterHandler('DropKit')
		host.gpmevents.unregisterHandler('EnterVehicle')
		host.gpmevents.unregisterHandler('ExitVehicle')
		host.gpmevents.unregisterHandler('VehicleDestroyed')
		host.gpmevents.unregisterHandler('PlayerConnect')
		host.gpmevents.unregisterHandler('PlayerDisconnect')
		host.gpmevents.unregisterHandler('ChatMessage')
		host.gpmevents.unregisterHandler('RemoteCommand')
		host.gpmevents.unregisterHandler('TimeLimitReached')

	def coreGameStatusChanged(self, status):
		print "onGameStatusChanged"
		try:
			if status == bf2.GameStatus.Playing:
				self.initSbx()
				self.players = {}
				for p in bf2.playerManager.getPlayers():
					self.corePlayerConnect(p)
			if self.addonCallback("onGameStatusChanged",status): return
			self.onGameStatusChanged(status)
		except:
			ExceptionOutput()

	def onGameStatusChanged(self, status):
		pass

	def coreTimeLimitReached(self, value):
		if self.addonCallback("onTimeLimitReached",value): return
		try: self.onTimeLimitReached(value)
		except: ExceptionOutput()

	def onTimeLimitReached(self, value):
		pass

	def corePlayerDeath(self, playerObject, soldierObject):
		if self.addonCallback("onPlayerDeath", self.getPlayerByObject(playerObject), soldierObject): return
		try: self.onPlayerDeath(self.getPlayerByObject(playerObject), soldierObject)
		except: ExceptionOutput()

	def onPlayerDeath(self, playerObject, soldierObject):
		pass

	def corePlayerKilled(self, victimPlayerObject, attackerPlayerObject, weaponObject, assists, victimSoldierObject):
		if self.addonCallback("onPlayerKilled", self.getPlayerByObject(victimPlayerObject), self.getPlayerByObject(attackerPlayerObject), weaponObject, assists, victimSoldierObject): return
		try: self.onPlayerKilled(self.getPlayerByObject(victimPlayerObject), self.getPlayerByObject(attackerPlayerObject), weaponObject, assists, victimSoldierObject)
		except: ExceptionOutput()

	def onPlayerKilled(self, victimPlayerObject, attackerPlayerObject, weaponObject, assists, victimSoldierObject):
		pass

	def corePlayerSpawn(self, playerObject, soldierObject):
		p = self.registerPlayer(playerObject)
		if p.isRemote():
			self.multiplayer = True
		else:
			p.level = 21 # automatically make local players admin
		if self.addonCallback("onPlayerSpawn", self.getPlayerByObject(playerObject), soldierObject): return
		try: self.onPlayerSpawn(self.getPlayerByObject(playerObject), soldierObject)
		except: ExceptionOutput()

	def onPlayerSpawn(self, playerObject, soldierObject):
		pass

	def corePickupKit(self, playerObject, kitObject):
		if self.addonCallback("onPickupKit", self.getPlayerByObject(playerObject), kitObject): return
		try: self.onPickupKit(self.getPlayerByObject(playerObject), kitObject)
		except: ExceptionOutput()

	def onPickupKit(self, playerObject, kitObject):
		pass

	def coreDropKit(self, playerObject, kitObject):
		if self.addonCallback("onDropKit", self.getPlayerByObject(playerObject), kitObject): return
		try: self.onDropKit(self.getPlayerByObject(playerObject), kitObject)
		except: ExceptionOutput()

	def onDropKit(self, playerObject, kitObject):
		pass

	def coreEnterVehicle(self, playerObject, vehicleObject, freeSoldier):
		if self.addonCallback("onEnterVehicle", self.getPlayerByObject(playerObject), vehicleObject, freeSoldier): return
		try: self.onEnterVehicle(self.getPlayerByObject(playerObject), vehicleObject, freeSoldier)
		except: ExceptionOutput()

	def onEnterVehicle(self, playerObject, vehicleObject, freeSoldier):
		pass

	def coreExitVehicle(self, playerObject, vehicleObject):
		if self.addonCallback("onExitVehicle", self.getPlayerByObject(playerObject), vehicleObject): return
		try: self.onExitVehicle(self.getPlayerByObject(playerObject), vehicleObject)
		except: ExceptionOutput()

	def onExitVehicle(self, playerObject, vehicleObject):
		pass

	def coreVehicleDestroyed(self, vehicleObject, attackerObject):
		#self.deleteObject(vehicleObject)
		if self.addonCallback("onVehicleDestroyed", vehicleObject, attackerObject): return
		try: self.onVehicleDestroyed(vehicleObject, attackerObject)
		except: ExceptionOutput()

	def onVehicleDestroyed(self, vehicleObject, attackerObject):
		pass

	def corePlayerConnect(self, playerObject):
		print "Connected"
		try: p = self.registerPlayer(playerObject)
		except: ExceptionOutput()
		p.connectTime = host.timer_getWallTime()
		if self.addonCallback("onPlayerConnect", p): return
		try: self.onPlayerConnect(p)
		except: ExceptionOutput()

	def onPlayerConnect(self, playerObject):
		pass

	def corePlayerDisconnect(self, playerObject):
		if self.addonCallback("onPlayerDisconnect", self.getPlayerByObject(playerObject)): return
		#for o in playerObject.objects:
		#	if o.templateName in self.settings.vehicles or o.templateName in self.settings.dynamic_objects:
		#		self.cleanDeleteObject(o)
		try: self.onPlayerDisconnect(self.getPlayerByObject(playerObject))
		except: pass
		try: self.unregisterPlayer(self.getPlayerByObject(playerObject))
		except: ExceptionOutput()

	def onPlayerDisconnect(self, playerObject):
		pass

	def coreChatMessage(self, playerId, text, channel, flags):
		if playerId == -1: #fix for local servers
			playerId = 255
		command, parameter = self.decodeChatMessage(text)
		if command:
			p = self.getPlayerByIndex(playerId)
			if not self.settings.checkPermission(p, "chat", command):
				print "Insufficient permissions - " + str(p.getName()) + ", chat_" + str(command)
				return
			if parameter: parameters = parameter.split(" ")
			else: parameters = []
			self.addonCallback("chat_"+command, p, parameters)
			if hasattr(self, ('chat_' + command)):
				method = getattr(self, ('chat_' + command))
				try: method(p, parameters)
				except: ExceptionOutput()
			else:
				print "Unimplemented chat method - " + mname
			self.addonCallback("chat_post_"+command, p, parameters)
		try: self.onChatMessage(playerId, text, channel, flags)
		except: ExceptionOutput()

	def onChatMessage(self, playerId, text, channel, flags):
		pass

	def coreRemoteCommand(self, playerId, cmd):
		if playerId == -1: #fix for local servers
			playerId = 255
		p = self.getPlayerByIndex(playerId)
		print "RCommand"
		print playerId,cmd
		cmdArray = cmd.split(" ")
		command = cmdArray.pop(0)
		parameters = cmdArray
		if not self.settings.checkPermission(p, "rcon", command):
			print "Insufficient permissions - " + str(p.getName()) + ", rcon_" + str(command)
			return
		self.addonCallback("rcon_"+command, p, parameters)
		if hasattr(self, ('rcon_' + command)):
			method = getattr(self, ('rcon_' + command))
			try: method(p, parameters)
			except: ExceptionOutput()
		else:
			print "Unimplemented rcon method - " + mname
		self.addonCallback("rcon_post_"+command, p, parameters)
		try: self.onRemoteCommand(playerId, cmd)
		except: ExceptionOutput()

	def onRemoteCommand(self, playerId, cmd):
		pass

	##################################
	# Our core functions for Sandbox #
	##################################

	def queueObject(self, oName, oPos, oRot = (0.0,0.0,0.0), team = 2):
		if not self.spawnQueue.has_key(oName):
			self.spawnQueue[oName] = []
			self.identQueue[oName] = []
		#self.createObject(oName, oPos, oRot, team)
		self.spawnQueue[oName].append([oPos, oRot, team])
		#self.identQueue[oName].append([oPos, oRot, team])

	def createObject(self, oName, oPos, oRot = (0.0,0.0,0.0), team = 2):
		if not oName in self.spawnerTemplates:
			self.createSpawnerTemplate(oName)
		host.rcon_invoke("Object.create sbx_" + oName)
		# object is initially spawned underground to prevent conflicts that cause some vehicles to fail
		host.rcon_invoke("Object.absolutePosition " + str(oPos[0]) + "/" + str(-1000.0) + "/" + str(oPos[2]))
		host.rcon_invoke("Object.rotation " + str(oRot[0]) + "/" + str(oRot[1]) + "/" + str(oRot[2]))
		host.rcon_invoke("Object.team " + str(team))
		if oName == "usaas_stinger_spw" or oName == "aircontroltower": host.rcon_invoke("ObjectTemplate.teamOnVehicle 1")
		self.objectCount += 1

	def createSpawnerTemplate(self, oName):
		host.rcon_invoke("ObjectTemplate.create ObjectSpawner sbx_" + oName)
		host.rcon_invoke("ObjectTemplate.activeSafe ObjectSpawner sbx_" + oName)
		host.rcon_invoke("ObjectTemplate.hasMobilePhysics 0")
		host.rcon_invoke("ObjectTemplate.setObjectTemplate 1 " + oName)
		host.rcon_invoke("ObjectTemplate.setObjectTemplate 2 " + oName)
		host.rcon_invoke("ObjectTemplate.minSpawnDelay 700000")
		host.rcon_invoke("ObjectTemplate.maxSpawnDelay 900000")
		self.spawnerTemplates.append(oName)

	def decodeChatMessage(self, text):
		text = text.replace( "HUD_TEXT_CHAT_TEAM", "" )
		text = text.replace( "HUD_TEXT_CHAT_SQUAD", "" )
		text = text.replace( "HUD_CHAT_DEADPREFIX", "" )
		text = text.replace( "*\xA71DEAD\xA70*", "" )
		command = None
		parameter = None
		if text[0:1] == "@":
			pattern = re.compile(r'@(\w*) ?(.*)')
			matches = pattern.findall(text)
			command = matches[0][0]
			if matches[0][1] != "":
				parameter = matches[0][1]
			else:
				parameter = None
		return command, parameter

	def queueDeleteObject(self, o):
		if not self.deleteQueue.has_key(o.templateName):
			self.deleteQueue[o.templateName] = []
		self.deleteQueue[o.templateName].append(o)

	def deleteObject(self, o):
		try:
			if self.addonCallback("onDeleteObject", o): return
			print "Deleting " + str(o.templateName)
			if hasattr(o,"owner"):
				if hasattr(o.owner,"objects"):
					if o.owner.objects.count(o):
						o.owner.objects.remove(o)
			if hasattr(o,"oId"):
				oName = o.templateName
				if o in self.objects:
					self.objects.remove(o)
				if o in self.objectsOfTemplate[oName]:
					self.objectsOfTemplate[oName].remove(o)
				if self.objectClasses.has_key(o.root):
					del self.objectClasses[o.root]
				else: print "fail"
				host.rcon_invoke("Object.active id" + str(o.oId))
				host.rcon_invoke("Object.delete")
				self.objectCount = len(self.objects)
				print "Deleted!"
		except: ExceptionOutput()

	def endRoundAfter(self,secs):
		host.rcon_invoke("sv.timeLimit " + str(int(host.timer_getWallTime() - self.roundStartTime) + secs))

	################################################
	# Player management: because BF2 sucks at this #
	################################################

	def registerPlayer(self, playerObject):
		if not self.players.has_key(playerObject.getName()):
			if self.offlineplayers.has_key(playerObject.getName()):
				newPlayerObject = self.offlineplayers[playerObject.getName()]
				del self.offlineplayers[playerObject.getName()]
				newPlayerObject.reinit(playerObject)
				self.dbg("Recycled registration...")
			else:
				newPlayerObject = self.playerObject(playerObject)
			self.players[playerObject.getName()] = newPlayerObject
			self.dbg("Registered " + str(newPlayerObject.getName()) + " [" + str(newPlayerObject.getIndex()) + "]")
			self.addonCallback("onRegisterPlayer", newPlayerObject)
		else:
			newPlayerObject = self.getPlayerByObject(playerObject)
		return newPlayerObject

	def unregisterPlayer(self, playerObject):
		name = playerObject.getName()
		playerObject.bf2PlayerObject = None
		playerObject.disconnectTime = host.timer_getWallTime()
		self.offlineplayers[name] = playerObject
		del self.players[name]
		self.dbg("Player disconnected - " + name)

	def getPlayerByIndex(self, index):
		pObj = bf2.PlayerManager.Player(index)
		return self.getPlayerByName(pObj.getName())

	def getPlayerByObject(self, pObj):
		return self.getPlayerByName(pObj.getName())

	def getPlayerByName(self, name):
		if self.players.has_key(name):
			return self.players[name]
		else:
			self.dbg("getPlayerByName failed for " + str(name))
			return false

	# returns a list of all player objects
	def getAllPlayers(self):
		ret = []
		for (i,x) in self.players.items():
			if x.isValid():
				ret.append(x)
		return ret
	
	# just an alias
	def getPlayers(self):
		return self.getAllPlayers()

	def getAlivePlayers(self):
		ret = []
		for (i,x) in self.players.items():
			if x.isValid():
				if x.isAlive() and not x.isManDown():
					ret.append(x)
		return ret
	
	def getOfflinePlayers(self):
		ret = []
		for (i,x) in self.offlineplayers.items():
			ret.append(x)
		return ret

	#
	# Utility functions
	#

	def sendMsg(self, text):
		host.rcon_invoke("game.sayAll \"" + str(text) + "\"")

	def dbg(self, text):
		if GLOBAL_DEBUG:
			self.sendMsg(text)
		print text

