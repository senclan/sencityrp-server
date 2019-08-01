#******************************************************************************
# Name: Sandbox Object Class
# Author: Elton "Elxx" Muuga (http://elxx.net)
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************

import host
import bf2
import math

class sbxObject:
	def __init__(self, o):
		self.root = o
		self.oId = o.oId
		#self.oNum = o.oNum
		self.templateName = o.templateName
		self.rotation = o.getRotation()
		self.globalrotation = (0.0,0.0,0.0)
		self.isDynamic = False
		self.owner = None
		self.isGrabbed = False
		self.isLocked = False
		self.animation = None
		self.keyframes = []
		self.trigger = None
		self.triggerAnim = None
		self.triggerType = None
		self.type = "object"

	def isValid(self):
		return self.root.isValid()

	def getPosition(self):
		return self.root.getPosition()

	def getRotation(self):
		if self.isDynamic:
			return self.root.getRotation()
		else:
			return self.rotation

	def setPosition(self, pos):
		self.root.setPosition(pos)

	def setRotation(self, rot):
		self.root.setRotation(rot)
		if not self.isDynamic:
			self.rotation = rot

	'''def getGlobalRotation(self):
		return self.globalrotation

	def setGlobalRotation(self, rot):
		yaw = rot[0]
		pitch = rot[1]
		roll = rot[2]

		gYaw = yaw
		#gPitch = (1.0 - (gYaw / 90.0)) * pitch
		#gRoll = (gYaw / 90.0) * pitch
		gPitch = (math.cos(math.radians(yaw)) * pitch) - (math.sin(math.radians(yaw)) * roll)
		gRoll = (math.sin(math.radians(yaw)) * pitch) - (math.cos(math.radians(yaw)) * roll)

		self.globalrotation = rot
		localrotation = (gYaw, gPitch, gRoll)
		self.setRotation(localrotation)
		print self.globalrotation
		print self.rotation'''