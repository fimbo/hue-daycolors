
from beautifulhue.api import Bridge

class Room
	def __init__(self, id):
        self.id = id  
        self.state = "off"

    def reportLamps(self, lamps):
    	self.lamps = lamps

    def apply(self, color):
    	for lamp in self.lamps:
    		lamp.apply(color)

    def loadGroups():
    	groups = bridge.group.get({'which':'all'})
    	Rooms[] rooms = []
		for group in groups["resource"]:
			config = getGroupConfig(group)
			rooms.add(new Room(group["id"], group, config))
		return rooms
				

class Lamp:
	def __init__(self, id):
        self.id = id  
        self.state = "off"

	def applyState(self, color, bridge):
		ressource = self.createRessource(color) # create builder
		ressource = setState(color)
		bridge.light.update(ressource)


	def createRessource(self, data) :
		return  {
		    'which': int(self.id),
		}


	def setState(self, resource, data):
		resource["state"] = data
		return resource