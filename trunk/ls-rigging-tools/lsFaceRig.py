import maya.cmds as mc
import lsRigTools as rt
import lsCreateNode as cn
import lsMotionSystems as ms
reload(ms)
reload(cn)
reload(rt)

#===============================================================================
# Eyeball collide with eyelids
#===============================================================================
def addJntsOnSurfIntersection(surf1, surf2, jntsNum):
    '''
    Places jnts along intersection curve between surf1 and surf2
    naming convention based on surf1
    '''
    
    # intersect surfaces
    crvGrp, intNode = mc.intersect(surf1, surf2, fs=True, ch=True, o=True, cos=False)[:2]
    intNode = mc.rename(intNode, surf1+'_ints')
    crvGrp = mc.rename(crvGrp, surf1+'_ints_crv_grp')
    crv = mc.listRelatives(crvGrp, c=True)[0]
    crv = mc.rename(crv, surf1+'_ints_crv')
    
    # rebuild curve to jntNum spans
    rbdCrv, rbdNode = mc.rebuildCurve(crv, ch=True, o=True, rpo=False, spans=jntsNum, rt=0, kr=2, n=crv+'_rbd_crv')
    rbdNode = mc.rename(rbdNode, crv+'_rbd')
    
    # offset curve to control size of eye hole
    offsetCrv, offsetNode = mc.offsetCurve(rbdCrv, ch=True, distance=0, o=True, ugn=0, n=crv+'_offset_crv')
    offsetNode = mc.rename(offsetNode, crv+'_offset')
    
    locs = []
    locName = '_'.join(surf1.split('_')[:2])
    # attach locators to intersection curve
    for locId in range(jntsNum):
        loc = mc.spaceLocator(n=locName+'_loc_%d' % locId)[0]
        rt.attachToMotionPath(offsetCrv, locId, loc, fm=False)
        mc.setAttr(loc+'.localScale', 0.05, 0.05, 0.05)
        locs.append(loc)
        
    # normal constraint to surf1
    for loc in locs:
        mc.normalConstraint(surf1, loc, aim=(1,0,0))
    
    jnts = []
    # add joints under locators
    for loc in locs:
        mc.select(cl=True)
        jnt = mc.joint(n=loc.replace('_loc_','_jnt_'))
        rt.parentSnap(jnt, loc)
        mc.setAttr(jnt+'.jointOrient', 0,0,0)
        jnts.append(jnt)
        
    # groups
    grp = mc.group(crvGrp, offsetCrv, rbdCrv, locs, n=surf1+'_intersect_loc_grp')
    
    # create offset attribute
    mc.addAttr(grp, ln='collideOffset', at='double', dv=0, k=True)
    offsetPlug = cn.create_multDoubleLinear(grp+'.collideOffset', -1)
    mc.connectAttr(offsetPlug, offsetNode+'.distance', f=True)
    
    # connect debug
    rt.connectVisibilityToggle(offsetCrv, grp, 'offsetCrv', False)
    rt.connectVisibilityToggle(rbdCrv, grp, 'rebuildCrv', False)
    rt.connectVisibilityToggle(crvGrp, grp, 'intersectCrv', False)
    rt.connectVisibilityToggle(locs, grp, 'crvLocs', False)
    rt.connectVisibilityToggle(jnts, grp, 'crvJnts', False)
    

#===============================================================================
# EYELIDS
#===============================================================================

