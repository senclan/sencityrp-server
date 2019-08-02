import host

#
# Thanks to kiff on BFEditor.org for the original concept of this event dispatcher
# http://bfeditor.org/forums/index.php?s=&showtopic=4304&view=findpost&p=35124
#

class eventDispatcher:
	def __init__(self):
		print "Event dispatcher init"
		host.registerGameStatusHandler(self.onGameStatusChanged)
		host.registerHandler('PlayerDeath', self.onPlayerDeath)
		host.registerHandler('PlayerKilled', self.onPlayerKilled)
		host.registerHandler('PlayerSpawn', self.onPlayerSpawn)
		host.registerHandler('PickupKit', self.onPickupKit)
		host.registerHandler('DropKit', self.onDropKit)
		host.registerHandler('EnterVehicle', self.onEnterVehicle)
		host.registerHandler('ExitVehicle', self.onExitVehicle)
		host.registerHandler('VehicleDestroyed', self.onVehicleDestroyed)
		host.registerHandler('PlayerConnect', self.onPlayerConnect, 1)
		host.registerHandler('PlayerDisconnect', self.onPlayerDisconnect, 1)
		host.registerHandler('ChatMessage', self.onChatMessage, 1)
		host.registerHandler('RemoteCommand', self.onRemoteCommand, 1)
		host.registerHandler('TimeLimitReached', self.onTimeLimitReached, 1)
		
		self.events = {}
		self.events["GameStatusChanged"] = []
		self.events["PlayerDeath"] = []
		self.events["PlayerKilled"] = []
		self.events["PlayerSpawn"] = []
		self.events["PickupKit"] = []
		self.events["DropKit"] = []
		self.events["EnterVehicle"] = []
		self.events["ExitVehicle"] = []
		self.events["VehicleDestroyed"] = []
		self.events["PlayerConnect"] = []
		self.events["PlayerDisconnect"] = []
		self.events["ChatMessage"] = []
		self.events["RemoteCommand"] = []
		self.events["TimeLimitReached"] = []
	
	def registerHandler(self,event,handler):
		self.events[event] = [handler]
	
	def unregisterHandler(self, event):
		self.events[event] = []
	
	def onGameStatusChanged(self, *args):
		for f in self.events["GameStatusChanged"]:
			f(*args)

	def onTimeLimitReached(self, *args):
		for f in self.events["TimeLimitReached"]:
			f(*args)

	def onPlayerDeath(self, *args):
		for f in self.events["PlayerDeath"]:
			f(*args)

	def onPlayerKilled(self, *args):
		for f in self.events["PlayerKilled"]:
			f(*args)

	def onPlayerSpawn(self, *args):
		for f in self.events["PlayerSpawn"]:
			f(*args)

	def onPickupKit(self, *args):
		for f in self.events["PickupKit"]:
			f(*args)

	def onDropKit(self, *args):
		for f in self.events["DropKit"]:
			f(*args)

	def onEnterVehicle(self, *args):
		for f in self.events["EnterVehicle"]:
			f(*args)

	def onExitVehicle(self, *args):
		for f in self.events["ExitVehicle"]:
			f(*args)

	def onVehicleDestroyed(self, *args):
		for f in self.events["VehicleDestroyed"]:
			f(*args)

	def onPlayerConnect(self, *args):
		for f in self.events["PlayerConnect"]:
			f(*args)

	def onPlayerDisconnect(self, *args):
		for f in self.events["PlayerDisconnect"]:
			f(*args)

	def onChatMessage(self, *args):
		for f in self.events["ChatMessage"]:
			f(*args)

	def onRemoteCommand(self, *args):
		for f in self.events["RemoteCommand"]:
			f(*args)

host.gpmevents = eventDispatcher()