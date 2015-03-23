__author__ = 'f.forti'

import InternsGenerator.Room
reload(InternsGenerator.Room)
from InternsGenerator.Room import *
from utilities import *
import maya.cmds as cmd
import pseudoRandom as rand
reload(rand)
import copy

class HouseGenerator(object):

	def __init__(self):
		#tipi di camera in ordine di grandezza
		self.roomTypes = ["ingresso", "bagno", "letto", "cucina", "salone"]
		self.rooms = None

	def roomsOfType(self, type):
		for r in self.rooms:
			if r.type == type:
				yield r

	def libraryBySelection(self, type = None):
		if type is None:
			type = self.roomTypes[-1]
		interns = [Furniture(obj) for obj in cmd.ls(sl=True)]
		Room.loadLibrary(type, interns)
		#se le camere sono gia' state create fai il reload delle furniture
		if self.rooms is not None:
			for r in self.roomsOfType(type):
				r.reloadFurniture()

	def fill(self):
		if self.rooms is None:
			raise Exception("devi prima generare le stanze")
		for room in self.rooms:
			room.decorate()

	def createRooms(self, bb):
		#rapporto tra lati
		b = [ bb.__len__(0), bb.__len__(2)]
		h = bb.__len__(1)
		rapp = [h/b[0], h/b[1], b[0]/b[1]]
		dbg(rapp)
		thrH = 0.6
		thrB = 0.5
		self.rooms = []
		convex = rand.generateRandomConvex(4)
		# l'altezza e maggiore di una percetuale thrH della base
		if rapp[0] > thrH or rapp[1] > thrH:
			dbg("rapp[0] ", rapp[0])
			dbg("rapp[1] ", rapp[1])
			bbs = [bb]
			dbg("rapp[2] ", rapp[2])
			#se le due basi sono troppo differenti rispetto a una soglia thrB
			if rapp[2] > 1+thrB:
				bbs = bb.divide(rapp[2], 0)
			elif rapp[2] < 1-thrB:
				bbs = bb.divide(1/rapp[2], 2)
			for palace in bbs:
				newH = thrH * max(palace.__len__(0), palace.__len__(2))
				nHouse = int(round(h / newH))
				dbg(nHouse)
				floors = palace.divide(nHouse, 1)
				for floor in floors:
					floorRooms = self.subdiv(floor, convex)
					floorRooms = self.divideSelected(floorRooms, -2)
					#assegnamento dei tipi di stanza
					finalFloorRooms = [Room(self.roomTypes[i], floorRooms[i]) for i in range(len(floorRooms))]
					self.rooms.extend(finalFloorRooms)
		else:
			roomsBB = self.subdiv(bb, convex)
			roomsBB = self.divideSelected(roomsBB, -2)
			self.rooms = [Room(self.roomTypes[i], roomsBB[i]) for i in range(len(roomsBB))]

	def generate(self):
		boxe = cmd.ls(sl=True)
		if not len(boxe):
			raise Exception("non hai selezionato la stanza")

		bb = BoundingBox(extract=boxe)
		self.createRooms(bb)
		for r in self.rooms:
			r.draw()

	@staticmethod
	def divideSelected(floorRooms, id):
		lToDiv = floorRooms[id].getLMax([0, 2])
		dividedRooms = floorRooms[id].divide(2, lToDiv)
		dbg("divided ", dividedRooms)
		floorRooms.pop(id)
		floorRooms.extend(dividedRooms)
		return sorted(floorRooms)

	@staticmethod
	def subdiv(bb, convex):
		# points
		bb2d = copy.deepcopy(bb)
		#elimino la y dai calcoli
		bb2d.subDimension(1)
		vertex = bb2d.retrieveVertex()
		pivot = [
			convex[0]*vertex[0][0]+convex[1]*vertex[1][0]+convex[2]*vertex[2][0]+convex[3]*vertex[3][0],
			convex[0]*vertex[0][1]+convex[1]*vertex[1][1]+convex[2]*vertex[2][1]+convex[3]*vertex[3][1],
		]
		#cmd.polyCube(w=bb.max[0]-bb.min[0], h=bb.max[1]-bb.min[1], d=bb.max[2]-bb.min[2])
		if DEBUG:
			sphere = cmd.polySphere(r=1)
			cmd.move(pivot[0], 0, pivot[1], sphere, absolute=True, ws= True)
		rooms = sorted([
			BoundingBox(set=[vertex[0], pivot]), BoundingBox(set=[vertex[1], pivot]),
			BoundingBox(set=[vertex[2], pivot]), BoundingBox(set=[vertex[3], pivot])
		])
		for r in rooms:
			r.addDimension(1, bb.min[1], bb.max[1])
		return rooms