import time
import json
from beautifulhue.api import Bridge
import hue
from hue import Room, Lamp, LampState
import sys
import logging

def createLogger():
	logger = logging.getLogger('hue-daycolors')
	logger.setLevel(logging.DEBUG)

	fh = logging.FileHandler('log.log')
	fh.setLevel(logging.DEBUG)

	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)

	logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

def readConfiguration():
	filename = sys.argv[1]
	logger.info("reading configuration from {}".format(filename))
	with open(filename, "r") as configfile:
		config = json.load(configfile)
	return config

def run(bridge):
	rooms = hue.readRooms(bridge, logStatus)
	logger.info("start polling")
	while (True):
		for room in rooms:
			logger.debug(u"checking room {}".format(room.getName()))
			room.readState(bridge)
			if room.isOn():
				logger.debug("> lights are on")
				timestamp = time.time()
				targetProfile = getTargetProfile(room.getName(), timestamp)

				if not targetProfile:
					logger.debug(u"> no targetState defined for room {} at {}".format(room, timestamp))
				else:
					targetState = translateProfileString(targetProfile)
					logger.debug(u"> expecting state of {} to be {}".format(room, targetState))
					for lamp in room.lamps:
						lamp.targetState = targetState
						logger.debug("> checking lamp {}".format(lamp))
						lamp.readState(bridge)
						if not lamp.isOn:
							logger.debug("> lamp is off")
							return
						if lamp._status != LampState.manuallyChangedStatus and lamp._status != LampState.adjustedStatus:
							logger.info("> adjusting")
							lamp.applyState(bridge, targetState)
		time.sleep(2)


def getTargetProfile(groupname, time):
	homeconfig = getRoomConfig("Home")
	roomconfig = getRoomConfig(groupname)
	profile = None

	if homeconfig:
		profile = takeIfDefined(homeconfig["default-profile"], profile)

	if roomconfig:
		profile = takeIfDefined(roomconfig["default-profile"], profile)

	if homeconfig:
		profile = takeIfDefined(getProfileAtTime(homeconfig, time), profile)

	if roomconfig:
		profile = takeIfDefined(getProfileAtTime(roomconfig, time), profile)

	return profile

def takeIfDefined(candidate, default):
	if candidate:
		return candidate
	return default

def getProfileAtTime(groupConfig, timestamp):
	profile = None
	for span in groupConfig["spans"]:
		if isBetween(timestamp, time.strptime(span["from"],"%H:%M"), time.strptime(span["to"],"%H:%M")):
			profile = span["profile"]  # take last one

	return profile

def getRoomConfig(groupname):
	for roomconfig in config["rooms"]:
		if roomconfig["name"] == groupname:
			return roomconfig;


def translateProfileString(profile):
	return config["profiles"][profile]

def isBetween(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end

def isUserDefined():
	return config["user"] != ""

def logStatus(lamp, status):
	logger.info("Lamp {} changed status to {}".format(lamp, status))


logger = createLogger()
config = readConfiguration()
logger.info("using configuration:\n {}".format(config))
user, bridge = hue.connect(config["host"], config["user"])
logger.info("using user {}".format(user))
run(bridge)