'''
Created on May 9, 2014

@author: Leon

Module for sticky lips, seal lips, blink, etc
'''

import pymel.core as pm

import utils.rigging as rt
reload(rt)

def addStickyToFRS():
    '''
    assume all FRS nodes are already named correctly
    
    '''
    lf_ctl = pm.PyNode('LT_corner_lip_pri_ctrl')
    rt_ctl = pm.PyNode('RT_corner_lip_pri_ctrl')
    jaw_ctl = pm.PyNode('CT_jaw_pri_ctrl')
    
    lf_pinch = pm.PyNode('LT_upper_pinch_lip_sticky_master')
    lf_sneer = pm.PyNode('LT_upper_sneer_lip_sticky_master')
    rt_pinch = pm.PyNode('RT_upper_pinch_lip_sticky_master')
    rt_sneer = pm.PyNode('RT_upper_sneer_lip_sticky_master')
    ct_stick = pm.PyNode('CT_upper_lip_bnd_sticky_master')
    
    for ctl in lf_ctl, rt_ctl:
        ctl.addAttr('sealAmount', k=True, dv=0, min=0, max=1)
        ctl.addAttr('sealHeight', k=True, dv=0.5, min=0, max=1)
        
    jaw_ctl.addAttr('autoSticky', k=True, dv=0, min=0, max=1)
    
    # connect sealHeights
    lf_ctl.sealHeight >> lf_pinch.midVal
    lf_ctl.sealHeight >> lf_sneer.midVal
    rt_ctl.sealHeight >> rt_pinch.midVal
    rt_ctl.sealHeight >> rt_sneer.midVal
    # for center, use average between both sides
    ct_avg_pma = pm.createNode('plusMinusAverage', n='CT_stickyLips_avg_pma')
    ct_avg_pma.operation.set(3)
    lf_ctl.sealHeight >> ct_avg_pma.input3D[0].i3x
    rt_ctl.sealHeight >> ct_avg_pma.input3D[1].i3x
    ct_avg_pma.output3D.o3x >> ct_stick.midVal
    
    # connect sealAmounts
    rt.connectSDK(lf_ctl.sealAmount, lf_pinch.stickAmount, {0:0, 0.3:1})
    rt.connectSDK(lf_ctl.sealAmount, lf_sneer.stickAmount, {0.3:0, 0.7:1})
    rt.connectSDK(rt_ctl.sealAmount, rt_pinch.stickAmount, {0:0, 0.3:1})
    rt.connectSDK(rt_ctl.sealAmount, rt_sneer.stickAmount, {0.3:0, 0.7:1})
    # for center, use average between both sides
    rt.connectSDK(lf_ctl.sealAmount, ct_avg_pma.input3D[0].i3y, {0.7:0, 1:1})
    rt.connectSDK(rt_ctl.sealAmount, ct_avg_pma.input3D[1].i3y, {0.7:0, 1:1})
    ct_avg_pma.output3D.o3y >> ct_stick.stickAmount

