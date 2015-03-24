__author__ = 'f.forti'

import random as rand
from random import *

def generateRandomConvex(nConvex, type="central", deviation=0.2):
		convex = []
		for i in range(nConvex):
			if type == "central":
				gauss = min(max(abs(rand.gauss(0.5, deviation)), 0.05), 0.95)
				convex.append(gauss)
			elif type == "uniform":
				uniform = rand.uniform(0, 1)
				convex.append(uniform)

		summed = sum(convex)

		for i in range(nConvex):
			convex[i] = convex[i]/summed
		return convex