def rigEyeLids():
    '''
    needs cleanup.
    '''
    # names are currently hard-coded...
    # add locators to curve
    targetCurve = 'RT_eyeLidsShaper_crv_0'
    startParam = 0
    endParam = 19
    
    for param in range(startParam, endParam+1):
        loc = mc.spaceLocator(n=targetCurve.replace('_crv_','_loc_').replace('_0','_%d'%param))[0]
        poci = mc.createNode('pointOnCurveInfo', n=targetCurve.replace('_crv_','_poci_').replace('_0','_%d'%param))
        mc.connectAttr(targetCurve+'.worldSpace', poci+'.inputCurve', f=True)
        mc.connectAttr(poci+'.result.position', loc+'.translate', f=True)
        mc.setAttr(poci+'.parameter', param)
        mc.setAttr(loc+'.localScale', 0.02, 0.02, 0.02)
        
    # create joints from eyePivot to crvLocs
    targetCurve = 'RT_eyeLidsShaper_crv_0'
    startParam = 0
    endParam = 19
    eyePivot = mc.xform('RT_eyeRot_pivot_loc_0', q=1, ws=1, t=1)
    
    jnts = []
    for param in range(startParam, endParam+1):
        mc.select(cl=True)
        baseJnt = mc.joint(n=targetCurve.replace('_crv_','_jnt_').replace('_0','_%d'%param), p=eyePivot)
        endPivot = mc.xform(targetCurve.replace('_crv_','_loc_').replace('_0','_%d'%param), q=1, ws=1, t=1)
        endJnt = mc.joint(n=targetCurve.replace('_crv_','_endJnt_').replace('_0','_%d'%param), p=endPivot)
        jnts.append(baseJnt)
        jnts.append(endJnt)
    
    mc.select(jnts)
    mc.setAttr('.radius', *[0.1] * len(jnts))
    
    # create ikHandle on crvLocs
    selBaseJnts = mc.ls(sl=True)
    
    for eachJnt in selBaseJnts:
        endJnt = eachJnt.replace('_jnt_', '_endJnt_')
        targetLoc = eachJnt.replace('_jnt_', '_loc_')
        ikhandle = mc.ikHandle(n=eachJnt.replace('_jnt_', '_hdl_'), sj=eachJnt, ee=endJnt, solver='ikSCsolver')
        mc.parent(ikhandle[0], targetLoc)
        
    #===============================================================================
    # Eyelid control attributes - to be hooked up to UI
    #===============================================================================
    mc.addAttr(ln='lfUpLid', at='double', dv=0, min=-3, max=1, k=1)
    mc.addAttr(ln='lfLowLid', at='double', dv=0, min=-1, max=3, k=1)
    mc.addAttr(ln='rtUpLid', at='double', dv=0, min=-3, max=1, k=1)
    mc.addAttr(ln='rtLowLid', at='double', dv=0, min=-1, max=3, k=1)
    
    mc.addAttr(ln='lfUpLidRot', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='lfLowLidRot', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtUpLidRot', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtLowLidRot', at='double', dv=0, min=-1, max=1, k=1)
    
    mc.addAttr(ln='lfBlink', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtBlink', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='lfBias', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtBias', at='double', dv=0, min=-1, max=1, k=1)
    
    mc.addAttr(ln='lfInCorner', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='lfOutCorner', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtInCorner', at='double', dv=0, min=-1, max=1, k=1)
    mc.addAttr(ln='rtOutCorner', at='double', dv=0, min=-1, max=1, k=1)
    
def rigEyes():
    # eyeBall - eyeLids intersections
    surf1 = 'LT_eyeBallIntersect_srf_0'
    surf2 = 'CT_eyeBallHeadIntersecter_srf_0'
    jntsNum = 20
    addJntsOnSurfIntersection(surf1, surf2, jntsNum)
    
    # eyeBall pop controls
    baseTangentMP = ms.addTangentMPTo('LT_eyeBase_mPt', 'LT_eyeTip_mPt', 'z', default=0.2, reverse=False)
    tipTangentMP = ms.addTangentMPTo('LT_eyeTip_mPt', 'LT_eyeBase_mPt', 'z', default=0.2, reverse=True)
    midMP = ms.addMidMP(baseTangentMP, tipTangentMP, 'LT_eyeBase_mPt', 'LT_eyeTip_mPt', (0,0,1), (0,1,0), 'LT_mid_mPt')
    crv = ms.createSplineMPs(('LT_eyeBase_mPt', baseTangentMP, midMP, tipTangentMP, 'LT_eyeTip_mPt'), 8, 'LT_eyeSpine', (0,3,0))
    
    baseTangentMP = ms.addTangentMPTo('RT_eyeBase_mPt', 'RT_eyeTip_mPt', 'z', default=0.2, reverse=False)
    tipTangentMP = ms.addTangentMPTo('RT_eyeTip_mPt', 'RT_eyeBase_mPt', 'z', default=0.2, reverse=True)
    midMP = ms.addMidMP(baseTangentMP, tipTangentMP, 'RT_eyeBase_mPt', 'RT_eyeTip_mPt', (0,0,1), (0,1,0), 'RT_mid_mPt')
    crv = ms.createSplineMPs(('RT_eyeBase_mPt', baseTangentMP, midMP, tipTangentMP, 'RT_eyeTip_mPt'), 8, 'RT_eyeSpine', (0,3,0))