class Sticky():
    
    def __init__(self, name=None, up_bnd=None, low_bnd=None, center=None):
        '''
        name - Pass either String or None
        bnds - Pass either PyNodes or None
        '''
        sel = pm.ls(sl=True)
        
        if not up_bnd:
            up_bnd = sel[0]
        if not low_bnd:
            low_bnd = sel[1]
        if not center:
            center = sel[2]
        if not name:
            name = '_'.join(str(up_bnd).split('_')[:4]) + '_sticky'
            
        self.populateData(name, up_bnd, low_bnd, center)
        
        self.create()
        
    def create(self):
        '''
        '''
        # use group node as placeholder
        master = pm.group(em=True, name=self.name+'_master')
        master.addAttr('upVal', k=True, at='float', dv=0, min=0, max=1)
        master.addAttr('lowVal', k=True, at='float', dv=1, min=0, max=1)
        master.addAttr('midVal', k=True, at='float', dv=0.5, min=0, max=1)
        master.addAttr('radius', k=True, at='float', dv=self.radius)
        master.addAttr('rotateUpMult', k=True, at='float')
        master.addAttr('rotateLowMult', k=True, at='float')
        master.addAttr('stickAmount', k=True, at='float', dv=0, min=0, max=1)
        
        # use setRange to interpolate upVal and lowVal to midVal, driven by stickAmount
        setr = pm.createNode('setRange', n=self.name+'_setr')
        master.midVal >> setr.maxX
        master.midVal >> setr.maxY
        master.stickAmount >> setr.valueX
        master.stickAmount >> setr.valueY
        setr.minX.set(0)
        setr.oldMaxX.set(1)
        setr.oldMaxY.set(1)
        setr.minY.set(1)
        setr.outValueX >> master.upVal
        setr.outValueY >> master.lowVal
        
        master.upVal >> master.rotateUpMult
        master.lowVal >> master.rotateLowMult
        
        
        
        # up_ctg world pt
        up_ctg_pmm = pm.createNode('pointMatrixMult', n=self.name+'_up_ctg_pmm')
        self.up_ctg.worldMatrix[0] >> up_ctg_pmm.inMatrix
        # calculate offset
        up_pos = self.up_ctg.getTranslation(space='world')
        low_pos = self.low_ctg.getTranslation(space='world')
        vec = low_pos - up_pos
        center_pos_world = up_pos + vec * 0.45
        center_pos_world = pm.dt.Point(center_pos_world)
        up_ctg_inv_mat = self.up_ctg.getMatrix(worldSpace=True).inverse()
        up_offset = center_pos_world * up_ctg_inv_mat
        up_ctg_pmm.inPoint.set(up_offset)
        
        # low_ctg world pt
        low_ctg_pmm = pm.createNode('pointMatrixMult', n=self.name+'_low_ctg_pmm')
        self.low_ctg.worldMatrix[0] >> low_ctg_pmm.inMatrix
        center_pos_world = low_pos - vec * 0.45
        center_pos_world = pm.dt.Point(center_pos_world)
        low_ctg_inv_mat = self.low_ctg.getMatrix(worldSpace=True).inverse()
        low_offset = center_pos_world * low_ctg_inv_mat
        low_ctg_pmm.inPoint.set(low_offset)    
        
        # arc direction vector
        vp = pm.createNode('vectorProduct', n=self.name+'_arcDirection_vp')
        self.up_ctg.worldMatrix[0] >> vp.matrix
        vp.operation.set(3)
        vp.input1.set(1,0,0)
        
        # 2-pt-circular-arc
        arc = pm.createNode('makeTwoPointCircularArc', n=self.name+'_arc')
        up_ctg_pmm.output >> arc.point1
        low_ctg_pmm.output >> arc.point2
        master.radius >> arc.radius
        vp.output >> arc.directionVector
        
        # UPPER motion path
        up_mp = pm.createNode('motionPath', n=self.name+'_upper_mp')
        arc.outputCurve >> up_mp.geometryPath
        self.up_ctg.worldMatrix[0] >> up_mp.worldUpMatrix
        master.upVal >> up_mp.uValue
        up_mp.frontAxis.set(1)
        up_mp.upAxis.set(2)
        up_mp.inverseFront.set(True)
        up_mp.worldUpType.set(2)
        up_mp.worldUpVector.set(0,0,1)
        up_mp.fractionMode.set(True)
        
        # compose matrix for UPPER sticky xfo
        up_cm = pm.createNode('composeMatrix', n=self.name+'_upper_cm')
        up_mp.allCoordinates >> up_cm.inputTranslate
        up_mp.rotate >> up_cm.inputRotate
        
        # create sticky grp for UPPER_CTG
        up_sticky = pm.group(em=True, n=self.name+'_upper_sticky_grp')
        self.up_ctg | up_sticky
        pm.makeIdentity(up_sticky, t=True, r=True, s=True, a=False)
        up_sticky | self.up_ctl
        
        # multiply matrix into sticky grp space
        up_mm = pm.createNode('multMatrix', n=self.name+'_upper_mm')
        up_cm.outputMatrix >> up_mm.matrixIn[0]
        up_sticky.parentInverseMatrix >> up_mm.matrixIn[1]
        
        # decompose matrix
        up_dm = pm.createNode('decomposeMatrix', n=self.name+'_upper_dm')
        up_mm.matrixSum >> up_dm.inputMatrix
        
        # remember translate offset using PMA
        up_tr_pma = pm.createNode('plusMinusAverage', n=self.name+'_upper_tr_pma')
        up_dm.outputTranslate >> up_tr_pma.input3D[0]
        up_tr_pma.input3D[1].set(-1 * up_offset)
         
        # remember rotation offset using PMA
        up_pma = pm.createNode('plusMinusAverage', n=self.name+'_upper_pma')
        up_dm.outputRotate >> up_pma.input3D[0]
        up_pma.input3D[1].set(-up_dm.outputRotateX.get(), -up_dm.outputRotateY.get(), -up_dm.outputRotateZ.get())
        
        # modulate rotations by a multiplier
        up_rot_md = pm.createNode('multiplyDivide', n=self.name+'_up_rot_md')
        up_pma.output3D >> up_rot_md.input1
        master.rotateUpMult >> up_rot_md.input2X
        master.rotateUpMult >> up_rot_md.input2Y
        master.rotateUpMult >> up_rot_md.input2Z
        
        # connect into sticky grp
        up_tr_pma.output3D >> up_sticky.translate
        # up_rot_md.output >> up_sticky.rotate # have to fix rotations
        
        # connect sticky values to bnd
        up_bnd_sticky = pm.group(em=True, n=self.name+'_upper_sticky_bnd')
        bnd_parent = self.up_bnd.getParent()
        bnd_parent  | up_bnd_sticky
        pm.makeIdentity(up_bnd_sticky, t=True, r=True, s=True, a=False)
        up_bnd_sticky | self.up_bnd
        up_sticky.translate >> up_bnd_sticky.translate
        up_sticky.rotate >> up_bnd_sticky.rotate
        
        # LOWER motion path
        low_mp = pm.createNode('motionPath', n=self.name+'_lower_mp')
        arc.outputCurve >> low_mp.geometryPath
        self.low_ctg.worldMatrix[0] >> low_mp.worldUpMatrix
        master.lowVal >> low_mp.uValue
        low_mp.frontAxis.set(1)
        low_mp.upAxis.set(2)
        low_mp.inverseFront.set(True)
        low_mp.worldUpType.set(2)
        low_mp.worldUpVector.set(0,0,1)
        low_mp.fractionMode.set(True)
        
        # compose matrix for LOWER sticky xfo
        low_cm = pm.createNode('composeMatrix', n=self.name+'_lower_cm')
        low_mp.allCoordinates >> low_cm.inputTranslate
        low_mp.rotate >> low_cm.inputRotate
        
        # create sticky grp for LOWER_CTG
        low_sticky = pm.group(em=True, n=self.name+'_lower_sticky_grp')
        self.low_ctg | low_sticky
        pm.makeIdentity(low_sticky, t=True, r=True, s=True, a=False)
        low_sticky | self.low_ctl
        
        # multiply matrix into sticky grp space
        low_mm = pm.createNode('multMatrix', n=self.name+'_lower_mm')
        low_cm.outputMatrix >> low_mm.matrixIn[0]
        low_sticky.parentInverseMatrix >> low_mm.matrixIn[1]
        
        # decompose matrix
        low_dm = pm.createNode('decomposeMatrix', n=self.name+'_lower_dm')
        low_mm.matrixSum >> low_dm.inputMatrix
        
        # remember translate offset using PMA
        low_tr_pma = pm.createNode('plusMinusAverage', n=self.name+'_lower_tr_pma')
        low_dm.outputTranslate >> low_tr_pma.input3D[0]
        low_tr_pma.input3D[1].set(-1 * low_offset)
         
        # remember rotation offset using PMA
        low_pma = pm.createNode('plusMinusAverage', n=self.name+'_lower_pma')
        low_dm.outputRotate >> low_pma.input3D[0]
        low_pma.input3D[1].set(-low_dm.outputRotateX.get(), -low_dm.outputRotateY.get(), -low_dm.outputRotateZ.get())
        
        # modulate rotations by a multiplier
        low_rot_md = pm.createNode('multiplyDivide', n=self.name+'_low_rot_md')
        low_pma.output3D >> low_rot_md.input1
        master.rotateLowMult >> low_rot_md.input2X # actually needs to be reversed!
        master.rotateLowMult >> low_rot_md.input2Y
        master.rotateLowMult >> low_rot_md.input2Z
        
        # connect into sticky grp
        low_tr_pma.output3D >> low_sticky.translate
        # low_rot_md.output >> low_sticky.rotate # have to fix rotations
        
        # connect sticky values to bnd
        low_bnd_sticky = pm.group(em=True, n=self.name+'_lower_sticky_bnd')
        bnd_parent = self.low_bnd.getParent()
        bnd_parent  | low_bnd_sticky
        pm.makeIdentity(low_bnd_sticky, t=True, r=True, s=True, a=False)
        low_bnd_sticky | self.low_bnd
        low_sticky.translate >> low_bnd_sticky.translate
        low_sticky.rotate >> low_bnd_sticky.rotate
        
        pm.select(master)

        
        

        
        
        
        
        
    
    
    def populateData(self, name, up_bnd, low_bnd, center):
        '''
        '''
        self.name = name
        self.up_bnd = up_bnd
        self.low_bnd = low_bnd
        
        self.up_ctg = pm.PyNode(str(up_bnd).replace('_bnd', '_ctrl_ctg'))
        self.up_ctl = pm.PyNode(str(up_bnd).replace('_bnd', '_ctrl'))
        self.low_ctg = pm.PyNode(str(low_bnd).replace('_bnd', '_ctrl_ctg'))
        self.low_ctl = pm.PyNode(str(low_bnd).replace('_bnd', '_ctrl'))
        
        start_pos = up_bnd.getTranslation(space='world')
        center_pos = center.getTranslation(space='world')
        self.radius = (start_pos - center_pos).length()
        
        
    def test(self):
        '''
        '''
        print self.up_bnd
        print self.low_bnd
        print self.up_ctg
        print self.low_ctg
        print self.name