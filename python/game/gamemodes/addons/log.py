NAME 	= "Player Info Logger"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
HIDDEN = 1
DESCRIPTION = "Stores player info in /sandbox/players/ (if folder excists!)"

import host
import bf2
import ConfigParser

class Addon:
	def __init__(self, core):
		self.core = core

	def onPlayerConnect(self, playerObject):
		prefix = playerObject.getName().split(" ")[-0]
		name = playerObject.getName().split(" ")[-1]
		if prefix == name: prefix = "N/A"
		file = open(host.sgl_getModDirectory() +"/players/" + str(name) + ".txt","w")
		file.write("Name: " + str(name) + "\n")
		file.write("Prefix: " + str(prefix) + "\n")
		file.write("Gamespy ID: " + str(playerObject.getProfileId()) + "\n")
		file.write("CDKeyHash: " + str(playerObject.getKeyHash()) + "\n")
		file.write("IP: " + str(playerObject.getAddress()))
		file.close()