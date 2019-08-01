NAME 	= "Kill"
VERSION = "1.0"
AUTHOR 	= "Bullace"
WEBSITE = "http://sandboxaddicted.com"
HIDDEN = 1
COMMANDS = {
	"kill": ["player ID","Will kill player with ID [player ID]"],
	"autokill": ["player ID","Will toogle autokill on player with ID [player ID]"]
}
PERMISSIONS = {
	"chat": {
		"kill": 21,
		"autokill": 21
	}
}

from game.gamemodes.sbxErrorHandling import ExceptionOutput
import host
import bf2

class Addon:
	def __init__(self, core):
		self.core = core

	def onPlayerConnect(self, playerObject):
		playerObject.autokill = False
		playerObject.autoheal = False

	def onGameStatusChanged(self, status):
		for p in self.core.getAllPlayers():
			p.autokill = False
			p.autoheal = False
		if status == bf2.GameStatus.Playing:
			self.bleed()

	def tickFrame(self):
		self.autokill()

	def autokill(self):
		for p in self.core.getAlivePlayers():
			if p.autokill == True:
				if p.isAlive():
					if p.autoheal == True:
						p.autoheal = False
					try:
						if p.getVehicle() == p.getDefaultVehicle():
							p.getDefaultVehicle().setDamage(0.1)
						else:
							p.getVehicleRoot().setDamage(0.1)
					except: pass

	def bleed(self):
		host.rcon_invoke("objecttemplate.active meinsurgent_heavy_soldier")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")
		host.rcon_invoke("objecttemplate.active meinsurgent_heavy_soldier_3p")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")
		host.rcon_invoke("objecttemplate.active meinsurgent_soldier_jet")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")
		host.rcon_invoke("objecttemplate.active meinsurgent_soldier_jet_3p")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")
		host.rcon_invoke("objecttemplate.active us_light_soldier")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")
		host.rcon_invoke("objecttemplate.active mec_heavy_soldier")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")
		host.rcon_invoke("objecttemplate.active ch_heavy_soldier")
		host.rcon_invoke("ObjectTemplate.armor.hpLostWhileCriticalDamage 0.1")
		host.rcon_invoke("ObjectTemplate.armor.criticalDamage 0.1")

	def chat_kill(self, p, params):
		player = self.core.getPlayerByIndex(int(params[0]))
		if player.autoheal == True:
			player.autoheal = False
		try:
			if player.getVehicle() == player.getDefaultVehicle():
				player.getDefaultVehicle().setDamage(0.1)
			else:
				player.getVehicleRoot().setDamage(0.1)
		except: pass

	def chat_autokill(self, p, params):
		player = self.core.getPlayerByIndex(int(params[0]))
		if player.autokill == False:
			player.autokill = True
		else:
			player.autokill = False