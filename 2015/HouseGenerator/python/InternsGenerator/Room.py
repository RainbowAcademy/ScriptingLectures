__author__ = 'f.forti'


from InternsGenerator.BoundingBox import *
from utilities import *
import maya.cmds as cmd
import pseudoRandom as rand
import copy

class Room(BoundingBox):

	#static variable of the class
	library = {}
	nMaxTentativi = 10

	def __init__(self, type, BB=None, **kwargs):
		if BB is not None:
			super(self.__class__, self).__init__(min=BB.min, max=BB.max)
		else:
			super(self.__class__, self).__init__(**kwargs)
		self.type = type
		if "furniture" in kwargs.keys():
			self.furniture = sorted(kwargs["furniture"])
		elif type in self.__class__.library:
			self.furniture = sorted(self.__class__.library[type])
			dbg("la furniture per %s e' %s", type, self.furniture)
		else:
			dbg("la furniture per %s e' vuota", type)
			self.furniture = None

	def __str__(self):
		BBstr = super(self.__class__, self).__str__()
		return " %s room with %s " % (self.type, BBstr)

	@classmethod
	def loadLibrary(cls, type, objs):
		cls.library[type] = sorted(objs)

	def reloadFurniture(self):
		self.furniture = sorted(self.__class__.library[self.type])

	def randomPoint(self, f):
		convex = rand.generateRandomConvex(2**len(f.constraint), "uniform")
		#elimino le dimensioni non necessarie (quelle che non stano in f.constraint)
		SubRoom = copy.deepcopy(self)
		eulerSet = set([0, 1, 2])
		subdim = eulerSet - f.constraint
		resortedim = sorted(subdim, reverse=True)
		for sub in resortedim:
			SubRoom.subDimension(sub)
		#mi ricavo i vertici interessati
		dbg("SubRoom ", SubRoom)
		vertex = SubRoom.retrieveVertex()
		dbg("vertex ", vertex)
		dbg("convex ", convex)
		#generazione del punto random
		randomPoint = []
		for d in range(SubRoom.dimension):
			value = 0
			for i in range(len(vertex)):
				value += convex[i]*vertex[i][d]
			vertex = sorted(vertex, key=lambda x: x[d])
			#offset basato sulla lunghezza della furiniture
			offset = f.__len__(d)/2
			dbg("max %s e min %s ", self.max, self.min)
			dbg("vertex ", vertex)
			dbg("offset ", offset)
			dbg("max(min(%s, %s), %s)", value, vertex[-1][d]-offset, vertex[0][d]+offset)
			value = max(min(value, vertex[-1][d]-offset), vertex[0][d]+offset)
			randomPoint.append(value)
		#ripristino la dimensione del punto generato
		for d in subdim:
			if f.bMin is None:
				f.bMin = rand.randint(0, 1)
			startPoint = [self.max, self.min]
			offset = f.__len__(d)/2
			randomPoint.insert(d, startPoint[f.bMin][d]+offset)
		return randomPoint

	def furnitureCollision(self, f):
		for x in self.furniture:
			if x is not f:
				if f.collision(x):
					return 1
		return 0

	def decorate(self):
		if self.furniture is None:
			dbg("%s non ha furniture ", self)
			return False
		#il pivot della furniture viene considerato al centro di essa
		for f in self.furniture:
			randomPoint = self.randomPoint(f)
			#posizionamento della furniture
			f.copyMayaObj()
			f.move(randomPoint)
		for f in self.furniture:
			tentativi = 0
			while self.furnitureCollision(f) and tentativi < self.__class__.nMaxTentativi:
				randomPoint = self.randomPoint(f)
				tentativi += 1
				f.move(randomPoint)
			if tentativi > self.__class__.nMaxTentativi:
				f.deleteMayaObj()
				self.furniture.remove(f)


class Furniture(BoundingBox):

	def __init__(self, mayaObj, constraint=[0, 1], bMin = None, typ="generic"):
		super(self.__class__, self).__init__(extract=mayaObj)
		self.mayaObj = mayaObj
		self.type = typ
		self.bMin = bMin
		self.constraint = set(constraint)

	def copyMayaObj(self):
		self.mayaObj = cmd.duplicate(self.mayaObj)

	def deleteMayaObj(self):
		cmd.delete(self.mayaObj)

	def updateFromMayaObj(self):
		if self.mayaObj is not None:
			super(self.__class__, self).__init__(extract=self.mayaObj)

	def __str__(self):
		BBstr = super(self.__class__, self).__str__()
		return " %s furniture with %s " % (self.type, BBstr)

	def move(self, point):
		cmd.move(point[0], point[1], point[2], self.mayaObj, absolute=True, ws=True)
		self.updateFromMayaObj()

