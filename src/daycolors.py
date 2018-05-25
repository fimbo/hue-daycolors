import time
import json
from beautifulhue.api import Bridge
from pprint import pprint
import hue
from hue import Room, Lamp, LampState
import sys

def readConfiguration():
	print "reading configuraton"
	for str in sys.argv:
		print str
	filename = sys.argv[1]
	with open(filename, "r") as configfile:
		config = json.load(configfile)
	return config

def run(bridge):
	rooms = hue.readRooms(bridge)
	while (True):
		for room in rooms:
			print u"checking room {}".format(room.getName())
			room.readState(bridge)
			if room.isOn():
				print "> lights are on"
				groupConfig = getRoomConfig(room.getName())
				targetProfile = getTargetProfile(groupConfig, time.time())
				targetState = translateProfileString(targetProfile)
				print "> expecting state of {} to be {}".format(room, targetState)
				for lamp in room.lamps:
					lamp.readState(bridge)
					print "> checking lamp {}".format(lamp)
					if not lamp.isOn:
						print "> lamp is off"
						return
					if not lamp.meets(targetState):
						if lamp.status == LampState.MANUALLY_CHANGED:
							print "> state is changed manually, leaving as is"
						else:
							print "> adjusting"
							lamp.applyState(bridge, targetState)
		time.sleep(2)

def getRoomConfig(groupname):
	for roomconfig in config["rooms"]:
		if roomconfig["name"] == groupname:
			return roomconfig

def getTargetProfile(groupConfig, now):
	profile = groupConfig["default-profile"];
	for span in groupConfig["spans"]:
		if isBetween(now, time.strptime(span["from"],"%H:%M"), time.strptime(span["to"],"%H:%M")):
			profile = span["profile"]
	return profile

def translateProfileString(profile):
	return config["profiles"][profile]

def isBetween(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end

def isUserDefined():
	return config["user"] != ""

config = readConfiguration()
pprint(config)
bridge = hue.connect(config)
run(bridge)