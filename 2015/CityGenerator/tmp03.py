import maya.cmds as cmd

''' costruzione del palazzo '''
building = cmd.polyCube(sx=1, sy=1, sz=1, w=10, h=25, d=10, n='testBuilding')

''' costruzione del blocco di strada intorno al palazzo '''
buildingBlock = cmd.polyPlane(sx=1, sy=1, w=15, h=15, n='testBuildingBlock')

for o in [building, buildingBlock]:
    bbox = cmd.exactWorldBoundingBox(o)  # Preleva il bounding box dell'oggetto
    height = abs(bbox[1]) + abs(bbox[4])
    cmd.xform(o, piv=[0,bbox[1],0], ws=True)  # Sposta il pivot dell'oggetto alla sua base
    cmd.move(0, bbox[4], 0, o)  # sposta l'oggetto verso l'alto affinché il pivot sia a zero
    cmd.makeIdentity(o, apply=True, t=True, r=True, s=True)  # effettua il freeze transform
    cmd.delete(o, constructionHistory=True)  # cancella la construction history dell'oggetto
    
cmd.select( clear=True )  # pulisce la selezione in viewport