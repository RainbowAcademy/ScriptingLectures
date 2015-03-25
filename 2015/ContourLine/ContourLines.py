__author__ = 'a.paoletti'

import maya.cmds as cmd
import maya.OpenMaya as om


def checkClosed(curves):
	"""
	Check if curves are closed

	:param curves: curves to check
	:return: None
	"""
	for c in curves:
		state = cmd.getAttr(c + '.f')  # 0 Open, 1 Closed, 2 Periodic
		if state != 1 and state != 2:
			raise Exception('La curva \'' + c + '\' non e chiusa!')


def checkIntersection(curves):
	"""
	Check if any curve intersect each other

	:param curves: curves to check
	:return: None
	"""
	for c in curves:
		for i in range(0, len(curves)):
			if c != curves[i]:
				int_point = cmd.curveIntersect(c, curves[i])
				if int_point is not None:
					print 'La curva \'' + c + '\' si interseca con la curva \'' + curves[i] + '\''
					print 'Punto di intersezione: ' + int_point
					raise Exception('Curve di livello irregolari.')


def checkPlanar(curves):
	"""
	Check if curves are planar (they must have the same y value)

	:param curves: curves to check
	:return: None
	"""
	for i in range(1, len(curves)):
		t = cmd.listRelatives(curves[i], type='transform', p=True)
		t1 = cmd.listRelatives(curves[i-1], type='transform', p=True)
		t_y = cmd.getAttr(t[0] + '.translateY')
		t1_y = cmd.getAttr(t1[0] + '.translateY')
		if t_y != t1_y:
			raise Exception('La curva \'' + t[0] + '\' non e complanare con \'' + t1[0] + '\'')


def createShapeFromCurve(d, curve):
	"""
	Duplicate the curve and create a shape (with loft tool)

	:param d: distance between curve copy
	:param curve: curve that is used to create the shape
	:return: resulting shape from loft tool
	"""
	cmd.select(curve)
	copy1 = cmd.duplicate(st=True)
	cmd.move(d, y=True, r=True)
	copy2 = cmd.duplicate(st=True)
	cmd.move(-3*d, y=True, r=True)

	cmd.select(copy1)
	cmd.select(copy2, add=True)

	loft = cmd.loft(u=True, ss=3, po=1, rsn=True)
	cmd.delete(copy1, copy2)
	cmd.setAttr(loft[0] + ".visibility", 0)
	cmd.select(cl=True)
	return loft[0]


def displacePointsInsideMesh(plane, mesh, height, sse, ssd):
	"""
	Select vertices of plane that are inside mesh and displace those vertices
	(with amount height)

	:param plane: object to displace
	:param mesh: shape for select vertices to displace
	:param height: height of displacement
	:param sse: enable soft selection 0 False 1 True
	:param ssd: soft select distance
	:return: None
	"""
	cmd.selectMode(component=True)
	cmd.softSelect(sse=sse, ssd=ssd)

	vtxNumber = len(cmd.getAttr(plane+'.vtx[:]'))
	for i in range(0, vtxNumber):
		v = plane+'.vtx[%d]' % i
		cmd.select(v, r=True)
		vPosition = cmd.xform(v, query=True, translation=True, worldSpace=True)
		if test_if_inside_mesh(mesh, vPosition):
			cmd.move(height, y=True, r=True)

	cmd.softSelect(sse=0)
	cmd.selectMode(o=True)


def resetVertices():
	"""
	Reset vertices of selected plane at y=0 (local space)

	:return: None
	"""
	sel = cmd.ls(sl=True)
	if len(sel) == 0:
		raise Exception("Selezionare il piano!")
	cmd.selectMode(component=True)
	cmd.select(sel[0]+'.vtx[:]')
	cmd.move(0, y=True, ls=True)
	cmd.selectMode(o=True)


def testIfInsideCurve(point, curve, direction):
	p1 = point
	pTmp = (direction[0]*1000, direction[1]*1000, direction[2]*1000)
	p2 = (p1[0]+pTmp[0], p1[1]+pTmp[1], p1[2]+pTmp[2])
	segment = cmd.curve(p=[p1, p2], d=1)
	node = cmd.curveIntersect(segment, curve, ud=True, d=(0, 1, 0), ch=True)

	if node:
		intCurve1 = cmd.getAttr(node+'.parameter1')
		numOfIntersection = len(intCurve1[0])
	else:
		numOfIntersection = 0
		print 'Node e\' NoneType!'

	cmd.delete(segment)
	cmd.delete(node)
	return numOfIntersection % 2 == 1


def tmp():
	curves = cmd.ls(type='nurbsCurve')

	sel = cmd.ls(sl=True)
	if len(sel) == 0:
		raise Exception("Selezionare il piano!")
	print '--------- Selection is: ' + sel[0] + ' ---------'

	cmd.selectMode(component=True)
	count = 1
	for c in curves:
		vtxNumber = len(cmd.getAttr(sel[0]+'.vtx[:]'))
		for i in range(0, vtxNumber):
			v = sel[0]+'.vtx[%d]' % i
			vPosition = cmd.xform(v, query=True, translation=True, worldSpace=True)
			if testIfInsideCurve(vPosition, c, (1, 0, 0)):
				cmd.move(3, v, y=True, r=True)

		print "Terminato displacement livello " + str(count)
		count += 1

	cmd.selectMode(o=True)


