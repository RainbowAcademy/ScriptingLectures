__author__ = 'a.paoletti'

import maya.cmds as cmd
import os
import sys
sys.path.append("C://Users//a.paoletti//Desktop//MY//CORSOSCRIPTING - DISPLACE_GEOTIFF//gdalwin32-1.6//bin")
import colorsys


def getTexture():
	"""

	:rtype : String
	:return : Nome della texture applicata al canale color del lambert
	"""
	sel = cmd.ls(sl=True)
	print '--------- Selection is: ' + sel[0] + ' ---------'
	selMesh = cmd.listRelatives(sel, s=True)
	print '----- Shape: ' + selMesh[0]
	selSG = cmd.listConnections(selMesh[0], t='shadingEngine')
	print '----- Shading group: ' + selSG[0]
	selMat = cmd.listConnections(selSG[0], t='lambert')
	print '----- Material: ' + selMat[0]
	selTexture = cmd.listConnections(selMat[0]+'.color')
	print '--------- La texture e\': ' + selTexture[0] + ' ---------'
	return selTexture[0]


def testColorAtPoint():
	# per testare questa funzione seleziona la mesh nel suo intero in object mode
	txtName = getTexture()
	colors = cmd.colorAtPoint(txtName, o='RGB', su=16, sv=16, mu=0.0, mv=0.0, xu=0.5, xv=0.5)
	print colors


def clamp(my_value, min_value, max_value):
	return max(min(my_value, max_value), min_value)


def colorToElevation(r, g, b):
	"""
	Data una terna RGB, ritorna il valore dell'altezza interpretando l'immagine
	come mappa fisica

	:param r: red component between 0 and 1
	:param g: green component between 0 and 1
	:param b: blue component between 0 and 1
	:return: Float che rappresenta l'elevazione del punto
	"""
	hsvColor = colorsys.rgb_to_hsv(r, g, b)
	h = hsvColor[0]
	s = hsvColor[1]
	v = hsvColor[2]

	base = 5
	elevation = 0
	# print "H--- " + str(h) + "S--- " + str(s) + "V--- " + str(v)
	# if v > 0.5:
	tmp = clamp((0.23-h), 0, 1)  # 0 blue 1 rosso
	elevation = pow(base, tmp+1) - base

	return elevation


def testGeoSampler():
	sel = cmd.ls(sl=True)
	if len(sel) == 0:
		raise Exception("Selezionare il piano!")
	print '--------- Selection is: ' + sel[0] + ' ---------'
	cmd.selectMode(component=True)
	cmd.select(sel[0]+'.vtx[:]')

	cmd.polyGeoSampler(cs=False, cdo=False, dg=False, ac=True, bf=False)

	vtxNumber = len(cmd.getAttr(sel[0]+'.vtx[:]'))
	# cmd.softSelect(sse=1, ssd=1)
	for i in range(0, vtxNumber):
		v = sel[0]+'.vtx[%d]' % i
		cmd.select(v, r=True)
		vColor = cmd.polyColorPerVertex(query=True, r=True, g=True, b=True)
		r = vColor[0]
		g = vColor[1]
		b = vColor[2]

		h = colorToElevation(r, g, b)
		cmd.move(h, y=True, r=True)

	cmd.softSelect(sse=0)
	cmd.selectMode(object=True)


def readGeoTiff(filepath):
	try:
		from osgeo import gdal
	except:
		raise Exception("Cannot find gdal modules")
	# enable GDAL exceptions
	gdal.UseException()

	ds = gdal.Open(filepath)
	band = ds.GetRasterBand(1)
	elevation = band.ReadAsArray()

	print elevation.shape
	print elevation


def readGeoTiff2(filepath):
	import gdal
	import gdalconst

	# coordinates to get pixel values for
	xValues = [122588.008]
	yValues = [484475.146]

	# set directory
	os.chdir(r'D:\\temp\\AHN2_060')

	# register all of the drivers
	gdal.AllRegister()
	# open the image
	ds = gdal.Open(filepath, GA_ReadOnly)

	if ds is None:
		print 'Could not open image'
		sys.exit(1)

	# get image size
	rows = ds.RasterYSize
	cols = ds.RasterXSize
	bands = ds.RasterCount

	# get georeference info
	transform = ds.GetGeoTransform()
	xOrigin = transform[0]
	yOrigin = transform[3]
	pixelWidth = transform[1]
	pixelHeight = transform[5]

	# loop through the coordinates
	for xValue, yValue in zip(xValues, yValues):
		# get x,y
		x = xValue
		y = yValue

		# compute pixel offset
		xOffset = int((x - xOrigin) / pixelWidth)
		yOffset = int((y - yOrigin) / pixelHeight)
		# create a string to print out
		s = "%s %s %s %s " % (x, y, xOffset, yOffset)

		# loop through the bands
		for i in xrange(1, bands):
			band = ds.GetRasterBand(i)  # 1-based index
			# read data and add the value to the string
			data = band.ReadAsArray(xOffset, yOffset, 1, 1)
			value = data[0, 0]
			s = "%s%s " % (s, value)
		# print out the data string
		print s
		# figure out how long the script took to run
