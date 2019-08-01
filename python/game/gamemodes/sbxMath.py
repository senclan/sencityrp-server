#******************************************************************************
# Name: Sandbox Math Functions
# Author: Elton "Elxx" Muuga (http://elxx.net) et al.
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************
# "rect" and "polar" functions courtesy of William Park
# http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html

import math

def normalizeRotation(c):
	newCoords = []
	for a in c:
		if a > 180.0:
			a = -180.0 + (a - 180.0)
		if a < -180.0:
			a = 180.0 - (-a - 180.0)
		newCoords.append(a)
	return (newCoords[0],newCoords[1],newCoords[2])

def getVectoredPosition(pPos, distance, pRot, pCamRot):
	from math import pi
	#Calculate the height using a triangle
	p = pCamRot[1] #Pitch of the player's cam
	a = 90.0 - abs(p)
	p = pi * p / 180.0
	a = pi * a / 180.0
	sVz = (distance * math.sin(p))/math.sin(a)
	#convert from crazy-ass BF2 values to polar coordinate values
	new_pRot = -(pRot[0] + pCamRot[0]) + 90.0
	sVx,sVy = rect(distance,new_pRot,1) #Convert vector of [spawnDistance] with heading of cam rotation to x,y values
	sPos = (pPos[0] + sVx, pPos[1] - sVz, pPos[2] + sVy)
	return sPos

def rect(r, w, deg=0): # radian if deg=0; degree if deg=1
	from math import cos, sin, pi
	if deg:
		w = pi * w / 180.0
	return r * cos(w), r * sin(w)

def polar(x, y, deg=0): # radian if deg=0; degree if deg=1
	from math import hypot, atan2, pi
	if deg:
		return hypot(x, y), 180.0 * atan2(y, x) / pi
	else:
		return hypot(x, y), atan2(y, x)

def get2dDistance(x, y):
	return math.sqrt(math.pow(y[0] - x[0],2), math.pow(y[1] - x[1],2))

def get2dRotation(x, y, rot):
	#print "x=" + str(x) + ",y=" + str(y)
	polars = polar(x, y, 1)
	#print "polar1 = " + str(polars)
	polars = (polars[0],polars[1] + rot)
	#print "polar2 = " + str(polars)
	return rect(polars[0],polars[1],1)

def getVectorDistance(pos1, pos2):
	diffVec = [0.0, 0.0, 0.0]
	diffVec[0] = math.fabs(pos1[0] - pos2[0])
	diffVec[1] = math.fabs(pos1[1] - pos2[1])
	diffVec[2] = math.fabs(pos1[2] - pos2[2])
	return math.sqrt(diffVec[0] * diffVec[0] + diffVec[1] * diffVec[1] + diffVec[2] * diffVec[2])

def roundToNearest(num, nearest):
	x = num % nearest
	if x > (nearest / 2):
		return num + (nearest - x)
	else:
		return num - x

def cosineInterpolate(y1,y2,mu):
	mu2 = (1 - math.cos(mu * math.pi)) / 2
	return y1 * (1 - mu2) + y2 * mu2

def cubicInterpolate(y0,y1,y2,y3,mu):
	mu2 = mu * mu
	a0 = y3 - y2 - y0 + y1
	a1 = y0 - y1 - a0
	a2 = y2 - y0
	a3 = y1
	return a0 * mu * mu2 + a1 * mu2 + a2 * mu + a3