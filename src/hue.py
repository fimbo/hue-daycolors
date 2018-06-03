
from beautifulhue.api import Bridge
from enum import Enum

def connect(host, user):
	if not user:
		print "please press the button on your hue bridge"
		time.sleep(2)

	bridge = Bridge(device={'ip':host}, user={"name":user})
	return (user, bridge)


def readRooms(bridge, lampStatusListener):
		groups = bridge.group.get({'which':'all'})
		rooms = []
		for group in groups["resource"]:
			room = Room(group["id"], group)
			rooms.append(room)
			lamps = []
			for lightNb in group["lights"]:
				lamp = Lamp(lightNb, lampStatusListener)
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
				lamp.setStatus(LampState.initialStatus)
		
	def getName(self):
		return self.group["name"]

	def isOn(self):
		return self.group and self.group["state"]["any_on"] == True

	def __str__(self):
		return self.getName()


class Lamp:
	def __init__(self, id, statusListener):
		self.id = id  
		self.state = "unknown"
		self.targetState = "unknown"
		self.statusListener = statusListener
		self._status = LampState.initialStatus;

	def readState(self, bridge):
		resource = self.createRessource()
		light = bridge.light.get(resource)
		self.state = light["resource"]["state"]
		self._status(self)

	def isOn(self):
		return self.state["on"]

	def getUnmetProperties(self, expectedState):
		misses = []
		for property in expectedState:
			if not self.state[property] == expectedState[property]:
				misses = misses + [{ 'property': property, 'expected' :expectedState[property], 'actual' : self.state[property]}]
		return misses

	def meetsTarget(self):
		return self.meets(self.targetState)

	def meets(self, expectedState):
		return len(self.getUnmetProperties(expectedState)) == 0

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
		if self._status:
		  statusName = self._status.__name__
		else:
		  statusName = "n/a"

		return "{} ({})".format(self.id, statusName) 

	def setStatus(self, status):
		if self._status == status:
			return
		self.statusListener(self, status.__name__)
		self._status = status

######### lampstates #########

class LampState:

	@staticmethod
	def initialStatus(lamp):
		if not lamp.isOn():
			return

		if lamp.targetState == "unknown":
			return

		if lamp.meetsTarget():
			lamp.setStatus(LampState.adjustedStatus)

	@staticmethod
	def adjustedStatus(lamp):
		if not lamp.isOn():
			lamp.setStatus(LampState.initialStatus)

		if lamp.meetsTarget():
			return
		else:
			lamp.setStatus(LampState.manuallyChangedStatus)

	@staticmethod
	def manuallyChangedStatus(lamp):
		if not lamp.isOn():
			lamp.setStatus(LampState.initialStatus)

		

