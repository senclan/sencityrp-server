NAME 	= "admin load"
VERSION = "1.0"
AUTHOR 	= "Mike__MRM"
WEBSITE = "www.mikemrm.com"
DESCRIPTION = "allows admins to load as big of a group as they want"
HIDDEN = 1
import bf2
import host
import socket
from game.gamemodes.sbxErrorHandling import ExceptionOutput

host = "www.sandboxmod.com"
path = "/~sandbox/network/server2.0/"

def http_post(host, port = 80, document = "/",data="", timeout = 5):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(timeout)
	try: sock.connect((host, port))
	except: return false
	sock.sendall("POST "+str(document)+" HTTP/1.0\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+str(len(data))+"\r\n\r\n"+str(data))
	data = ""
	while 1:
		buf = sock.recv(1024)
		if not buf: break
		data += buf
	sock.close()
	data = data.split("\r\n\r\n")
	return data[len(data)-1]
def sbxsaveGroup(name, pid, groupName, data):
	name = name.replace("&","")
	pid = int(pid)
	groupName = groupName.replace("&","")
	data = data.replace("&","")
	return http_post(host, 80, path+"sbx.saveGroup.php","name="+str(name)+"&pid="+str(pid)+"&groupName="+str(groupName)+"&data="+str(data))
class Addon:

	def __init__(self, core):
		self.core = core
	
	def chat_info(self, p, params):
		objabletoload = self.core.settings.mpObjectLimit - self.core.objectCount - 100
		self.core.sendMsg("Number of objects loadable: " + str(objabletoload))
		
	def loadGroup(self, p, data):
		objDefinitions = data.split("!")
		objects = []
		for oInfo in objDefinitions:
			if oInfo:
				oInfo = oInfo.split(";")
				oName = oInfo[0].replace("_mp","")
				if oName in self.core.settings.sbxObjects:
					oName += "_mp"
				else:
					continue
				oPos = oInfo[1].split(",")
				oPos = (float(oPos[0]),float(oPos[1]),float(oPos[2]))
				oRot = oInfo[2].split(",")
				oRot = (float(oRot[0]),float(oRot[1]),float(oRot[2]))
				objects.append([oName,oPos,oRot])
		if not self.core.checkObjectCount(1):
			p.sendMsg("OBJLIMITREACHED")
			return
		if objects:
			self.core.rcon_btnEndGroup(p, ['null'])
			self.core.rcon_btnStartGroup(p, ['null'])
			p.selectedGroup.load = len(objects)
			tPos = p.getTracerLocation()
			for o in objects:
				oName = o[0]
				oPos = (tPos[0] + o[1][0], tPos[1] + o[1][1], tPos[2] + o[1][2])
				oRot = o[2]
				self.core.cacheObject(oName,oPos,oRot,p)
				self.core.queueObject(oName,oPos,oRot)
	
	def chat_adminloadgroup(self, p, params):
		if p.level < 18: return
		if p.saveDelay:
			p.sendMsg("SAVEDELAY")
			return
		p.saveDelay = 10
		filename = " ".join(params)
		if filename.lower().find("nuke") != -1:
			p.sendMsg("Sorry, no nukes allowed")
			return
		pName = p.getName()
		pName = pName.split(" ")[-1]
		try:
			result = sbxloadGroup(pName,p.getProfileId(),filename)
		except:
			self.core.sendMsg("Rut Row 1")
			ExceptionOutput()
			p.saveDelay = 0
			return
		else:
			if result:
				if result.lower().find("error:") == -1:
					try:
						self.loadGroup(p, result)
					except:
						p.sendMsg("Rut Row 2")
						ExceptionOutput()
					else:
						p.saveDelay = self.core.settings.groupDupeDelay
				else:
					p.sendMsg(result)
			else:
				p.sendMsg("Unable to contact the Sandbox Network server.")