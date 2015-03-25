__author__ = 'f.forti'

"""example:

import InternsGenerator.Generator as g
import copy
reload(g)
sofa=g.Furniture("sofa", [0,2],1)
lamp=g.Furniture("lamp", [0,2],0,"light",1)
doors=g.Furniture.generate4SideFurniture("door", 0, "door", 1)
windows=g.Furniture.generate4SideFurniture("window",1,"window",1)
water=g.Furniture("water",[2], 1, "generic", 1)
guardrobes=g.Furniture.generate4SideFurniture("guardrobe", 0)
kitchen=g.Furniture("kitchen", [0], [0,1,0])
g.Room.library = { "ingresso" : [copy.copy(lamp),copy.copy(doors[2]),copy.copy(doors[3])], "bagno" : [copy.copy(lamp),copy.copy(doors[3]),copy.copy(windows[2]),water], "letto" : [copy.copy(lamp),copy.copy(doors[3]),copy.copy(windows[0]),copy.copy(windows[2]),copy.copy(guardrobes[1])], "cucina" :[copy.copy(lamp),copy.copy(doors[0]),copy.copy(windows[1]), copy.copy(windows[3]),kitchen], "salone" : [lamp,windows[0],windows[3],guardrobes[0],sofa] }
generator = g.HouseGenerator()
generator.generate()
generator.fill()

"""

import InternsGenerator.Room
reload(InternsGenerator.Room)
from InternsGenerator.Room import *
from utilities import *
import maya.cmds as cmd
import maya.mel as mel
import pseudoRandom as rand
reload(rand)
import copy

class HouseGenerator(object):

	def __init__(self):
		#tipi di camera in ordine di grandezza
		self.roomTypes = ["ingresso","bagno", "letto", "cucina", "salone"]
		self.rooms = None
		self.bb = None

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

	def createDoorsAndWindows(self):
		for room in self.rooms:
			if room.furniture is None:
				continue
			for f in room.furniture:
				if f.type == "door" or f.type == "window":
					eulerSet = {0, 1, 2}
					constraint = list((eulerSet - f.constraint) - {1})
					dbg("constraint ",constraint)
					move = [0, 0, 0]
					move[constraint[0]] = f.__len__(constraint[0])/2
					if f.bMin[constraint[0]]:
						move[constraint[0]] = - move[constraint[0]]
					dbg("move ", move)
					dbg("f first ",f)
					f.move(move, False)
					dbg("f after ",f)
					f.draw()
					for room2 in self.rooms:
						if room2.collision(f):
							room2.subtract(f)
					self.bb.subtract(f)
					f.undraw()

	def fill(self):
		if self.rooms is None:
			raise Exception("devi prima generare le stanze")
		for room in self.rooms:
			room.decorate()
			room.setLights()
		self.createDoorsAndWindows()


	def createRooms(self, convex):
		#rapporto tra lati
		bb = copy.deepcopy(self.bb)
		b = [bb.__len__(0), bb.__len__(2)]
		h = bb.__len__(1)
		rapp = [h/b[0], h/b[1], b[0]/b[1]]
		thrH = 0.3
		thrB = 0.5
		self.rooms = []
		# l'altezza e maggiore di una percetuale thrH della base
		if rapp[0] > thrH or rapp[1] > thrH:
			bbs = [bb]
			#se le due basi sono troppo differenti rispetto a una soglia thrB
			if rapp[2] > 1+thrB:
				bbs = bb.divide(rapp[2], 0)
			elif rapp[2] < 1-thrB:
				bbs = bb.divide(1/rapp[2], 2)
			for palace in bbs:
				newH = thrH * max(palace.__len__(0), palace.__len__(2))
				nHouse = int(round(h / newH))
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

	def randomGenerate(self):
		boxe = cmd.ls(sl=True)
		if not len(boxe):
			raise Exception("non hai selezionato la stanza")
		boxe = boxe[0]
		self.bb = BoundingBox(extract=boxe)
		convex = rand.generateRandomConvex(4)
		self.createRooms(convex)
		for r in self.rooms:
			r.draw()
			cmd.select(r.mayaBB, r=True)
			mel.eval('CenterPivot')
			cmd.makeIdentity(apply=True, t=1, r=1, s=1, n=2)
			cmd.scale(0.999, 0.999, 0.999)
			r.updateFromMayaBB()
			cmd.polyNormal(r.mayaBB, normalMode=0, userNormalMode=1, ch=0)


	def generate(self):
		boxe = cmd.ls(sl=True)
		if not len(boxe):
			raise Exception("non hai selezionato la stanza")
		boxe = boxe[0]
		self.bb = BoundingBox(extract=boxe)
		convex = [0.25, 0.25, 0.25, 0.25]
		self.createRooms(convex)
		for r in self.rooms:
			r.draw()
			cmd.select(r.mayaBB, r=True)
			mel.eval('CenterPivot')
			cmd.makeIdentity(apply=True, t=1, r=1, s=1, n=2)
			cmd.scale(0.97, 0.97, 0.97)
			r.updateFromMayaBB()
			cmd.polyNormal(r.mayaBB, normalMode=0, userNormalMode=1, ch=0)

	@staticmethod
	def divideSelected(floorRooms, id):
		lToDiv = floorRooms[id].getLMax([0, 2])
		dividedRooms = floorRooms[id].divide(2, lToDiv)
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

		rooms = sorted([
			BoundingBox(set=[vertex[0], pivot]), BoundingBox(set=[vertex[1], pivot]),
			BoundingBox(set=[vertex[2], pivot]), BoundingBox(set=[vertex[3], pivot])
		])
		for r in rooms:
			r.addDimension(1, bb.min[1], bb.max[1])
		return rooms