import maya.cmds as cmd
import maya.OpenMaya as om


# Per tutta la lunghezza della curva (da 0 a 100%)
for incr in xrange(0,100):
    
    # calcola il valore tra 0.0 e 1.0
    val = incr/100.0
    
    # preleva il punto sulla curva associato al valore indicato
    point = cmd.pointOnCurve('curve1', pr=val, p=True)
    
    # sposta il locator "controllore" nel punto trovato sulla curva
    cmd.move( point[0], point[1], point[2], 'locator1')
    
    # preleva la posizione del locator "controllato" sul piano
    position = cmd.xform('locator2', query=True, translation=True)
    #tmpCube = cmd.polyCube(sx=1, sy=1, sz=1, w=1, h=1, d=1)
    #cmd.move( position[0], position[1], position[2], tmpCube[0])
    
    # crea un locator nel punto individuato
    cmd.spaceLocator(position=position)


# preleva la matrice di trasformazione dal locator indicato
mlist = cmd.xform('locator2', query=True, matrix=True)

mat = om.MMatrix()

# converti la matrice trovata in una matrice MMatrix (nativa OpenMaya)
om.MScriptUtil.createMatrixFromList(mlist, mat)

# Converti la matrice in una matrice di trasformazione
tmat = om.MTransformationMatrix(mat)

# Estrapola la componente di traslazione da questa matrice
tvec = tmat.translation(om.MSpace.kObject)

# stampa le componenti individualmente
print tvec[0]
print tvec[1]
print tvec[2]