__author__ = 'f.forti'

import InternsGenerator.BoundingBox as bb
reload(bb)
from InternsGenerator.BoundingBox import *
from utilities import *
import maya.cmds as cmd
import pseudoRandom as rand
import copy

class Room(BoundingBox):

	#static variable of the class
	library = {}
	nMaxTentativi = 50
	scale = 5000000.0

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
			#dbg("la furniture per %s e' %s", type, self.furniture)
			dbg("furniture ", [f.mayaObj for f in self.furniture])
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

	@staticmethod
	def generateAlignedConvex(nConvex, align):
		convex = []
		for i in range(nConvex):
			if align == 0:
				convex.append(i/nConvex)
			elif align == 1:
				convex.append(0.5)
			else:
				convex.append(1-i/nConvex)
		summed = sum(convex)
		for i in range(nConvex):
			convex[i] = convex[i]/summed
		return convex

	def randomPoint(self, f):

		if f.align is None:
			convex = rand.generateRandomConvex(2**len(f.constraint), "uniform")
		else:
			convex = self.generateAlignedConvex(2**len(f.constraint), f.align)
		#elimino le dimensioni non necessarie (quelle che non stanno in f.constraint)

		SubRoom = copy.deepcopy(self)
		eulerSet = set([0, 1, 2])
		subdim = eulerSet - f.constraint

		#le dimensioni vengono tolte secondo un certo ordine
		orderDim = sorted(f.constraint)
		orderSubDim = sorted(subdim, reverse=True)
		for sub in orderSubDim:
			SubRoom.subDimension(sub)

		#mi ricavo i vertici interessati
		vertex = SubRoom.retrieveVertex()
		#generazione del punto random
		randomPoint = []

		for d in range(SubRoom.dimension):
			value = 0
			for i in range(len(vertex)):
				value += convex[i]*vertex[i][d]
			vertex.sort(key=lambda x: x[d])
			#offset basato sulla lunghezza della furiniture
			offset = f.__len__(orderDim[d])/2
			value = max(min(value, vertex[-1][d]-offset), vertex[0][d]+offset)
			randomPoint.append(value)

		#ripristino la dimensione del punto generato
		startPoint = [self.max, self.min]

		bMin = copy.copy(f.bMin)
		while None in bMin:
			bMin[bMin.index(None)] = rand.randint(0, 1)
		for d in subdim:
			#scelta del massimo o del minimo
			choice = bMin[d]
			offset = f.__len__(d)/2
			if choice == 0:
				#prendo il massimo
				offset = - offset
			randomPoint.insert(d, startPoint[choice][d]+offset)
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
			f.rotate()
		for f in self.furniture:
			tentativi = 0
			while self.furnitureCollision(f) and tentativi < self.__class__.nMaxTentativi:
				randomPoint = self.randomPoint(f)
				tentativi += 1
				f.move(randomPoint)
			if tentativi >= self.__class__.nMaxTentativi:
				f.deleteMayaObj()
				self.furniture.remove(f)

	def setLights(self):
		if self.furniture is None:
			dbg("%s non ha furniture ", self)
			return False
		for f in self.furniture:
			if f.type == "light":
				light = cmd.pointLight(rs=True, ss=True, i=len(f)/Room.scale, n=f.mayaObj+"_light")
				translation = list(cmd.getAttr(f.mayaObj+'.translate')[0])
				lmax = f.getLMax()
				translation[lmax] -= f.__len__(lmax)
				cmd.move(translation[0], translation[1], translation[2], light)



class Furniture(BoundingBox):

	types = ["door", "window", "light", "generic"]

	@classmethod
	def generate4SideFurniture(cls, mayaObj, hang=False, typ=None, align=None):
		Furnitures=[]
		constraint = set()
		if hang:
			constraint = {1}
		# X min
		Furnitures.append(cls(mayaObj, {0} | constraint, [1, 1, 1], typ, align, [0, 90, 0]))
		# X max
		Furnitures.append(cls(mayaObj, {0} | constraint, [0, 1, 0], typ, align, [0, 270, 0]))
		# z min
		Furnitures.append(cls(mayaObj, {2} | constraint, [1, 1, 1], typ, align))
		# z max
		Furnitures.append(cls(mayaObj, {2} | constraint, [0, 1, 0], typ, align, [0, 180, 0]))

		return Furnitures


	def __init__(self, mayaObj, constraint=None, bMin=None, typ=None, align=None, rotation=None):
		super(self.__class__, self).__init__(extract=mayaObj)
		print "mayaObj "+str(mayaObj)
		#set default value
		if bMin is None:
			bMin = [None, True, None]
		elif bMin == False:
			bMin = [False, False, False]
		elif bMin == True:
			bMin = [True, True, True]
		if constraint is None:
			constraint = [0]
		if typ is None:
			typ = self.__class__.types[-1]

		self.mayaObj = mayaObj
		self.rotation = rotation
		print "mayaObj "+str(mayaObj)
		if typ not in self.__class__.types:
			raise constructionError("non riconosco il tipo %s non e' uno tra %s" % (typ, self.__class__.types[-1]))
		self.type = typ
		self.align = align
		self.constraint = set(constraint)

		if type(bMin) is list:
			if len(bMin) != 3:
				raise constructionError("l'array bMin deve essere di lunghezza pari a 3 [bMinx,bMiny,bMinz]")
			self.bMin = bMin
		else:
			for i in range(3):
				self.bMin.append(rand.randint(0, 1))

	def copyMayaObj(self):
		self.mayaObj = cmd.duplicate(self.mayaObj)[0]

	def deleteMayaObj(self):
		cmd.delete(self.mayaObj)

	def updateFromMayaObj(self):
		if self.mayaObj is not None:
			super(self.__class__, self).__init__(extract=self.mayaObj)

	def __str__(self):
		BBstr = super(self.__class__, self).__str__()
		return " %s furniture with constraint %s and bMin %s and dimension %s " % (self.type, self.constraint, self.bMin, BBstr)

	def __lt__(self, other):
		volumeOrder = super(self.__class__, self).__lt__(other)
		typeOrder = self.__class__.types
		if self.type == other.type:
			return volumeOrder
		else:
			return typeOrder.index(self.type) < typeOrder.index(other.type)

	def __gt__(self, other):
		volumeOrder = super(self.__class__, self).__gt__(other)
		typeOrder = self.__class__.types
		if self.type == other.type:
			return volumeOrder
		else:
			return typeOrder.index(self.type) > typeOrder.index(other.type)

	def move(self, point, absolute=True):
		cmd.move(point[0], point[1], point[2], self.mayaObj, absolute=absolute, relative=not absolute, ws=True)
		self.updateFromMayaObj()

	def rotate(self):
		if self.rotation is not None:
			cmd.rotate(str(self.rotation[0])+"deg", str(self.rotation[1])+"deg", str(self.rotation[2])+"deg", self.mayaObj)

