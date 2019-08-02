#******************************************************************************
# Name: Sandbox Build Gamemode
# Author: Elton "Elxx" Muuga (http://elxx.net)
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************

import host
import re

import bf2
import bf2.Timer
import bf2.PlayerManager

from sbxCore import sbxCore
from sbxObjectManager import sbxObject
from sbxPlayerManager import sbxPlayer
from sbxErrorHandling import ExceptionOutput
from bf2.stats.constants import *
import sbxMath
import math

from socket import *
import md5
import sbxSettings 


class sbxGame_build(sbxCore):

	def initGame(self):
		self.GPMVERSION = "1.0.1"
		self.objCache = {}
		self.obj_freeze = {}
		self.groups = []
		self.animations = []
		self.loadedSettings = 0

	def tickFrame(self):
		self.onGrabTimer()
		self.onFreezeTimer()
		for x in self.animations:
			x.tickFrame()

	def tickOneSec(self):
		self.onUpdateScoreboardTimer()
		self.checkDisconnectedPlayers()
		self.runMessageCache()

	def onGrabTimer(self):
		if self.addonCallback("onGrabTimer"): return
		for p in self.getAlivePlayers():
			if p.grabObject:
				o = p.grabObject[0]
				if not o.isValid(): continue
				offset = p.grabObject[2]
				pPos = p.getTracerLocation(p.grabObject[1])
				if p.grabSnap == 1:
					if p.gridSnap:
						newPos = (
									sbxMath.roundToNearest(pPos[0] - offset[0],p.gridSnap), 
									sbxMath.roundToNearest(pPos[1] - offset[1],p.gridSnap), 
									sbxMath.roundToNearest(pPos[2] - offset[2],p.gridSnap)
								)
					else:
						newPos = ((pPos[0] - offset[0]),(pPos[1] - offset[1]),(pPos[2] - offset[2]))
				else:
					if p.gridSnap:
						newPos = (
									sbxMath.roundToNearest(pPos[0],p.gridSnap), 
									sbxMath.roundToNearest(pPos[1],p.gridSnap), 
									sbxMath.roundToNearest(pPos[2],p.gridSnap)
								)
					else:
						newPos = pPos
				if p.grabGroup:
					p.grabGroup.setPosition(newPos)
				else:
					o.setPosition(newPos)
					o.setRotation(p.grabObject[4])
		for p in self.getAllPlayers():
			if p.spawnDelay > 0:
				p.spawnDelay -= 1

	def onUpdateScoreboardTimer(self):
		for p in self.getAllPlayers():
			try:
				if p.saveDelay:
					p.saveDelay -= 1
				if p.groupDupeDelay:
					p.groupDupeDelay -= 1
				p.score.score = len(p.objects)
				p.score.skillScore = len(p.objects)
				p.score.rplScore = len(p.groups)
				p.score.deaths = p.saveDelay
			except: ExceptionOutput()
	
	def checkDisconnectedPlayers(self):
		if self.settings.disconnectTime and len(self.offlineplayers):
			for p in self.getOfflinePlayers():
				if p.objects and p.disconnectTime and (host.timer_getWallTime() - p.disconnectTime) >= self.settings.disconnectTime:
					self.addonCallback("onDellOfflinePlayer", p)
					for obj in list(p.objects):
						self.cleanDeleteObject(obj)
					self.sendMsg(p.getName() + " - Player was offline, objects cleared")
	
	def runMessageCache(self):
		for p in self.getAlivePlayers():
			for c in p.msgCache:
				p.sendMsg(p.msgCache[c])
			p.msgCache = {}

	def onFreezeTimer(self):
		#### Refreeze all frozen objects
		invalidFreezes = []
		for o in self.obj_freeze:
			if self.obj_freeze[o]:
				if (o.isValid()) and (type(self.obj_freeze[o][0]) == type(tuple())):
					if o.getPosition() != self.obj_freeze[o][0]:
						o.setPosition(self.obj_freeze[o][0])
					if o.getRotation() != self.obj_freeze[o][1]:
						o.setRotation(self.obj_freeze[o][1])
					try:
						if hasattr(o,"setDamage"):
							if o.getDamage() > 0:
								o.setDamage(10000)
					except:
						pass
				else:
					invalidFreezes.append(o)
		for f in invalidFreezes:
			if self.obj_freeze.has_key(f):
				self.obj_freeze.pop(f)

	def cacheObject(self, oName, oPos, oRot, p, ignoreAutograb=False):
		if not self.objCache.has_key(oName): self.objCache[oName] = []
		self.objCache[oName].append([oPos,oRot,p,ignoreAutograb])
		
	
	def checkObjectCount(self, add=0):
		if self.multiplayer and self.objectCount + add > self.settings.mpObjectLimit: return False
		else: return True

	def onObjectCreated(self, o):
		try:
			if self.objCache[o.templateName]:
				cachedRequest = self.objCache[o.templateName].pop(0)
				o.owner = cachedRequest[2]
				p = o.owner
				p.objects.append(o)
				if o.templateName in self.settings.vehicles:
					o.isDynamic = True
				if p.autoLock:
					o.isLocked = True
				if cachedRequest[3]:
					return
				if o.templateName not in self.settings.vehicles:
					if p.selectedGroup:
						p.selectedGroup.addObject(o)
						if p.selectedGroup.load:
							p.selectedGroup.load -= 1
							if p.selectedGroup.load <= 0:
								self.rcon_btnEndGroup(p, [])
							return # to ensure that we don't grab each object that gets loaded
					if p.selectedAnimation:
						if not p.selectedAnimation.keyframes:
							p.selectedAnimation.addTarget(o)
							p.sendMsg("Object added to animation")
					if p.autoGrab:
						oPos = cachedRequest[0]
						oRot = cachedRequest[1]
						p.grabObject = [o,p.tracerDistance,(0.0,0.0,0.0),oPos,oRot]
						p.sendHudEvent(57)
			else: self.dbg("Object not in expected cache - " + str(o.templateName))
		except: ExceptionOutput()

	def rcon_btnCreate(self, p, params):
		if self.multiplayer and p.spawnDelay > 0: return
		if p.grabGroup: return
		if not self.checkObjectCount(1):
			p.sendMsg("OBJLIMITREACHED")
			return
		if not self.addonCallback("createObject", p, params): return
		if params:
			oName = params[0]
			if ((oName not in self.settings.sbxObjects) and (oName not in self.settings.vehicles) and (oName not in self.settings.dynamic_objects)):
				return
			if not self.settings.checkPermission(p, "objects", oName):
				return
			if self.multiplayer and oName in self.settings.sbxObjects:
				oName += "_mp"
			oRot = p.getDefaultVehicle().getRotation()
			p.lastRotation = oRot
		else:
			if p.lastTemplate:
				oName = p.lastTemplate
				oRot = p.lastRotation
			else:
				return
		p.clearGrabbed()
		oPos = p.getTracerLocation()
		self.cacheObject(oName,oPos,oRot,p)
		self.queueObject(oName,oPos,oRot,p.getTeam())
		p.lastTemplate = oName
		if not self.addonCallback("createdObject", p, oName): return
		if (self.settings.dynamic_objects.count(oName) or self.settings.vehicles.count(oName)):
			p.spawnDelay = self.settings.vehiclespawnDelay
		else:
			p.spawnDelay = self.settings.spawnDelay

	def rcon_btnSpawn(self, p, params): # Alias for btnCreate
		self.rcon_btnCreate(p, params)

	def rcon_btnGrab(self, p, params):
		pPos = p.getTracerLocation()
		closest = [0,p.tracerDistance + 10.0]
		if p.grabMode == 1:
			objects = p.objects
		else:
			objects = self.objects
		for o in objects:
			if o.isValid():
				if o.isLocked:
					if o.owner != p:
						if not self.settings.checkPermission(p, "misc", "grablocked"): continue
				oDist = sbxMath.getVectorDistance(pPos,o.getPosition())
				if oDist < closest[1]:
					closest = [o,oDist]
		if closest[0]:
			try:
				o, oDist = closest
				if not self.addonCallback("grabObject", p, o): return
				oPos = o.getPosition()
				if self.obj_freeze.has_key(o):
					frozen = True
					self.obj_freeze.pop(o)
				else: frozen = False
				if o.animation:
					o.animation.stop()
				pPos = p.getTracerLocation()
				grabOffset = ((pPos[0] - oPos[0]),(pPos[1] - oPos[1]),(pPos[2] - oPos[2]))
				p.grabObject = [o,p.tracerDistance,grabOffset,oPos,o.getRotation()]
				o.isGrabbed = True
				p.lastAction.append(["grab",o,oPos,o.getRotation(),frozen])
				p.sendHudEvent(57) # close to mine
			except: ExceptionOutput()

	def rcon_btnUndo(self, p, cmdVar):
		if p.lastAction:
			par = p.lastAction.pop()
			p.lastAction = []
			if par[0] == "grab": # [object, original position, original rotation, original frozen]
				try:
					self.dbg("Grab undoing")
					o = par[1]
					if p.grabObject[0] == o:
						p.grabObject = []
					o.setPosition(par[2])
					o.setRotation(par[3])
					if par[4]:
						self.obj_freeze[o] = [par[2],par[3]]
						self.dbg("Refrozen")
					o.isGrabbed = False
					p.sendHudEvent(58)
				except:
					ExceptionOutput()
			if par[0] == "grabgroup": # [group, position, rotation]
				self.dbg("Group grab undoing")
				p.grabObject = None
				p.grabGroup = None
				p.sendHudEvent(58)
				try:
					par[1].setPosition(par[2])
					par[1].setRotation(par[3])
				except:
					ExceptionOutput()
			if par[0] == "drop": # [p.grabObject]
				try:
					self.dbg("Drop undoing")
					p.grabObject = par[1]
					p.grabObject[0].isGrabbed = True
					p.sendHudEvent(57)
				except:
					ExceptionOutput()
			self.dbg("Undone.")

	def rcon_btnDrop(self, p, params):
		if p.grabObject: p.lastAction.append(["drop",p.grabObject])
		p.grabObject[0].isGrabbed = False
		p.grabObject = []
		p.grabGroup = None
		p.sendHudEvent(58)

	def rcon_btnPush(self, p, params):
		if p.grabObject:
			p.grabObject[1] += 0.5

	def rcon_btnPull(self, p, params):
		if p.grabObject:
			p.grabObject[1] -= 0.5

	def rcon_btnRotate(self, p, params):
		if p.grabObject:
			if params[1] == "1": rFactor = p.rotationFactor
			else: rFactor = -p.rotationFactor
			o = p.grabObject[0]
			oRot = o.getRotation()
			if params[0] == "A":
				newRot = (round(oRot[0] + rFactor), oRot[1], oRot[2])
			if params[0] == "P":
				newRot = (oRot[0], round(oRot[1] + rFactor), oRot[2])
			if params[0] == "R":
				newRot = (oRot[0], oRot[1], round(oRot[2] + rFactor))
			newRot = sbxMath.normalizeRotation(newRot)
			if p.grabGroup:
				if params[0] == "A": p.grabGroup.setRotation(newRot)
			else:
				p.grabObject[4] = newRot
				o.setRotation(newRot)
				p.lastRotation = newRot

	def rcon_btnResetRotation(self, p, params):
		if p.grabGroup: return
		elif p.grabObject:
			obj = p.grabObject[0]
			if obj and obj.isValid():
				p.grabObject[4] = p.savedRotation
				obj.setRotation(p.savedRotation)
				p.lastRotation = p.savedRotation

	def rcon_btnSaveRotation(self, p, params):
		if p.grabObject:
			obj = p.grabObject[0]
			if obj and obj.isValid():
				p.savedRotation = obj.getRotation()
				p.sendMsg("ROTATION_SAVED")
		else:
			p.savedRotation = (0.0,0.0,0.0)
			p.sendMsg("ROTATION_CLEARED")

	def rcon_btnLock(self, p, params):
		if p.grabObject:
			obj = p.grabObject[0]
			if obj and obj.isValid():
				obj.isLocked = True
		if p.grabGroup:
			g = p.grabGroup
			for obj in list(g.objects):
				obj.isLocked = True

	def rcon_btnUnLock(self, p, params):
		if p.grabObject:
			obj = p.grabObject[0]
			if obj and obj.isValid():
				obj.isLocked = False
		if p.grabGroup:
			g = p.grabGroup
			for obj in list(g.objects):
				obj.isLocked = False

	def rcon_btnDelete(self, p, params):
		if p.grabGroup:
			g = p.grabGroup
			p.grabGroup = []
			p.grabObject = []
			p.sendHudEvent(58)
			if g.animation:
				g.animation.removeTarget(g)
			for obj in list(g.objects):
				self.cleanDeleteObject(obj)
			try: self.groups.pop(g)
			except: pass
		elif p.grabObject:
			if p.selectedAnimation:
				target = p.getGrabbed()
				if target: p.selectedAnimation.removeTarget(target)
			obj = p.grabObject[0]
			p.grabObject = []
			p.sendHudEvent(58)
			self.cleanDeleteObject(obj)

	def cleanDeleteObject(self, obj):
		for g in self.groups:
			if obj in g.objects:
				g.removeObject(obj)
				if not len(g.objects):
					try: self.groups.remove(g)
					except: pass
		for p in self.getAllPlayers():
			if p.selectedGroup:
				if obj in p.selectedGroup.objects:
					p.selectedGroup.removeObject(obj)
		if obj.animation:
			obj.animation.removeTarget(obj)
		if obj.templateName in self.settings.dynamic_objects:
			# move explosive objects away so the explosion doesn't affect anything else
			try: obj.setPosition((0.0,5000.0,0.0))
			except: pass
		self.queueDeleteObject(obj)

	def rcon_btnAutoLockToggle(self, p, params):
		if p.autoLock:
			p.autoLock = False
			p.sendMsg("AUTOLOCK_DISABLED")
		else:
			p.autoLock = True
			p.sendMsg("AUTOLOCK_ENABLED")

	def rcon_btnAutoGrabToggle(self, p, params):
		if p.autoGrab:
			p.autoGrab = False
			p.sendMsg("AUTOGRAB_DISABLED")
		else:
			p.autoGrab = True
			p.sendMsg("AUTOGRAB_ENABLED")

	def rcon_btnGrabMode(self, p, params):
		if p.grabMode == 1:
			p.grabMode = 2
			p.sendMsg("GRABMODE_ALL")
		elif p.grabMode == 2:
			p.grabMode = 1
			p.sendMsg("GRABMODE_MINE")
			
	def rcon_btnGrabSnap(self, p, params):
		if p.grabSnap == 1:
			p.grabSnap = 2
			p.sendMsg("GRABSNAP_TRACER")
		elif p.grabSnap == 2:
			p.grabSnap = 1
			p.sendMsg("GRABSNAP_RELATIVE")
	def rcon_btnRotSnap(self, p, params): # Steps through rotation snaps 1,5,10,15,etc.
		if params[0] == "inc":
			if p.rotationFactor >= 5:
				p.rotationFactor += 5
			elif p.rotationFactor == 1:
				p.rotationFactor = 5
		else:
			if p.rotationFactor > 5:
				p.rotationFactor -= 5
			elif p.rotationFactor == 5:
				p.rotationFactor = 1
		p.sendMsg("Rotation factor set to " + str(p.rotationFactor) + "deg",1)

	def rcon_btnSnap(self, p, cmdVar):
		if cmdVar[0] == "inc":
			p.gridSnap += 0.25
		else:
			p.gridSnap -= 0.25
		if p.gridSnap < 0.25: p.gridSnap = 0.0
		if p.gridSnap > 0:
			p.sendMsg("Grid snap set to " + str(p.gridSnap) + "m",2)
		else:
			p.sendMsg("Grid snap disabled",2)

	def rcon_btnFreeze(self, p, cmdVar):
		if p.grabObject:
			if p.grabObject[0].isValid():
				self.obj_freeze[p.grabObject[0]] = [p.grabObject[0].getPosition(),p.grabObject[0].getRotation()]
				p.lastAction.append([2,p.grabObject[0],p.grabObject[1],1])
				p.grabObject = []

	def rcon_btnAdGrab(self, p, params):
		if params[0] == "1":
			self.settings.permissions["rcon"]["btnGrab"] = 0
			self.sendMsg("Object grab has been enabled for all players.")
		else:
			self.settings.permissions["rcon"]["btnGrab"] = 21
			self.sendMsg("Object grab has been disabled for non-admin players.")

	def rcon_btnAdLock(self, p, params):
		if params[0] == "1":
			self.settings.permissions["rcon"]["btnLock"] = 0
			self.sendMsg("Object locking has been enabled for all players.")
		else:
			self.settings.permissions["rcon"]["btnLock"] = 21
			self.sendMsg("Object locking has been disabled for non-admin players.")

	def rcon_btnAdCreate(self, p, params):
		if params[0] == "1":
			self.settings.permissions["rcon"]["btnCreate"] = 0
			self.settings.permissions["rcon"]["btnSpawn"] = 0
			self.sendMsg("Object creation has been enabled for all players.")
		else:
			self.settings.permissions["rcon"]["btnCreate"] = 21
			self.settings.permissions["rcon"]["btnSpawn"] = 21
			self.sendMsg("Object creation has been disabled for non-admin players.")

	# GROUPS #

	def rcon_btnGrabGroup(self, p, params):
		if not p.grabObject:
			self.rcon_btnGrab(p, params)
		if p.grabObject:
			o = p.grabObject[0]
			if p.grabMode == 1:
				src = p.groups
			else:
				src = self.groups
			g = None
			src.reverse()
			for grp in src:
				if o in grp.objects:
					g = grp
					break
			if g:
				if g.animation:
					g.animation.stop()
				g.objects.remove(o)
				g.objects.insert(0,o)
				g.resetAnchor()
				p.lastAction.append(["grabgroup",g,g.getPosition(),g.getRotation()])
				p.grabGroup = g

	def rcon_btnStartGroup(self, p, params):
		if not p.selectedGroup:
			p.selectedGroup = Group()
			p.selectedGroup.owner = p
			if not params: p.sendMsg("GROUP_INITIALIZED")
		else:
			p.sendMsg("GROUP_ALREADY_SELECTED")

	def rcon_btnEndGroup(self, p, params):
		if p.selectedGroup:
			g = p.selectedGroup
			if g.objects:
				p.groups.append(g)
				self.groups.append(g)
			p.selectedGroup = None
			if not params: p.sendMsg("GROUP_DESELECTED")

	def rcon_btnSelectGroup(self, p, params):
		if params:
			if params[0] != 'null': g = params
			else: g = p.grabGroup
		else: g = p.grabGroup
		if g:
			p.selectedGroup = g
			self.rcon_btnDrop(p, params)
			p.groups.remove(p.selectedGroup)
			self.groups.remove(p.selectedGroup)
			if params:
				if params[0] != 'null': p.sendMsg("GROUP_SELECTED")
			else: p.sendMsg("GROUP_SELECTED")

	def rcon_btnMergeGroup(self, p, params):
		try:
			if p.selectedGroup:
				if p.grabGroup:
					g = Group()
					for o in p.selectedGroup.objects:
						g.addObject(o)
					for o in p.grabGroup.objects:
						g.addObject(o)
					p.groups.remove(p.grabGroup)
					self.groups.remove(p.grabGroup)
					self.rcon_btnDrop(p, params)
					p.selectedGroup = None
					p.groups.append(g)
					self.groups.append(g)
					p.sendMsg("MERGE_COMPLETED")
				else:
					self.rcon_btnEndGroup(p, ['end_merge'])
					p.sendMsg("MERGE_CANCELLED")
			else:
				self.rcon_btnSelectGroup(p, ['null'])
				p.sendMsg("MERGE_STARTED")
		except: ExceptionOutput()

	def rcon_btnAddToGroup(self, p, params):
		if p.selectedGroup and p.grabObject:
			p.selectedGroup.addObject(p.grabObject[0])
			p.sendMsg("GROUP_OBJECTADDED")
		else:
			self.rcon_btnSelectGroup(p, [])

	def rcon_btnRemFromGroup(self, p, params):
		if p.grabObject and p.selectedGroup:
			p.selectedGroup.removeObject(p.grabObject[0])
			p.sendMsg("GROUP_OBJECTREMOVED")

	def rcon_btnUnGroup(self, p, params):
		if not p.selectedGroup:
			self.rcon_btnSelectGroup(p, params)
		if p.selectedGroup:
			p.selectedGroup = None
			p.sendMsg("GROUP_UNGROUPED")

	def rcon_btnDuplicateGroup(self, p, params):
		if not p.selectedGroup:
			self.rcon_btnSelectGroup(p, params)
		if p.selectedGroup:
			if not self.checkObjectCount(len(p.selectedGroup.objects)):
				p.sendMsg("OBJLIMITREACHED")
				return
			if (len(p.selectedGroup.objects) <= self.settings.groupDupeLimit) or self.multiplayer == False:
				if p.groupDupeDelay:
					p.sendMsg("DUPEDELAY")
					return
				p.groupDupeDelay = self.settings.groupDupeDelay
				objects = dict(p.selectedGroup.objectData)
				self.rcon_btnEndGroup(p, ['null'])
				self.rcon_btnStartGroup(p, ['null'])
				p.selectedGroup.load = len(objects)
				tPos = p.getTracerLocation()
				for (o,oData) in objects.items():
					oName = o.templateName
					print oData[0]
					oPos = (tPos[0] + oData[0][0], tPos[1] + oData[0][1], tPos[2] + oData[0][2])
					oRot = o.getRotation()
					self.cacheObject(oName,oPos,oRot,p)
					self.queueObject(oName,oPos,oRot)
			else: p.sendMsg("GROUP_DUPELIMITREACHED")

	def rcon_selectKit(self, p, params):
		soldier = int(params[0])
		kit = int(params[1])
		if soldier >= 4 and soldier <= 6 and kit >= 0 and kit <= 6:
			p.kits[int(4)] = 0
			print "Kit selected", soldier, kit

	def rcon_verify(self, p, params):
		name = p.getName().split(" ")[-1]
		if self.settings.users.has_key(name):
			if self.settings.users[name]["password"]:
				if params[0] == self.settings.users[name]["password"]:
					print "User verified by password"
					p.level = self.settings.users[name]["level"]
					print "Setting rank for " + str(name)
					try: bf2.gameLogic.sendRankEvent(p, p.level, 1)
					except: ExceptionOutput()

	#
	# CHAT COMMANDS
	#
	

	def chat_delall(self, p, params):
		p.lastAction = []
		p.groups = []
		p.presetModeCache = None
		p.selectedAnimation = None
		p.clearGrabbed()
		for obj in list(p.objects):
			if obj.templateName in self.settings.vehicles: continue
			self.cleanDeleteObject(obj)
		p.objects = []
		p.sendMsg("All objects deleted.")

	def chat_delalln(self, p, params):
		player = self.getPlayerByIndex(int(params[0]))
		player.lastAction = []
		player.groups = []
		player.presetModeCache = None
		player.selectedAnimation = None
		for obj in list(player.objects):
			self.cleanDeleteObject(obj)
		player.objects = []
		player.sendMsg("All objects deleted.")

	def chat_rotfactor(self, p, params):
		if int(params[0]) > 1 and int(params[0]) < 180:
			p.rotationFactor = int(params[0])

	def chat_r(self, p, params):
		self.coreRemoteCommand(p.index, " ".join(params))

	def chat_c(self, p, params):
		print host.rcon_invoke(" ".join(params))
	
	def chat_reloadsettings(self, p, params):
		self.settings.loadGameSettings()
		self.settings.loadAddonSettings()
		self.settings.loadUsers()
		self.settings.loadPermissions()

	def onEnterVehicle(self, playerObject, vehicleObject, freeSoldier):
		playerObject.clearGrabbed()

	def onPlayerDeath(self, playerObject, soldierObject):
		playerObject.clearGrabbed()

	def onPlayerKilled(self, victimPlayerObject, attackerPlayerObject, weaponObject, assists, victimSoldierObject):
		victimPlayerObject.clearGrabbed()

	def onGameStatusChanged(self, status):
		if status == bf2.GameStatus.Playing:
			self.settings.loadGameSettings()
			if self.settings.mapObjectLimits.has_key(host.sgl_getMapName().lower()):
				self.settings.mpObjectLimit = self.settings.mapObjectLimits[host.sgl_getMapName().lower()]
		
	def onPlayerSpawn(self, playerObject, soldierObject):
		kit = "RP_Player"
		try:
			kit = self.addonCallbackReturn("onPlayerSpawnKit", playerObject)
		except:
			kit = "RP_Player"
			ExceptionOutput()
		print "Kit: " + str(kit)
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 0 \"" + str(kit) + "\" \"meinsurgent_soldier\"")
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 1 \"" + str(kit) + "\" \"meinsurgent_soldier\"")
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 2 \"" + str(kit) + "\" \"meinsurgent_soldier\"")
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 3 \"" + str(kit) + "\" \"meinsurgent_soldier\"")
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 4 \"" + str(kit) + "\" \"meinsurgent_soldier\"")
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 5 \"" + str(kit) + "\" \"meinsurgent_soldier\"")
		host.rcon_invoke("gameLogic.setKit " + str(playerObject.getTeam()) + " 6 \"" + str(kit) + "\" \"meinsurgent_soldier\"")

		if playerObject.firstSpawn == True:
			playerObject.firstSpawn = False

		if playerObject.level == -1:
			name = playerObject.getName().split(" ")[-1]
			if self.settings.users.has_key(name):
				if self.settings.users[name]["hash"]:
					if self.settings.users[name]["hash"] == playerObject.getKeyHash():
						print "User verified by cdkeyhash"
						playerObject.level = self.settings.users[name]["level"]
						print "Setting rank for " + str(name)
						try: bf2.gameLogic.sendRankEvent(playerObject, playerObject.level, 1)
						except: ExceptionOutput()
				elif self.settings.users[name]["password"]:
					print "User needs verification"
					playerObject.level = 0
				else:
					playerObject.level = self.settings.users[name]["level"]
					print "Setting rank for " + str(name)
					try: bf2.gameLogic.sendRankEvent(playerObject, playerObject.level, 1)
					except: ExceptionOutput()
			else:
				playerObject.level = 0

	def onPlayerConnect(self, playerObject):
		pass

	def onPlayerDisconnect(self, playerObject):
		playerObject.firstSpawn = True
	
	# 
	# ANIMATION
	#
	
	def chat_smooth(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		val = int(params[0])
		if 0 <= val <= 2:
			p.selectedAnimation.interpolate = val
		if val == 0:
			p.sendMsg("Animation smoothing off")
		elif val == 1:
			p.sendMsg("Animation smoothing set to cubic")
		elif val == 2:
			p.sendMsg("Animation smoothing set to sine")
	
	def rcon_btnAnimSelect(self, p, params):
		target = p.getGrabbed()
		if not target: return
		if target.animation:
			p.presetModeCache = None
			p.selectedAnimation = target.animation
			# undo so the object is sent back to its original spot
			self.rcon_btnUndo(p, params)
			p.sendMsg("ANIMATION_SELECTED")
		else:
			p.sendMsg("This object/group has no animation")
	
	def rcon_btnAnimDeselect(self, p, params):
		p.presetModeCache = None
		if p.selectedAnimation:
			if not p.selectedAnimation.targets:
				self.rcon_btnAnimDelete(p, params)
			p.selectedAnimation = None
			p.sendMsg("ANIMATION_DESELECTED")
	
	def rcon_btnAnimCreate(self, p, params):
		self.createAnimation(p)
	
	def createAnimation(self, p, requireObject=False):
		target = p.getGrabbed()
		if not target:
			if requireObject: return
			else: target = []
		else:
			if target.type == "object":
				if target.templateName in self.settings.vehicles: return
			target = [target]
		anim = MultiObjectAnimation(target)
		p.selectedAnimation = anim
		self.animations.append(anim)
		p.sendMsg("ANIMATION_CREATED")
		if target:
			p.sendMsg("ADDED_TO_ANIMATION")
		return True

	def rcon_btnAnimDelete(self, p, params):
		if p.selectedAnimation:
			p.selectedAnimation.delete()
			self.animations.remove(p.selectedAnimation)
			p.selectedAnimation = None
			p.sendMsg("ANIMATION_DELETED")
	
	def rcon_btnAnimAdd(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		target = p.getGrabbed()
		if not target: return
		if target.type == "object":
			if target.templateName in self.settings.vehicles: return
		###
		if p.selectedAnimation.addTarget(target):
			p.sendMsg("ADDED_TO_ANIMATION")
	
	def rcon_btnAnimRemove(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		target = p.getGrabbed()
		if not target: return
		###
		if p.selectedAnimation.removeTarget(target):
			p.sendMsg("REMOVED_FROM_ANIMATION")
	
	def rcon_btnAnimAddKeyframe(self, p, params):
		if not p.selectedAnimation:
			if not self.createAnimation(p,True): return
		###
		if not p.selectedAnimation.targets:
			p.sendMsg("THERE_ARE_NO_OBJECTS_TO_ANIMATE")
			return
		if p.selectedAnimation.addKeyframe():
			p.sendMsg("KEYFRAME_ADDED")
	
	def rcon_btnAnimDelKeyframe(self, p, params):
		if not p.selectedAnimation: return
		###
		if not p.selectedAnimation.keyframes:
			p.sendMsg("THERE_ARE_NO_KEYFRAMES_TO_DELETE")
			return
		if p.selectedAnimation.removeKeyframe():
			p.sendMsg("KEYFRAME_DELETED")
	
	def chat_animateto(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		if not params:
			p.sendMsg("NO_ANIMATION_FRAME_DEFINED")
			return
		p.selectedAnimation.animateTo(int(params[0]))
	
	def rcon_btnAnimate(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		###
		if int(params[0]) == 1:
			p.selectedAnimation.animateNext()
		else:
			p.selectedAnimation.animatePrev()
	
	def rcon_btnAnimGoto(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		###
		if int(params[0]) == 1:
			p.selectedAnimation.gotoNext()
		else:
			p.selectedAnimation.gotoPrev()
	
	def rcon_btnAnimSpeed(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		###
		if p.selectedAnimation.isBusy(): return
		result = p.selectedAnimation.changeSpeed(float(params[0]) * 10.0)
		if result:
			p.sendMsg("Keyframe speed set to " + str(int(result)) + " frames",3)
		else:
			p.sendMsg("Keyframe speed too slow/fast")
	
	def rcon_btnAnimUpdateKeyframe(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		###
		if p.selectedAnimation.updateKeyframe():
			p.sendMsg("KEYFRAME_UPDATED")
	
	def rcon_btnAnimLoop(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		###
		if not p.selectedAnimation.keyframes:
			p.sendMsg("This animation has no keyframes yet")
			return
		if not p.selectedAnimation.targets:
			p.sendMsg("THERE_ARE_NO_OBJECTS_TO_ANIMATE")
			return
		if p.selectedAnimation.loop == 0:
			p.selectedAnimation.loop = 1
			p.sendMsg("LOOP_STARTED_CONTINUOUS")
		elif p.selectedAnimation.loop == 1:
			p.selectedAnimation.loop = 2
			p.sendMsg("LOOP_STARTED_BACKANDFORTH")
		else:
			p.selectedAnimation.stop()
			p.sendMsg("LOOP_STOPPED")
	
	def rcon_btnAnimTriggerSet(self, p, params):
		if not p.selectedAnimation:
			p.sendMsg("NO_SELECTED_ANIMATION")
			return
		###
		if p.grabObject:
			object = p.grabObject[0]
			if object.trigger:
				if object.triggerAnim == p.selectedAnimation:
					if object.triggerType == 1:
						object.triggerType = 2
						p.sendMsg("TRIGGER_MODE_2")
					elif object.triggerType == 2:
						object.triggerType = 3
						p.sendMsg("TRIGGER_MODE_3")
					elif object.triggerType == 3:
						object.triggerType = 4
						p.sendMsg("TRIGGER_MODE_4")
					elif object.triggerType == 4:
						object.triggerType = 5
						p.sendMsg("TRIGGER_MODE_5")
					elif object.triggerType == 5:
						object.triggerType = 6
						p.sendMsg("TRIGGER_MODE_6")
					else:
						object.triggerType = 1
						p.sendMsg("TRIGGER_MODE_1")
				else:
					p.sendMsg("TRIGGER_DIFF_ANIMATION")
			else:
				object.triggerAnim = p.selectedAnimation
				object.triggerType = 1
				trigid = bf2.triggerManager.createRadiusTrigger(object.root, self.onAnimTrigger, '<<PCO>>', 1.5, (p,p.selectedAnimation,object))
				object.trigger = trigid
				p.sendMsg("TRIGGER_SET")
				p.sendMsg("TRIGGER_MODE_1")
		else:
			if p.presetModeCache == 1:
				p.presetModeCache = 2
				p.sendMsg("PRESET_MODE_2")
			elif p.presetModeCache == 2:
				p.presetModeCache = 1
				p.sendMsg("PRESET_MODE_1")
			else:
				p.presetModeCache = 1
				p.sendMsg("PRESET_CHOOSE")
				p.sendMsg("PRESET_MODE_1")
	
	def rcon_btnPreset(self, p, params):
		preset = int(params[0])
		action = int(params[1])
		if p.presetModeCache:
			if p.presetModeCache > 0:
				p.presets[preset] = [p.selectedAnimation,p.presetModeCache]
				p.presetModeCache = None
				p.sendMsg("PRESET_SET")
			else:
				p.presets[preset] = []
				p.presetModeCache = None
				p.sendMsg("PRESET_CLEARED")
		elif p.presets[preset]:
			try: p.presets[preset][0].onPresetTrigger(action,p.presets[preset][1])
			except: ExceptionOutput()
	
	def rcon_btnAnimTriggerUnset(self, p, params):
		if p.grabObject:
			object = p.grabObject[0]
			if object.trigger:
				bf2.triggerManager.destroy(object.trigger)
				object.trigger = None
				object.triggerAnim = None
				p.sendMsg("TRIGGER_CLEARED")
		else:
			p.presetModeCache = -1
			p.sendMsg("PRESET_CHOOSE_CLEAR")
	
	def onAnimTrigger(self, triggerID, object, vehicle, enter, params):
		owner = params[0]
		animation = params[1]
		object = params[2]
		players = vehicle.getOccupyingPlayers()
		for p in players:
			if self.getPlayerByObject(p) == owner:
				animation.onTrigger(enter, object.triggerType)
				break

class MultiObjectAnimation:
	def __init__(self, targets=[]):
		self.targets = targets
		self.keyframes = []
		self.currentFrame = None
		self.nextFrame = None
		self.animPosition = 0.0
		self.queue = []
		self.loop = 0
		self.interpolate = 1
		for t in self.targets:
			t.animation = self
	
	def delete(self):
		self.stop()
		for t in self.targets:
			self.removeTarget(t)
	
	def addTarget(self, t):
		if t in self.targets: return
		for k in self.keyframes:
			t.keyframes.append([t.getPosition(),t.getRotation()])
		t.animation = self
		self.targets.append(t)
		return True
	
	def removeTarget(self, t):
		if t in self.targets:
			self.targets.remove(t)
			t.animation = None
			t.keyframes = []
			return True
	
	def isBusy(self):
		if self.nextFrame or self.queue: return True
	
	def addKeyframe(self, speed=100.0):
		if self.isBusy(): return
		if self.currentFrame:
			frameid = self.currentFrame + 1
		else:
			frameid = 1
		self.keyframes.insert(frameid - 1,speed)
		for t in self.targets:
			t.keyframes.insert(frameid - 1,[t.getPosition(),t.getRotation()])
		self.currentFrame = frameid
		print len(self.targets),"targets",len(self.keyframes),"keyframes"
		return True
	
	def removeKeyframe(self):
		if self.isBusy(): return
		if not self.currentFrame: return
		self.keyframes.pop(self.currentFrame - 1)
		for t in self.targets:
			t.keyframes.pop(self.currentFrame - 1)
		if len(self.keyframes):
			if self.currentFrame == 1:
				self.goTo(1)
			else:
				self.goTo(self.currentFrame - 1)
		else:
			self.currentFrame = None
		return True
	
	def updateKeyframe(self):
		if self.isBusy(): return
		if not self.currentFrame: return
		for t in self.targets:
			t.keyframes[self.currentFrame - 1] = [t.getPosition(),t.getRotation()]
		return True
	
	def stop(self):
		self.loop = 0
		self.queue = []
		self.nextFrame = None
		self.animPosition = 0.0
	
	def goTo(self, keyframe):
		if len(self.keyframes) < keyframe: return
		self.stop()
		self.currentFrame = keyframe
		for t in self.targets:
			t.setPosition(t.keyframes[self.currentFrame - 1][0])
			t.setRotation(t.keyframes[self.currentFrame - 1][1])
	
	def gotoNext(self):
		if not self.currentFrame: return
		nextframe = self.currentFrame + 1
		if len(self.keyframes) < nextframe:
			nextframe = 1
		self.goTo(nextframe)
	
	def gotoPrev(self):
		if not self.currentFrame: return
		if self.currentFrame == 1:
			nextframe = len(self.keyframes)
		else:
			nextframe = self.currentFrame - 1
		self.goTo(nextframe)
	
	def animateTo(self, keyframe):
		if keyframe > len(self.keyframes): return
		self.queue.append(keyframe)
	
	def animateNext(self):
		if not self.currentFrame: return
		nextframe = self.getLastQueuedFrame() + 1
		if len(self.keyframes) < nextframe:
			nextframe = 1
		self.animateTo(nextframe)
	
	def animatePrev(self):
		if not self.currentFrame: return
		if self.getLastQueuedFrame() == 1:
			nextframe = len(self.keyframes)
		else:
			nextframe = self.getLastQueuedFrame() - 1
		self.animateTo(nextframe)
	
	def animateToStart(self, force=False):
		if not self.currentFrame: return
		if force:
			self.queue = []
		lastframe = self.getLastQueuedFrame()
		for i in range(1, lastframe):
			self.animateTo(lastframe - i)
	
	def animateToEnd(self, force=False):
		if not self.currentFrame: return
		if force:
			self.queue = []
		lastframe = self.getLastQueuedFrame()
		for i in range(lastframe, len(self.keyframes)):
			self.animateTo(i + 1)
	
	def animateStartToEnd(self, block=False):
		if block: self.stop()
		for i in range(len(self.keyframes)):
			self.animateTo(i + 1)
	
	def animateEndToStart(self, block=False):
		if block: self.stop()
		for i in range(len(self.keyframes)):
			self.animateTo(len(self.keyframes) - i)
	
	def onTrigger(self, enter, type=1):
		if type == 1:
			if enter: self.animateToEnd(True)
			else: self.animateToStart(True)
		elif type == 2 and enter:
			if self.getLastQueuedFrame() == len(self.keyframes):
				self.animateToStart(True)
			else:
				self.animateToEnd(True)
		elif type == 3 and enter:
			self.queue = []
			self.animateNext()
		elif type == 4 and enter:
			self.queue = []
			if self.getLastQueuedFrame() != len(self.keyframes):
				self.animateNext()
		elif type == 5 and enter:
			self.queue == []
			self.animatePrev()
		elif type == 6 and enter:
			self.queue = []
			if self.getLastQueuedFrame() != 1:
				self.animatePrev()
	
	def onPresetTrigger(self, direction, type=1):
		if type == 1:
			if direction == 1:
				self.animateNext()
			else:
				self.animatePrev()
		elif type == 2:
			if direction == 1:
				self.animateToEnd(True)
			else:
				self.animateToStart(True)
	
	def changeSpeed(self, factor):
		if not self.currentFrame or self.isBusy(): return
		newspeed = self.keyframes[self.currentFrame - 1] + factor
		if newspeed > 0.0 and newspeed < 500.0:
			self.keyframes[self.currentFrame - 1] = newspeed
			return newspeed
		else:
			return False
	
	def getLastQueuedFrame(self):
		if self.queue:
			return self.queue[-1]
		elif self.nextFrame:
			return self.nextFrame
		else:
			return self.currentFrame
	
	def tickFrame(self):
		if self.nextFrame:
			self.animPosition += 1.0
			startFrameSpd = self.keyframes[self.currentFrame - 1]
			for t in self.targets:
				try:
					if t.type == "object":
						if not t.isValid():
							try: self.removeTarget(t)
							except: pass
							continue
				except:
					try: self.removeTarget(t)
					except: pass
					continue
				startFramePos = t.keyframes[self.currentFrame - 1][0]
				startFrameRot = t.keyframes[self.currentFrame - 1][1]
				endFramePos = t.keyframes[self.nextFrame - 1][0]
				endFrameRot = t.keyframes[self.nextFrame - 1][1]
				animPercentage = self.animPosition / startFrameSpd
				if self.interpolate == 0:
					offsetPos = (
						startFramePos[0] + ((endFramePos[0] - startFramePos[0]) * animPercentage),
						startFramePos[1] + ((endFramePos[1] - startFramePos[1]) * animPercentage), 
						startFramePos[2] + ((endFramePos[2] - startFramePos[2]) * animPercentage)
						)
					offsetRot = (
						startFrameRot[0] + ((endFrameRot[0] - startFrameRot[0]) * animPercentage),
						startFrameRot[1] + ((endFrameRot[1] - startFrameRot[1]) * animPercentage), 
						startFrameRot[2] + ((endFrameRot[2] - startFrameRot[2]) * animPercentage)
						)
				elif self.interpolate == 1 or self.interpolate == 2:
					if self.loop == 1 and self.interpolate == 2:
						leftFrame = self.currentFrame - 1
						if leftFrame < 1:
							leftFrame = len(self.keyframes)
						leftFramePos = t.keyframes[leftFrame - 1][0]
						leftFrameRot = t.keyframes[leftFrame - 1][1]
						rightFrame = self.nextFrame + 1
						if rightFrame > len(self.keyframes):
							rightFrame = 1
						rightFramePos = t.keyframes[rightFrame - 1][0]
						rightFrameRot = t.keyframes[rightFrame - 1][1]
						offsetPos = (
							sbxMath.cubicInterpolate(leftFramePos[0], startFramePos[0], endFramePos[0], rightFramePos[0], animPercentage),
							sbxMath.cubicInterpolate(leftFramePos[1], startFramePos[1], endFramePos[1], rightFramePos[1], animPercentage), 
							sbxMath.cubicInterpolate(leftFramePos[2], startFramePos[2], endFramePos[2], rightFramePos[2], animPercentage)
							)
						offsetRot = (
							sbxMath.cubicInterpolate(leftFrameRot[0], startFrameRot[0], endFrameRot[0], rightFrameRot[0], animPercentage),
							sbxMath.cubicInterpolate(leftFrameRot[1], startFrameRot[1], endFrameRot[1], rightFrameRot[1], animPercentage), 
							sbxMath.cubicInterpolate(leftFrameRot[2], startFrameRot[2], endFrameRot[2], rightFrameRot[2], animPercentage)
							)
					else:
						offsetPos = (
							sbxMath.cosineInterpolate(startFramePos[0], endFramePos[0], animPercentage),
							sbxMath.cosineInterpolate(startFramePos[1], endFramePos[1], animPercentage), 
							sbxMath.cosineInterpolate(startFramePos[2], endFramePos[2], animPercentage)
							)
						offsetRot = (
							sbxMath.cosineInterpolate(startFrameRot[0], endFrameRot[0], animPercentage),
							sbxMath.cosineInterpolate(startFrameRot[1], endFrameRot[1], animPercentage), 
							sbxMath.cosineInterpolate(startFrameRot[2], endFrameRot[2], animPercentage)
							)
				t.setPosition(offsetPos)
				t.setRotation(offsetRot)
			if self.animPosition >= startFrameSpd:
				self.currentFrame = self.nextFrame
				self.nextFrame = None
				self.animPosition = 0.0
		elif self.queue:
			next = self.queue.pop(0)
			self.nextFrame = next
		elif self.loop:
			if self.loop == 1:
				self.animateNext()
			elif self.loop == 2:
				if self.currentFrame < len(self.keyframes):
					self.animateNext()
				else:
					self.loop = 3
					self.animatePrev()
			elif self.loop == 3:
				if self.currentFrame > 1:
					self.animatePrev()
				else:
					self.loop = 2
					self.animateNext()

class Group:
	def __init__(self):
		self.objects = []
		self.objectData = {}
		self.owner = None
		self.settings = sbxSettings.sbxSettingsManager()

		self.load = 0

		self.groups = []
		
		self.animation = None
		self.keyframes = []
		
		self.type = "group"

	def addObject(self, o, offset=None):
		if o not in self.objects and o not in self.settings.vehicles:
			if offset:
				posOffset = offset
			elif not self.objects:
				posOffset = (0.0,0.0,0.0)
			else:
				oPos = o.getPosition()
				anchor = self.objects[0]
				anchorPos = anchor.getPosition()
				posOffset = (oPos[0] - anchorPos[0], oPos[1] - anchorPos[1], oPos[2] - anchorPos[2])
			self.objects.append(o)
			self.objectData[o] = [posOffset]

	def removeObject(self, o):
		if o in self.objects:
			self.objects.remove(o)
			del self.objectData[o]

	def resetAnchor(self):
		anchor = self.objects[0]
		anchorPos = anchor.getPosition()
		for o in self.objectData:
			if o == anchor:
				oPos = (0.0,0.0,0.0)
				self.objectData[o][0] = oPos
			else:
				oPos = o.getPosition()
				self.objectData[o][0] = (oPos[0] - anchorPos[0], oPos[1] - anchorPos[1], oPos[2] - anchorPos[2])

	def setPosition(self, newPos):
		anchor = self.objects[0]
		anchor.setPosition(newPos)
		for o in self.objects:
			if o != anchor:
				oOffset = self.objectData[o][0]
				o.setPosition(((newPos[0] + oOffset[0]), (newPos[1] + oOffset[1]), (newPos[2] + oOffset[2])))
	
	def getPosition(self):
		return self.objects[0].getPosition()

	def setRotation(self, newRot):
		anchor = self.objects[0]
		oldRot = anchor.getRotation()
		rFactor = newRot[0] - oldRot[0]
		anchor.setRotation(newRot)
		try:
			for x in self.objects:
				if x != anchor:
					rot = x.getRotation()
					newPos = sbxMath.get2dRotation(self.objectData[x][0][0],self.objectData[x][0][2],-rFactor)
					self.objectData[x][0] = (newPos[0],self.objectData[x][0][1],newPos[1])
					x.setRotation(((rot[0] + rFactor), rot[1], rot[2]))
		except: ExceptionOutput()
	
	def getRotation(self):
		return self.objects[0].getRotation()