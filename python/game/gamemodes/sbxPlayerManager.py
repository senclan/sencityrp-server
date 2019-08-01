#******************************************************************************
# Name: Sandbox Player Class
# Author: Elton "Elxx" Muuga (http://elxx.net)
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************

import host
import bf2
import bf2.PlayerManager
from bf2.stats.constants import *
import re

import sbxMath

from sbxSettings import *
sbxSettingsManager = sbxSettingsManager()

class sbxPlayer:
	def __init__(self, pObject):
		self.bf2PlayerObject = pObject

		self.index = self.bf2PlayerObject.index
		self.score = bf2.PlayerManager.PlayerScore(self.index)
		
		self.cacheName = self.bf2PlayerObject.getName()
		self.cacheProfileId = self.bf2PlayerObject.getProfileId()

		self.tracerDistance = 8
		self.rotationFactor = 5.0
		self.gridSnap = 0
		self.grabMode = 1
		self.grabSnap = 1
		self.autoGrab = True
		self.autoLock = False
		self.lastTemplate = ""
		self.lastRotation = (0.0,0.0,0.0)
		self.savedRotation = (0.0,0.0,0.0)

		self.objects = []
		self.grabObject = []
		self.lastAction = []

		self.groups = []
		self.grabGroup = []
		self.selectedGroup = None
		
		self.animations = []
		self.selectedAnimation = None
		
		self.presetModeCache = None
		self.presets = {1: [], 2: [], 3: [], 4: [], 5: []}
		
		self.groupDupeDelay = 0
		self.saveDelay = 0
		self.spawnDelay = 0
		self.firstSpawn = True

		self.kits = {}
		self.kits[4] = 2
		self.kits[5] = 2
		self.kits[6] = 2

		self.connectTime = 0
		self.disconnectTime = 0
		
		self.msgCache = {}

		self.level = -1

	def reinit(self, pObject):
		self.bf2PlayerObject = pObject
		self.index = self.bf2PlayerObject.index
		self.score = bf2.PlayerManager.PlayerScore(self.index)
		self.cacheName = self.bf2PlayerObject.getName()
		self.cacheProfileId = self.bf2PlayerObject.getProfileId()

	def getTracerLocation(self, distance = -1):
		if distance == -1: distance = self.tracerDistance
		return sbxMath.getVectoredPosition(self.getDefaultVehicle().getPosition(), distance, self.getDefaultVehicle().getRotation(), self.getSoldierCam().getRotation())

	def getSoldierCam(self):
		parent = getRootParent(self.getDefaultVehicle())
		kids = parent.getChildren()
		for child in kids:
			if child.templateName == "SoldierCamera":
				return child
		for child in kids:
			if child.templateName == "SoldierCameraChase":
				return child

	def getPosition(self):
		return self.getDefaultVehicle().getPosition()

	def setPosition(self, pos):
		self.getVehicle().setPosition(pos)

	def sendMsg(self, msg, group=0):
		if sbxSettingsManager.pMessages.has_key(msg):
			x = sbxSettingsManager.pMessages[msg]
			bf2.gameLogic.sendMedalEvent(self.bf2PlayerObject, x[0], x[1])
		else:
			if group:
				self.msgCache[group] = msg
			else:
				host.rcon_invoke("game.sayAll \"" + "§C1001" + str(self.getName()) + " - " + str(msg) + "§C1001" + "\"")
	
	def getGrabbed(self):
		if self.grabGroup:
			return self.grabGroup
		elif self.grabObject:
			return self.grabObject[0]
		else:
			return False

	def clearGrabbed(self):
		self.grabObject = []
		self.grabGroup = []
		self.sendHudEvent(58) #not close to mine
		
	def setScores(self, score=0, team=0, kills=0, deaths=0):
		self.score.score = int(score)
		self.score.skillScore = int(team)
		self.score.rplScore = int(kills)
		self.score.deaths = int(deaths)

	def setScoreScore(self, score):
		self.score.score = int(score)

	def setScoreTeam(self, score):
		#self.score.skillScore = int(score)
		self.score.rplScore = int(score)

	def setScoreKills(self, score):
		self.score.kills = int(score)

	def setScoreDeaths(self, score):
		self.score.deaths = int(score)
	
	def clearScores(self):
		self.setScoreScore(0)
		self.setScoreTeam(0)
		self.setScoreKills(0)
		self.setScoreDeaths(0)

	def sendHudEvent(self, event):
		bf2.gameLogic.sendHudEvent(self.bf2PlayerObject, event, self.bf2PlayerObject.index)
	
	def hasJetpack(self):
		soldier = self.getDefaultVehicle()
		if soldier:
			if soldier.templateName[-4:] == "_jet" or soldier.templateName[-7:] == "_jet_3p": return True
		return False

	def getIndex(self): return self.bf2PlayerObject.index
	
	# thanks http://bf2tech.org/index.php/Cookbook:Accessing_CD_Key_Hash
	def getKeyHash(self):
		if not self.isRemote(): return
		rawData = host.rcon_invoke( "admin.listplayers" )
		pattern = re.compile(r'''^Id:\ +(\d+)
					\ -\ (.*?)
					\ is\ remote\ ip:\ (\d+\.\d+\.\d+\.\d+):
					(\d+)
					(?:.*?hash:\ (\w{32}))?
					''', re.DOTALL | re.MULTILINE | re.VERBOSE )
		for data in pattern.findall(rawData):
			print data[0]
			if ((str(data[0]) == str(self.getIndex())) or (str(data[1]) == str(self.getIndex()))):
				info = [data[0],data[1],data[2],data[3],data[4]]
				if not info[4]: info[4] = "N/A"
				return info[4]

	def isValid(self): return self.bf2PlayerObject.isValid()
	def isRemote(self): return self.bf2PlayerObject.isRemote()
	def isAIPlayer(self): return self.bf2PlayerObject.isAIPlayer()
	def isAlive(self): return self.bf2PlayerObject.isAlive()
	def isManDown(self): return self.bf2PlayerObject.isManDown()
	def isConnected(self): return self.bf2PlayerObject.isConnected()
	def getProfileId(self):
		if self.bf2PlayerObject:
			return self.bf2PlayerObject.getProfileId()
		else:
			return self.cacheProfileId

	def isFlagHolder(self): return self.bf2PlayerObject.isFlagHolder()

	def getTeam(self): return self.bf2PlayerObject.getTeam()
	def setTeam(self, t): return self.bf2PlayerObject.setTeam(t)
	def getPing(self): return self.bf2PlayerObject.getPing()

	def getSuicide(self): return self.bf2PlayerObject.getSuicide()
	def setSuicide(self, t): return self.bf2PlayerObject.setSuicide(t)

	def getTimeToSpawn(self): return self.bf2PlayerObject.getTimeToSpawn()
	def setTimeToSpawn(self, t): return self.bf2PlayerObject.setTimeToSpawn(t)

	def getSquadId(self): return self.bf2PlayerObject.getSquadId()
	def isSquadLeader(self): return self.bf2PlayerObject.isSquadLeader()
	def isCommander(self): return self.bf2PlayerObject.isCommander()

	def getName(self):
		if self.bf2PlayerObject:
			return self.bf2PlayerObject.getName()
		else:
			return self.cacheName
	def setName(self, name): return self.bf2PlayerObject.setName(name)

	def getSpawnGroup(self): return self.bf2PlayerObject.getSpawnGroup()
	def setSpawnGroup(self, t): return self.bf2PlayerObject.setSpawnGroup(t)

	def getKit(self): return self.bf2PlayerObject.getKit()
	def getVehicle(self): return self.bf2PlayerObject.getVehicle()
	def getVehicleRoot(self): return getRootParent(self.bf2PlayerObject.getVehicle())
	def getDefaultVehicle(self): return self.bf2PlayerObject.getDefaultVehicle()
	def getPrimaryWeapon(self): return self.bf2PlayerObject.getPrimaryWeapon()

	def getAddress(self): return self.bf2PlayerObject.getAddress()

	def setIsInsideCP(self, val): return self.bf2PlayerObject.setIsInsideCP(val)
	def getIsInsideCP(self): return self.bf2PlayerObject.getIsInsideCP()
