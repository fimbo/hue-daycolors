
from beautifulhue.api import Bridge
from enum import Enum

def connect(config):
	user = config["user"]
	if not user:
		print "please press the button on your hue bridge"
		while not config["user"]:
			#read auth
			time.sleep(1)

	print "using user " + user
	return Bridge(device={'ip':config["host"]}, user={"name":user})


def readRooms(bridge):
		groups = bridge.group.get({'which':'all'})
		rooms = []
		for group in groups["resource"]:
			room = Room(group["id"], group)
			rooms.append(room)
			lamps = []
			for lightNb in group["lights"]:
				lamp = Lamp(lightNb)
				lamp.readState(bridge)
				lamps.append(lamp)
				room.lamps = lamps
		return rooms


class Room:
	def __init__(self, id, group):
 		self.id = id
		self.group = group
		self.lamps = []

	def readState(self, bridge):
		self.group = bridge.group.get({'which':self.id})["resource"]
		if not self.isOn():
			for lamp in self.lamps:
				lamp.status = LampState.UNKNOWN
		
	def getName(self):
		return self.group["name"]

	def isOn(self):
		return self.group and self.group["state"]["any_on"] == True

	def __str__(self):
		return self.getName()


class LampState(Enum):
	UNKNOWN=0
	ADJUSTED=1
	MANUALLY_CHANGED=2

class Lamp:
	def __init__(self, id):
		self.id = id  
		self.state = "unknown"
		self.status = LampState.UNKNOWN

	def readState(self, bridge):
		resource = self.createRessource()
		light = bridge.light.get(resource)
		self.state = light["resource"]["state"]
		if not self.isOn():
			self.status = LampState.UNKNOWN

	def isOn(self):
		return self.state["on"]

	def meets(self, expectedState):
		matching = True
		for property in expectedState:
			if not self.state[property] or not self.state[property] == expectedState[property]:
				matching = False
				print "> property {} should be {} but is {}".format(property,expectedState[property], self.state[property])

		if matching:
			if not self.status == LampState.ADJUSTED:
				self.status = LampState.ADJUSTED
		else:
			if self.status == LampState.ADJUSTED:
				self.status = LampState.MANUALLY_CHANGED

		return matching

	def applyState(self, bridge, state):
		ressource = self.createRessource() # create builder
		ressource = self.setRessourceState(ressource, state)
		print "> updating {}".format(ressource)
		bridge.light.update(ressource)
		self.readState(bridge)

	def createRessource(self):
		return  {
			'which': int(self.id),
		}

	def setRessourceState(self, ressource, data):
		if not ressource.has_key("data"):
			ressource["data"] = {}
		ressource["data"]["state"] = data
		return ressource
	
	def __str__(self):
		return "{} ({})".format(self.id, self.status) 



