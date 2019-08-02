from game.gamemodes.sbxErrorHandling import ExceptionOutput
class autoMessages:
	def autoMessagesInit(self):
		self.messageTimer = {
		"countDown":0,
		"count":-1,
		"messages":[
			["==============RULES============",5],
			["1. Mass killing is a kick/ban",20],
			["2. Mass car steeling is a kick/ban",20],
			["3. Prop Blocking is a kick/ban",20],
			["4. If your selling drugs, you must have a sm. crate spawned near you signifying drugs",20],
			["5. Using props to get you to a higher location is a kick/ban",20],
			["6. Using objects to kill a player is a kick/ban",20],
			["================================",60],
			["Need help with the codes? Type /help to view a list of codes", 60]
			]
		}
	
	def autoMessagesTickOneSec(self):
		try:
			if self.messageTimer["countDown"] == 0:
				self.messageTimer["count"] += 1
				if self.messageTimer["count"] >= len(self.messageTimer["messages"]):
					self.messageTimer["count"] = 0
				self.messageTimer["countDown"] = self.messageTimer["messages"][self.messageTimer["count"]][1]
				if self.messageTimer["count"] % 2 == 0:
					color = "§C1001"
				else:
					color = ""
				self.core.sendMsg("§3" + str(color) + str(self.messageTimer["messages"][self.messageTimer["count"]][0]))
			else:
				self.messageTimer["countDown"] -= 1
		except:
			ExceptionOutput()
			