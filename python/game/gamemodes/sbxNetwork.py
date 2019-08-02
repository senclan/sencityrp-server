#******************************************************************************
# Name: Sandbox Network Functions
# Authors: Elton "Elxx" Muuga (http://elxx.net)
#          Missleboy
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************

import socket

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

def saveGroup(name, pid, groupName, data):
	name = name.replace("&","")
	pid = int(pid)
	groupName = groupName.replace("&","")
	data = data.replace("&","")
	return http_post(host, 80, path+"sbx.saveGroup.php","name="+str(name)+"&pid="+str(pid)+"&groupName="+str(groupName)+"&data="+str(data))

def loadGroup(name, pid, groupName):
	name = name.replace("&","")
	pid = int(pid)
	groupName = groupName.replace("&","")
	return http_post(host, 80, path+"sbx.loadGroup.php","name="+str(name)+"&pid="+str(pid)+"&groupName="+str(groupName))