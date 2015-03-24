__author__ = 'f.forti'

import maya.cmds as cmd
import copy
import utilities as ut

class BoundingBox(object):

	def __init__(self, **kwargs):

		self.min = None
		self.max = None
		self.volume = None

		keys = kwargs.keys()
		if "extract" in keys:
			mayabb = cmd.exactWorldBoundingBox(kwargs["extract"])
			self.min = mayabb[0:3]
			self.max = mayabb[3:6]
			self.dimension = 3
		elif "min" in keys and "max" in keys:
			self.min = kwargs["min"]
			self.max = kwargs["max"]
			self.dimension = self.checkDimension([kwargs["min"], kwargs["max"]])
		elif "set" in keys:
			self.computeBoundingBox(kwargs["set"])
		else:
			raise ut.constructionError(self.__name__)

	@staticmethod
	def checkDimension(arr):
		dimension = len(arr[0])
		if dimension < 2:
			raise Exception("i punti devono avere almeno due dimensioni")
		for p in arr:
			if len(p) != dimension:
				raise Exception(" tutti i punti devono avere la stessa dimensione")
		return dimension

	def computeBoundingBox(self, points):
		self.dimension = self.checkDimension(points)
		if len(points) < 2:
			raise Exception("l'array deve contenere almeno due punti")
		self.min = []
		self.max = []
		for i in range(self.dimension):
			sortedComp = sorted(map(lambda point: point[i], points))
			self.min.append(sortedComp[0])
			self.max.append(sortedComp[-1])
		return [self.min, self.max]


	def retrieveVertex(self):
		vertex = []
		if self.dimension == 1:
			vertex.append([self.min[0]])
			vertex.append([self.max[0]])
		if self.dimension == 2:
			vertex.append([self.min[0], self.min[1]])
			vertex.append([self.max[0], self.min[1]])
			vertex.append([self.min[0], self.max[1]])
			vertex.append([self.max[0], self.max[1]])
		return vertex

	def subDimension(self, l):
		self.volume = None
		self.dimension -= 1
		self.min.pop(l)
		self.max.pop(l)

	def addDimension(self, l, addMin, addMax):
		self.volume = None
		self.dimension += 1
		self.min.insert(l, addMin)
		self.max.insert(l, addMax)

	def collision(self, other):
		b = 1
		for d in range(self.dimension):
			if self.min[d] < other.max[d]:
				if self.max[d] > other.min[d]:
					b &= 1
				else:
					b &= 0
			else:
				b &= 0
		return b

	def draw(self):
		if self.dimension == 1:
			self.mayaBB = cmd.curve( p=[(self.min[0], 0, 0), (self.max[0], 0, 0)] )
		if self.dimension == 2:
			width = self.__len__(0)
			depth = self.__len__(1)
			self.mayaBB = cmd.polyPlane( w=width, h=depth, n="BB2D_0")
			cmd.move(self.min[0]+width/2, 0, self.min[1]+depth/2, self.mayaBB, absolute=True)
		elif self.dimension == 3:
			width = self.__len__(0)
			height = self.__len__(1)
			depth = self.__len__(2)
			self.mayaBB = cmd.polyCube(w=width, h=height, d=depth, n="BB_0")
			cmd.move(self.min[0]+width/2, self.min[1]+height/2, self.min[2]+depth/2, self.mayaBB, absolute=True)

	def __len__(self, l=None):
		if l is not None:
			if type(l) is list:
				if len(l) < self.dimension:
					area = 1
					for d in l:
						area *= self.__len__(d)
					return area
				else:
					return self.__len__()
			return abs(self.max[l] - self.min[l])
		else:
			self.volume = 1
			for d in range(self.dimension):
				self.volume *= self.__len__(d)
			return self.volume

	def __lt__(self, other):
		return self.__len__() < other.__len__()

	def __gt__(self, other):
		return self.__len__() > other.__len__()

	def getLMax(self, between=None):

		if between:
			lengths = [(d, self.__len__(d)) for d in between]
			return max(lengths, key=lambda x: x[1])[0]

		lengths = [self.__len__(d) for d in self.dimension]
		return max(xrange(self.dimension), key=lengths.__getitem__)

	def __str__(self):
		if self.volume:
			return "[ BB with volume: %f ]" % (self.volume)

		return "[ BB with min: %s and max: %s ]" % (self.min, self.max)

	def divide(self, value, l):
		if value <= 1:
			return [self]
		value = int(value)
		length = float(self.__len__(l))/value
		bbs = []
		for i in range(value):
			divMin = copy.copy(self.min)
			divMin[l] = self.min[l]+i*length
			divMax = copy.copy(self.max)
			divMax[l] = self.min[l]+(i+1)*length
			bbs.append(BoundingBox(
				min=divMin,
				max=divMax
			))
		return bbs

	def __div__(self, value):
		l = self.getLMax()
		return self.divide(value, l)