def test_if_inside_mesh(msh, point=(0.0, 0.0, 0.0), direction=(0.0, 0.0, 1.0)):
	"""
	Finds any intersection of a ray starting at raySource and travelling
	in rayDirection with the mesh.

	:param msh: shape to intersect
	:param point: point to test if is inside the mesh
	:param direction: unit vector for raycasting
	:return: True if point is inside mesh (check
	"""
	sel = om.MSelectionList()
	dag = om.MDagPath()

	sel.add(msh)
	sel.getDagPath(0, dag)

	mesh = om.MFnMesh(dag)

	point = om.MFloatPoint(*point)
	direction = om.MFloatVector(*direction)
	farray = om.MFloatPointArray()

	# See docs here:
	# http://download.autodesk.com/us/maya/2011help/API/class_m_fn_mesh.html#4ce7d38f9201f33c48f49e6068d07c18
	mesh.allIntersections(
		point, direction,
		None, None,
		False, om.MSpace.kWorld,
		10000, False,
		None,  # replace none with a mesh look up accelerator if needed
		False,
		farray,
		None, None,
		None, None,
		None
	)
	return farray.length() % 2 == 1


def CL_Displace(height, iUseSoftSel=0, ssRadius=0):
	"""
	Main function to perform ContourLines Displace. Keep all curves in the scene
	and displace the selected plane depends on the shape of that curves.
	Curves must be drawn from bigger to smaller (lower displace to higher)

	:param height: height of displacement
	:param iUseSoftSel: use soft selection 0 False 1 True
	:param ssRadius: soft selection radius
	:return: None
	"""
	curves = cmd.ls(type='nurbsCurve')
	checkClosed(curves)
	checkPlanar(curves)
	checkIntersection(curves)

	sel = cmd.ls(sl=True)
	if len(sel) == 0:
		raise Exception("Selezionare il piano!")
	print '--------- Selection is: ' + sel[0] + ' ---------'

	i = 1
	for c in curves:
		shape = createShapeFromCurve(height*i, c)
		displacePointsInsideMesh(sel[0], shape, height, iUseSoftSel, ssRadius)
		cmd.delete(shape)
		print "Terminato displacement livello " + str(i)
		i += 1

	cmd.polyTriangulate(sel[0])


def displacePointsInsideMeshSM(plane, mesh, height, fRadius):
	"""
	Same function as displacePointsInsideMesh, but use soft modification
	instead of soft selection

	:param plane: object to displace
	:param mesh: shape for select vertices to displace
	:param height: height of displacement
	:param fRadius: soft modification falloff radius
	:return: None
	"""
	cmd.selectMode(component=True)

	vtxNumber = len(cmd.getAttr(plane+'.vtx[:]'))
	for i in range(0, vtxNumber):
		v = plane+'.vtx[%d]' % i
		vPosition = cmd.xform(v, query=True, translation=True, worldSpace=True)
		if test_if_inside_mesh(mesh, vPosition):
			cmd.select(v, add=True)

	cmd.softMod(rel=True, fas=True, fr=fRadius, fm=False)
	cmd.move(height, y=True, r=True)
	cmd.selectMode(o=True)


def CL_Displace_SM(height, fRadius=5):
	"""
	Same function as CL_Displace, but use displacePointsInsideMeshSM
	instead of displacePointsInsideMesh

	:param height: height of displacement
	:param fRadius: soft modification radius
	:return: None
	"""
	curves = cmd.ls(type='nurbsCurve')
	checkClosed(curves)
	checkPlanar(curves)
	checkIntersection(curves)

	sel = cmd.ls(sl=True)
	if len(sel) == 0:
		raise Exception("Selezionare il piano!")
	print '--------- Selection is: ' + sel[0] + ' ---------'

	i = 1
	for c in curves:
		shape = createShapeFromCurve(height*i, c)
		displacePointsInsideMeshSM(sel[0], shape, height, fRadius)
		cmd.delete(shape)
		print "Terminato displacement livello " + str(i)
		i += 1

	cmd.polyTriangulate(sel[0])


def CL_Displace_noShape(height, sse=0, ssd=0):
	curves = cmd.ls(type='nurbsCurve')
	checkClosed(curves)
	checkPlanar(curves)
	checkIntersection(curves)

	sel = cmd.ls(sl=True)
	if len(sel) == 0:
		raise Exception("Selezionare il piano!")
	print '--------- Selection is: ' + sel[0] + ' ---------'

	cmd.selectMode(component=True)
	cmd.softSelect(sse=sse, ssd=ssd)
	count = 1
	for c in curves:
		vtxNumber = len(cmd.getAttr(sel[0]+'.vtx[:]'))
		for i in range(0, vtxNumber):
			v = sel[0]+'.vtx[%d]' % i
			vPosition = cmd.xform(v, query=True, translation=True, worldSpace=True)
			if testIfInsideCurve(vPosition, c, (1, 0, 0)):
				cmd.move(height, v, y=True, r=True)

		print "Terminato displacement livello " + str(count)
		count += 1

	cmd.softSelect(sse=0)
	cmd.selectMode(o=True)
	cmd.polyTriangulate(sel[0])