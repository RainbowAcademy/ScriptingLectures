import maya.cmds as cmd
import random as r
import math

blockSize = [15, 15]
buildingSize = [10, 5, 10]

buildingList = []

def createBuilding(position, blockSize, buildingSize):
    building = cmd.polyCube(sx=1, sy=1, sz=1, w=buildingSize[0], h=buildingSize[1], d=buildingSize[2])
    buildingBlock = cmd.polyPlane(sx=1, sy=1, w=blockSize[0], h=blockSize[1])
    #lamp = cmd.pointLight(decayRate=2, intensity=50, useRayTraceShadows=True)
    #cmd.move(6,2,0, lamp)
    
    buildingRig = cmd.circle(center=[0,0,0], normal=[0,1,0], radius=10, n='buildingRig')
    cmd.addAttr(buildingRig, longName='buildingHeight', shortName='bh', defaultValue=1, minValue=1, maxValue=20, attributeType='long')
    
    bbox = cmd.exactWorldBoundingBox(building)
    cmd.xform(building, piv=[0, bbox[1], 0], ws=True)
    cmd.move(0, -bbox[1], 0, building)
    cmd.makeIdentity(building, apply=True, t=True, r=True, s=True)
    cmd.delete(building, constructionHistory=True)
    cmd.delete(buildingBlock, constructionHistory=True)
    cmd.delete(buildingRig, constructionHistory=True)
    
    buildingGroup = cmd.group(em=True, name='building_1')
    buildingRig_group = cmd.parent(buildingRig[0], buildingGroup)
    cmd.parent(building[0], buildingGroup)
    cmd.parent(buildingBlock[0], buildingGroup)
    #cmd.parent(lamp, buildingGroup)
    
    cmd.connectAttr(buildingRig_group[0]+'.bh', building[0]+'.scaleY')
    x = position[0] * blockSize[0]
    y = position[1] * blockSize[1]
    cmd.move(x, 0, y, buildingGroup)
    height = math.floor(r.uniform(1, 10))
    cmd.setAttr(buildingRig_group[0]+'.bh', height)
    cmd.setAttr(buildingRig_group[0]+'.visibility', False)    
    return buildingGroup


def deleteBuildings(buildingList):
    counter = 0
    for building in buildingList:
        cmd.delete(building)
    del buildingList


cityBuildingsGroup = cmd.group( em=True, name='cityBuildings')

for x in range(-20, 20):
    for y in range(-20, 20):
        position = [x, y]
        buildingList.append( createBuilding(position, blockSize, buildingSize) )

for building in buildingList:
    cmd.parent(building, cityBuildingsGroup)

extController = cmd.circle(center=[0,0,0], normal=[0,1,0], radius=200, n='extController')
intController = cmd.circle(center=[0,0,0], normal=[0,1,0], radius=100, n='intController')

controls = cmd.group(em=True, name='Controls')

cmd.parent(extController, controls)
cmd.parent(intController, controls)
cmd.parent(controls, cityBuildingsGroup)
cmd.move(0,-10,0, controls)

deleteBuildings(buildingList)

for building in buildingList:
    rig = cmd.listRelatives(building, allDescendents=True, f=True)
    rndVal = math.floor(r.uniform(0,1)*2+1)
    cmd.setAttr(rig[1]+'.bh', rndVal)

center = cmd.getAttr('extController.translate')[0]
radius = cmd.getAttr('makeNurbCircle1.radius')
for building in buildingList:
    position = cmd.getAttr(building+'.translate')[0]
    len = pow(center[0]-position[0],2) + 0 + pow(center[2]-position[2],2)
    if len < pow(radius,2):
        rig = cmd.listRelatives(building, allDescendents=True, f=True)
        rndVal = math.floor(r.random()*3+(r.random()*3+1))
        cmd.setAttr(rig[1]+'.bh', rndVal)

center = cmd.getAttr('intController.translate')[0]
radius = cmd.getAttr('makeNurbCircle2.radius')
for building in buildingList:
    position = cmd.getAttr(building+'.translate')[0]
    len = pow(center[0]-position[0],2) + 0 + pow(center[2]-position[2],2)
    if len < pow(radius,2):
        rig = cmd.listRelatives(building, allDescendents=True, f=True)
        rndVal = math.floor(r.random()*10+(r.random()*10+1))
        cmd.setAttr(rig[1]+'.bh', rndVal)