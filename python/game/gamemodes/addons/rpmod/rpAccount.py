import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput
class Accounts:

	def playerConnectLogin(self, p):
		if self.players.has_key(self.getName(p)):
			return
			
		if not self.loadAccount(p):
			if self.saveAccount(p, {"bank":500, "job":"Ped", "snacks":0}):
				if not self.loadAccount(p):
					p.sendMsg("Unable to load account")
				else:
					p.sendMsg("Account Loaded")
		else:
			p.sendMsg("Account Loaded")
				
			

	def loadAccount(self, p):
		try:
			loadAcc = open(host.sgl_getModDirectory() + "/acc/" + str(p.getProfileId()) + ".txt", "r")
			self.players[str(self.getName(p))] = {}
			for info in loadAcc:
				info = info.replace("\n", "")
				info = info.replace("\r", "")
				if info[0] == ";":
					continue
				pInfo = info.split(" = ")
				pInfo[1] = str(pInfo[1])
				if pInfo[0] == "bank":
					pInfo[1] = float(pInfo[1])
				if pInfo[0] == "snacks":
					pInfo[1] = int(pInfo[1])
				self.players[str(self.getName(p))][str(pInfo[0])] = pInfo[1]
				print str(pInfo[0]) + " " + str(pInfo[1])
			loadAcc.close()
			return True
		except:
			print "Failed to load Account"
			ExceptionOutput()
			return False

	def saveAccount(self, p, info):
		try:
			name = self.getName(p)
			saveAcco = open(host.sgl_getModDirectory() + "/acc/" + str(p.getProfileId()) + ".txt", "w")
			saveAcco.write(";This is " + str(name) + "'s Account\n")
			for item in info:
				saveAcco.write(str(item) + " = " + str(info[str(item)]) + "\n")
			saveAcco.close()
			return True
		except:
			print "Failed to Save Account"
			ExceptionOutput()
			return False