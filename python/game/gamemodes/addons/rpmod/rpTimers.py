import host
from game.gamemodes.sbxErrorHandling import ExceptionOutput

class timers:
	def tickOneSec(self):
		try:
			if self.loadedSettings == 0:
				self.rp_loadsettings(None, None)
		except:
			print "Failed Loading Settings"
			ExceptionOutput()
		
		try:
			for teamP in self.core.getAllPlayers():
				name = teamP.getName().split(" ")[-1]
				if not self.players.has_key(str(name)):
					print "Player " + str(name) + " Account not found to switch teams"
					continue
				if self.players[str(name)]["job"] == "Police Officer":
					teamP.setTeam(1)
				elif teamP.getTeam() != 2:
					teamP.setTeam(2)
		except:
			print "Failed on Switching teams " + str(name)
			ExceptionOutput()
		
		try:self.rpTickSec()
		except:
			print "failed rpTickSec"
			ExceptionOutput()
		
		try:self.autoMessagesTickOneSec()
		except:
			print "failed autoMessagesTickOneSec"
			ExceptionOutput()
		
		try:
			self.coreTickSec()
		except:
			print "failed coreTickSec"
			ExceptionOutput()
			
		try:
			self.vehicleTickSec()
		except:
			print "Failed vehicleTickSec"
			ExceptionOutput()
			
		try:
			self.playerTickSec()
		except:
			print "Failed playerTickSec"
			ExceptionOutput()
		
		try:
			self.extraTickSec()
		except:
			print "Failed extraTickSec"
			ExceptionOutput()
		"""
		try:
			self.roleplayTickSec()
		except:
			print "Failed roleplayTickSec"
			ExceptionOutput()
		"""
			
			
		try:
			self.saveAcc += 1
			if self.saveAcc == 5:
				for pSaveAcc in self.core.getAllPlayers():
					if self.players.has_key(str(self.getName(pSaveAcc))):
						pSaveAccList = {
								"bank":self.players[str(self.getName(pSaveAcc))]["bank"],
								"job":"Ped",
								"snacks":0
							}
						self.saveAccount(pSaveAcc, pSaveAccList)
					else:
						print str(pSaveAcc.getName()) + " Account Not Found"
				self.saveAcc = 0
		except:
			print "Failed on save account timer"
			ExceptionOutput()
		
		try:
			if self.status == "Home":
				if self.statusTimer == 0:
					self.statusTimer = int(self.settings["worktime"])
					self.status = "Work"
					self.core.sendMsg("§3§C1001EVERYONE IS NOW AT WORK!!!")
			
			if self.status == "Work":
				if self.statusTimer == 0:
					self.statusTimer = int(self.settings["offtime"])
					self.status = "Home"
					self.core.sendMsg("§3§C1001EVERYONE IS NOW HOME!!!!!")
			
			if self.statusTimer > 0:
				self.statusTimer -= 1
		except:
			print "Failed on Status Change"
			ExceptionOutput()
		
		try:
			for time in self.timers:
				self.timers[time] -= 1
				if self.timers[time] <= 0:
					del self.timers[time]
		except:
			print "Failed on timers"
			ExceptionOutput()
		
		try:
			for JP in self.players:
				if self.players[JP].has_key("jailed") and self.players[JP].has_key("jailtime"):
					self.players[JP]["jailtime"] -= 1
					if self.players[JP]["jailtime"] <= 0:
						self.rp_job_unarrest(None, [str(JP)], 1)
		except:
			print "Failed on jail timer"
			ExceptionOutput()
		
		
	def tickFrame(self):
		self.vehicleTickFrame()

	def tickHalfSec(self):
		self.vehicleTickHalfSec()