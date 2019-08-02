NAME 	= "SeN RP CODES"
VERSION = "1.0."
AUTHOR 	= "=SeN= Mike__MRM"
WEBSITE = "www.senclan.com"
DESCRIPTION = "RP CODES FOR SEN CITY"

from game.gamemodes.addons.rpmod.rpCore import rpCore
from game.gamemodes.addons.rpmod.rpCoreCommands import coreCmd
from game.gamemodes.addons.rpmod.rpSettings import Settings
from game.gamemodes.addons.rpmod.rpJail import jail
from game.gamemodes.addons.rpmod.rpObjActions import objActions
from game.gamemodes.addons.rpmod.rpOthers import othersCodes
from game.gamemodes.addons.rpmod.rpPlayer import players
from game.gamemodes.addons.rpmod.rpVehicles import vehicles
from game.gamemodes.addons.rpmod.extraJobs import extraJobs
from game.gamemodes.addons.rpmod.automessages import autoMessages
from game.gamemodes.addons.rpmod.rpTimers import timers
from game.gamemodes.addons.rpmod.rpAdmin import Admin
from game.gamemodes.addons.rpmod.rpAccount import Accounts
from game.gamemodes.sbxErrorHandling import ExceptionOutput
import host
import bf2
import ConfigParser
import random

