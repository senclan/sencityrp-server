#******************************************************************************
# Name: Sandbox Error Handling Functions
# Authors: King of Camelot
#          Elton "Elxx" Muuga
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************
# Huge, huge thanks to King of Camelot @ the BF2 Technical Information Wiki.
# I've used this error handling system countless times in many projects, it 
# undoubtedly kicks ass.
# http://bf2tech.org/index.php/Cookbook:How_To_Implement_Better_Error_Catching

import sys
import host
import inspect
import re

def readline(filename, lineno):
	filen = re.sub('\\\\', '/', filename)
	file = open(filen, 'rU')
	lines = file.readlines()
	file.close()
	linen = lineno - 1
	line = re.sub('\s+', ' ', lines[linen])
	return line

def ExceptionOutput():
	sys.stderr.write("\n" + "Exception Occured: " + str(sys.exc_info()[0]) + "\n")
	sys.stderr.write("Value: " + str(sys.exc_info()[1]) + "\n")
	sys.stderr.write("Line:" + str(readline(inspect.getfile(sys.exc_info()[2]),
							sys.exc_info()[2].tb_lineno)) + "\n")
	sys.stderr.write("Line #: " + str(sys.exc_info()[2].tb_lineno) + "\n")
	sys.stderr.write("File: " + str(inspect.getfile(sys.exc_info()[2])) + "\n" + "\n")
	#host.rcon_invoke("game.sayAll \"Exception Caught: " + str(sys.exc_info()[1]) + "\"")
	#host.rcon_invoke("game.sayAll \"Line " + str(sys.exc_info()[2].tb_lineno) + "\"")