import time
import json
from beautifulhue.api import Bridge
from pprint import pprint

def readConfiguration():
	print "reading configuration"
	with open("config.json", "r") as configfile:
		config = json.load(configfile)
	return config

def run():
	while (True):
		print "checking rooms"
		groups = bridge.group.get({'which':'all'})
		for group in groups["resource"]:
			config = getGroupConfig(group)
			if(config):
				checkGroup(group, config)

		time.sleep(2)

def checkGroup(group, groupConfig):
	colorString = getTargetColor(groupConfig, time.time())
	color = translateColorString(colorString)
	print "checking group " + group["name"] + " to be " + colorString;

	if group["state"]["any_on"] == "False":
		print "lights are off"
		return

	for lightNb in group["lights"]:
		checkLight(lightNb, color)


def checkLight(lightNb, color):
	resource = {'which': int(lightNb)}
	light = bridge.light.get(resource)
	state = light["resource"]["state"];
	if color != { "bri": state["bri"], "ct":state["ct"]} :
		resource = {
		    'which': int(lightNb),
		    'data':{'state': color}
		}
		
		print "setting light {} to {}".format(lightNb,color)
		bridge.light.update(resource)

def getGroupConfig(group):
	groupname = group["name"]
	for roomconfig in  config["rooms"]:
		if roomconfig["name"] == group["name"]:
			return roomconfig

def getTargetColor(groupConfig, now):
	color = groupConfig["default-color"];
	for span in groupConfig["spans"]:
		if isBetween(now, time.strptime(span["from"],"%H:%M"), time.strptime(span["to"],"%H:%M")):
			color = span["color"]
	return color

def translateColorString(colorString):
	return config["colors"][colorString]

def isBetween(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end

def isUserDefined():
	return config["user"] != ""

def connect():
	if not isUserDefined():
		print "please press the button on your hue bridge"

	while not isUserDefined():
		#read auth
		time.sleep(1)

	print "using user " + config["user"]

def adjustColors():
	pass


config = readConfiguration()
pprint(config)
connect()
bridge = Bridge(device={'ip':config["host"]}, user={"name":config["user"]})
run()