class Addon(rpCore, coreCmd, jail, objActions, othersCodes, players, timers, vehicles, Settings, Accounts, Admin, extraJobs, autoMessages):
	def __init__(self, core):
		self.core = core
		self.settings = {}
		self.loadedSettings = 0
		self.drugJobs = {}
		self.fishers = {}
	
	def rpTickSec(self):
		for p in self.core.getAlivePlayers():
			if self.getPos(p)[0] == "fishingSpot" or self.getPos(p)[0] == str(self.players[self.getName(p)]["job"]):
				if not self.players[self.getName(p)].has_key("lastPos"):
					self.players[self.getName(p)]["lastPos"] = self.getPos(p)
					p.sendMsg("Has entered " + str(self.getPos(p)[0]))
			else:
				if self.players[self.getName(p)].has_key("lastPos"):
					p.sendMsg("Has left " + str(self.players[self.getName(p)]["lastPos"][0]))
					del self.players[self.getName(p)]["lastPos"]
		
		for p in self.core.getAlivePlayers():
			if self.fishers.has_key(self.getName(p)):
				if not self.getPos(p)[0] == "fishingSpot":
					continue
				if self.fishers[self.getName(p)]["Status"] == "Fishing":
					if self.fishers[self.getName(p)]["TimeToWait"] > 0:
						self.fishers[self.getName(p)]["TimeToWait"] -= 1
						continue
					randWeight = random.randrange(8)+2
					self.fishers[self.getName(p)]["Fish"].append(int(randWeight))
					randTime = random.randrange(30)+30
					self.fishers[self.getName(p)]["TimeToWait"] = randTime
					p.sendMsg("Cought a " + str(randWeight) + " lbs fish")
					if len(self.fishers[self.getName(p)]["Fish"]) == 10:
						p.sendMsg("You have hit your max fish.")
						self.rp_fish(p, ["stop"])
		
	def rp_spawn(self, p, params):
		pl = self.getPlayerName(params[0])[0]
		object = params[1]
		if object in self.core.settings.sbxObjects or object in self.core.settings.vehicles or object in self.core.settings.dynamic_objects:
			self.core.rcon_btnCreate(pl, [object, 1])
	
	#Alpha Codes
	#=================================
	def chat_setpos(self, p, params):
		self.pos[str(params[0])] = {str(params[1]):p.getDefaultVehicle().getPosition()}
		position = open(self.rpModSettingsDir + "positions.txt",'a')
		position.write("\n"+str(params[1]) + ";"+str(params[0])+"="+str(self.pos[str(params[0])][str(params[1])]) + ";" + str(params[2]) + ";" + str(params[3]))
		position.close()
		p.sendMsg("Position Set")
	
	def chat_info(self, p, params):
		p.sendMsg(str(self.getPos(p)))
	def rp_job_delivery(self, p, params, value):
		cmd = str(params[0])
		params.remove(params[0])
		if cmd == "start":
			pos = self.getPos(p)
			if pos:
				posName = pos[0].split("_")
				if posName[0] == "delivery":
					if posName[1] == "deliverystart":
						randomstr = random.randrange(int(len(self.deliveries)))
						count = 0
						while self.deliveries[randomstr] == "deliverystart":
							randomstr = random.randrange(int(len(self.deliveries)))
						while count < len(self.deliveries):
							if count == randomstr:
								break
							count += 1
						self.players[self.getName(p)]["delivery"] = {"status":0, "delivery":count, "timer":0}
						p.sendMsg("Deliver this info " + str(self.deliveries[count]))
					else:
						p.sendMsg("Not at the bank")
				else:
					p.sendMsg("Not at the bank")
			else:
				p.sendMsg("Not at the bank")

		if cmd == "drop":
			if not self.players[self.getName(p)].has_key("delivery"):
				p.sendMsg("You haven't started a delivery, type /delivery start")
				return
			pos = self.getPos(p)
			if pos:
				posName = pos[0].split("_")
				if posName[0] == "delivery":
					if posName[1] == self.deliveries[self.players[self.getName(p)]["delivery"]["delivery"]]:
						time = self.players[self.getName(p)]["delivery"]["timer"]
						if time < 60: amount = 50
						elif time > 90: amount = 10
						else: amount = ((60 / time) * 50)
						self.players[self.getName(p)]["bank"] += amount
						del self.players[self.getName(p)]["delivery"]
						p.sendMsg("Delivery Finished! + " + str(amount) + " Dollars! in " + str(time) + " seconds")
						return
					else:
						p.sendMsg("Wrong Delivery Area")
						return
			p.sendMsg("Not in delivery area")
		
		if cmd == "help":
			p.sendMsg("Codes are /delivery start and /delivery drop you must be at the bank to start a delivery")
	
	
	def rp_fish(self, p, params):
		if not self.fishers.has_key(self.getName(p)):
			self.fishers[self.getName(p)] = {"Fish":[], "Status":"Stopped", "TimeToWait":0}
		if len(params) == 0:
			p.sendMsg("Commands: start, stop, done, status")
			return
		cmd = str(params[0])
		params.remove(params[0])
		if self.getPos(p)[0] != "marinashopattendant" and self.getPos(p)[0] != "fishingSpot":
			p.sendMsg("Your not at the Marina's Cashier Counter or the Fishing Spot.")
			return
		if cmd == "start":
			if not self.fishers.has_key(self.getName(p)):
				self.fishers[self.getName(p)] = {"Fish":[], "Status":"Stopped", "TimeToWait":20}
			if self.fishers[self.getName(p)]["Status"] == "Stopped":
				self.fishers[self.getName(p)]["Status"] = "Fishing"
				p.sendMsg("Started Fishing")
			else:
				p.sendMsg("You have to stop fishing before starting again. type /fish stop")
		
		if cmd == "stop":
			if not self.fishers.has_key(self.getName(p)):
				p.sendMsg("You haven't started fishing yet, type /fish start")
				return
			if self.fishers[self.getName(p)]["Status"] == "Stopped":
				p.sendMsg("You are not fishing, type /fish start")
				return
			self.fishers[self.getName(p)]["Status"] = "Stopped"
			p.sendMsg("Has Stopped fishing")
		
		if cmd == "done":
			try:
				if not self.fishers.has_key(self.getName(p)):
					p.sendMsg("You haven't fished yet")
					return
				if self.getPos(p)[0] == "marinashopattendant":
					pounds = 0
					for amount in self.fishers[self.getName(p)]["Fish"]:
						pounds += amount
					pay = pounds * 1.5
					self.players[self.getName(p)]["bank"] += pay
					del self.fishers[self.getName(p)]
					p.sendMsg("Thank you for fishing! You have been paid " + str(pay) + " dollars")
				else:
					p.sendMsg("You must be at the cashiers counter to get paid")
			except:
				ExceptionOutput()
		if cmd == "status":
			if not self.fishers.has_key(self.getName(p)):
				p.sendMsg("You haven't fished yet")
				return
			numOfPounds = 0
			for fishlbs in self.fishers[self.getName(p)]["Fish"]:
				numOfPounds += fishlbs
			p.sendMsg("Fishing Status: " + str(self.fishers[self.getName(p)]["Status"]) + " | NumOfFish:" + str(len(self.fishers[self.getName(p)]["Fish"])) + " | Total Pounds: " + str(numOfPounds))
