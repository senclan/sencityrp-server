NAME 	= "Group All"
VERSION = "1.2"
AUTHOR 	= "FrostedFreeze-18"
WEBSITE = "http://www.xfire.com/profile/frostedfreeze/"
HIDDEN = 1
COMMANDS = {
	"groupall": ["Adds all of your objects to a group."],
	"ungroupall": ["Ungroups all of your objects."],
	"saveall": ["name","Saves all of your objects as a group."]
}

import host

class Addon:

	def __init__(self, core):
		self.core = core
		self.savetime = 0
	
	def onPlayerConnect(self, playerObject):
		playerObject.savebackup = 0
	
	def tickOneSec(self):
		self.savetime += 1
		if self.savetime == 80:
			self.core.sendMsg("Got to a big point? Want to BackupNow? type @backupnow")
		if self.savetime == 105:
			self.core.sendMsg("Backing up in 15 Seconds")
		if self.savetime == 110:
			self.core.sendMsg("Backing up in 10 Seconds")
		if self.savetime == 118:
			self.core.sendMsg("§3Backing UP!!!")
		if self.savetime == 120:
			self.savetime = 0
			for p in self.core.getAllPlayers():
				try: 
					if p.savebackup == 1:
						player = p
						self.backupnow(player, params = "")
				except: pass
			
	def rcon_groupall(self, p, params):
		self.chat_groupall(p, params)

	def rcon_ungroupall(self, p, params):
		self.chat_ungroupall(p, params)

	def rcon_saveall(self, p, params):
		self.chat_saveall(p, params)

	def chat_groupall(self, p, params):
		self.core.rcon_btnEndGroup(p, params)
		self.core.rcon_btnStartGroup(p, params)
		objCount = 0
		for x in p.objects:
			objCount += 1
			try:
				p.selectedGroup.addObject(x, None)
			except:
				p.sendMsg("Found a problem with the " + str(objCount) + " object added, exempting that object from group")
		self.core.rcon_btnEndGroup(p, params)

	def chat_ungroupall(self, p, params):
		if p.groups == []: return
		self.core.rcon_btnEndGroup(p, params)
		p.groups = []
		p.grabGroup = []
		p.selectedGroup = None
		p.sendMsg("GROUP_UNGROUPED")
		
	def chat_saveall(self, p, params):
		self.chat_ungroupall(p, params)
		self.chat_groupall(p, params)
		p.grabObject = [p.objects[0]]
		self.core.rcon_btnGrabGroup(p, params)
		if not params: params = ["QuickSave"]
		groupName = params
		self.core.chat_netsavegroup(p, groupName)
		p.sendMsg("The group was saved as '" + " ".join(groupName) + "'.")
	
	def chat_ocsaveall(self, p, params):
		self.chat_ungroupall(p, params)
		self.chat_groupall(p, params)
		p.grabObject = [p.objects[0]]
		self.core.rcon_btnGrabGroup(p, params)
		if not params: params = ["QuickSave"]
		groupName = params
		self.core.chat_netsavegroup(p, groupName)
		p.sendMsg("The group was saved as '" + " ".join(groupName) + "'.")
		
	def backupnow(self, p, params):
		self.chat_ungroupall(p, params)
		self.chat_groupall(p, params)
		p.grabObject = [p.objects[0]]
		self.core.rcon_btnGrabGroup(p, params)
		if not params: params = ["QuickSave"]
		pname = p.getName().split(" ")[-1]
		filename = "BACKUP - " + str(pname)
		
		if not p.selectedGroup:
			self.core.rcon_btnSelectGroup(p, [])
		if p.selectedGroup:
			try: out_file = open(host.sgl_getModDirectory() + "/saved/" + str(filename) + ".bf2sbg","w")
			except:
				p.sendMsg("Could not open file for writing.")
				try:
					p.sendMsg("Name is " + str(filename))
				except:
					p.sendMsg("RLLY")
				return
			out_file.write(self.core.saveGroup(p.selectedGroup))
			out_file.close()
			p.sendMsg("your creation has been backed up as " + str(filename) + ".bf2sbg")
			
	def chat_savebackup(self, p, params):
		if params[0] == "on":
			p.savebackup = 1
			p.sendMsg("Turned on - this groups everything to save, dont want your stuff grouped turn it off")
		else:
			p.savebackup = 0
			p.sendMsg("Turned off")

	def chat_loadbackup(self, p, params):
		pname = p.getName().split(" ")[-1]
		groupName = "BACKUP - " + str(pname)
		filename = groupName
		try: in_file = open(host.sgl_getModDirectory() + "/saved/" + str(filename) + ".bf2sbg","r")
		except:
			p.sendMsg("The file you specified was not found.")
			return
		data = in_file.read()
		in_file.close()
		if data:
			try: self.core.loadGroup(p, data)
			except: p.sendMsg("Error with loading Backup")
	
	def chat_backupnow(self, p, params):
		try:
			self.backupnow(p, params = "")
		except:
			p.sendMsg("Error")
	
	