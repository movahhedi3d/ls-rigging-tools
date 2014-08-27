'''
Created on Dec 31, 2013

@author: Leon
'''

import time
import maya.cmds as mc
import pymel.core as pm
from maya.mel import eval as meval

mel = pm.language.mel

import cgm.lib.position as cgmPos

import uitypes
import rigger.modules.eye as eye
reload(uitypes)
reload(eye)
import rigger.modules.face as face
reload(face)
import utils.symmetry as sym
reload(sym)

import rigger.lib.context as context
reload(context)
import rigger.utils.weights as weights
reload(weights)

import rigger.modules.placementGrp as placementGrp
reload(placementGrp)

from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.importExport import XmlImporter

class newUI(pm.uitypes.Window):
    """
    """
    
    # constants 
    _TITLE = 'Face Rig System'
    _WINDOW = 'lsFRS_win'
    
    _LTPREFIX = 'LT_'
    _RTPREFIX = 'RT_'
    '''
    imageRefPath = 'C:/Users/Leon/Pictures/FRS/Images/'
    
    mesh = pm.PyNode('CT_face_geo')
    lf_eye = pm.PyNode('LT_eyeball_geo')
    rt_eye = pm.PyNode('RT_eyeball_geo')
    '''
    def __new__(cls, baseFilePath, placerMapping, indMapping, meshNames):
        '''
        delete old window and create new instance
        '''
        if pm.window(cls._WINDOW, exists=True):
            pm.deleteUI(cls._WINDOW)
            
        self = pm.window(cls._WINDOW, title=cls._TITLE, menuBar=True)

        return pm.uitypes.Window.__new__(cls, self)
    
    def __init__(self, baseFilePath, placerMapping, indMapping, meshNames):
        '''
        create UI and init vars
        '''
        self.imageRefPath = baseFilePath
        self.placerMapping = placerMapping
        self.indMapping = indMapping
        self.mesh = meshNames['face']
        self.lf_eye = meshNames['leftEye']
        self.rt_eye = meshNames['rightEye']
        
        with pm.menu(l='Options') as menuOptions:
            pm.menuItem(l='Refresh')
            pm.menuItem(l='Reset')
        
        with pm.menu(l='Help') as menuHelp:
            pm.menuItem(l='Documentation')
            pm.menuItem(l='About')
        
        with pm.tabLayout() as mainTab:
            
            with pm.columnLayout(adj=True) as geoSelectionLayout:
                pass
            
            with pm.columnLayout(adj=True) as jntPlacementLayout:
            
                with pm.verticalLayout(ratios=(1,10,1), spacing=10) as jntPlacementVertLayout:
                    
                    #self.chk_symmetry = pm.checkBox(l='Symmetry', v=True)
                    self.btn_startJntPlacement = pm.button(l='Start Joint Placement', c=pm.Callback(self.startJointPlacement))
                    
                    self.img_jntReference = pm.image(image=self.imageRefPath+'default.jpg')
                
                    with pm.rowLayout(numberOfColumns=3, adj=2) as jntRowLayout:
                        self.btn_jntScrollLt = pm.button(l='<<', w=40, en=False)
                        self.txt_jntCurrent = pm.text(label='Click "Start Joint Placement" above to begin.', align='center')
                        self.btn_jntScrollRt = pm.button(l='>>', w=40, c=pm.Callback(self.selectNextItem), en=False)
                '''        
                with pm.verticalLayout() as edgeLoopsVertLayout:

                    #pm.separator(style='in')
                        
                    #self.sel_eyeLoopLt = uitypes.Selector(l='Left Eye Loop', lw=100)
                    #self.sel_eyeLoopRt = uitypes.Selector(l='Right Eye Loop', lw=100)
                    self.int_eyeRigidLoops = pm.intSliderGrp(l='Eye Rigid Loops', field=True, cw3=(100,40,140),
                                                          min=1, max=12, fieldMaxValue=99, v=4)
                    self.int_eyeFalloffLoops = pm.intSliderGrp(l='Eye Falloff Loops', field=True, cw3=(100,40,140),
                                                            min=1, max=12, fieldMaxValue=99, v=4)
                    
                    #pm.separator(style='in')
                    
                    #self.int_lipLoop = uitypes.Selector(l='Lip Loop', lw=100)
                    self.int_lipRigidLoops = pm.intSliderGrp(l='Lip Rigid Loops', field=True, cw3=(100,40,140),
                                                          min=1, max=12, fieldMaxValue=99, v=4)
                    self.int_lipFalloffLoops = pm.intSliderGrp(l='Lip Falloff Loops', field=True, cw3=(100,40,140),
                                                            min=1, max=12, fieldMaxValue=99, v=4)
                '''    
                with pm.verticalLayout(spacing=10) as buildRigVertLayout:
                    self.btn_buildRig = pm.button(l='Build Rig', c=pm.Callback(self.buildRig), en=False)
                
            with pm.columnLayout(adj=True) as expressionsLayout:
                pass
                
        mainTab.setTabLabel((geoSelectionLayout,'Geometry'))
        mainTab.setTabLabel((jntPlacementLayout,'Joints'))
        mainTab.setTabLabel((expressionsLayout,'Expressions'))
        mainTab.setSelectTab(jntPlacementLayout)
        
        self.show()
        
        
    def startJointPlacement(self):
        '''
        '''
        self.btn_startJntPlacement.setLabel('Restart Joint Placement')
        self.btn_jntScrollRt.setEnable(True)
        
        self.placementGrp = pm.group(n='CT_placement_grp', em=True)
        self.placementGrp.addAttr('locScale', at='float', dv=1.0)
        self.placementGrp.locScale.set(cb=True)
        
        jntPlacementContext = context.FaceJointPlacementContext(self.mesh, self, self.placementGrp)
        jntPlacementContext.runContext()
        
    def selectNextItem(self):
        '''
        '''
        if self.txt_jntCurrent.getLabel() == 'Select mouth lips loop':
            
            self.txt_jntCurrent.setLabel('Select left eyelid loop')
            fullRefPath = self.imageRefPath + "LT_eyeLidLoop.jpg"
            pm.image(self.img_jntReference, image=fullRefPath, e=True)
            
            # assign selection to placement_grp attr
            sel = pm.ls(sl=True, fl=True)
            self.placementGrp.addAttr('mouthLipsLoop', dt='stringArray')
            self.placementGrp.attr('mouthLipsLoop').set(len(sel), *sel, type='stringArray')
            pm.select(cl=True)
            
            placementGrp.addMouthLoopPlacements(self.placementGrp)
            
        elif self.txt_jntCurrent.getLabel() == 'Select left eyelid loop':
            # READY!
            self.txt_jntCurrent.setLabel('Ready to Build!')
            fullRefPath = r"C:\Users\Leon\Pictures\FRS\Images\FRSRef_default.jpg"
            pm.image(self.img_jntReference, image=fullRefPath, e=True)
            self.btn_jntScrollRt.setEnable(False)
            self.btn_buildRig.setEnable(True)
            pm.setToolTo('selectSuperContext')
            
            # assign selection to placement_grp attr
            sel = pm.ls(sl=True, fl=True)
            self.placementGrp.addAttr('leftEyelidLoop', dt='stringArray')
            self.placementGrp.attr('leftEyelidLoop').set(len(sel), *sel, type='stringArray')
            
            placementGrp.addEyeLoopPlacements(self.placementGrp)
            
            placementGrp.addIndependentPlacers(self.placementGrp, self.indMapping)
            '''
            # create independent locs that can be adjusted
            # JAW
            pos = pm.PyNode('LT_up_jaw_pLoc').getRotatePivot(space='world')
            pos.x = 0
            placementLoc = pm.spaceLocator(n='CT_jaw_pLoc')   
            placementLoc.t.set(pos)
            # create attribute to tell FRS what type of bind this will be
            placementLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=2)
            self.placementGrp | placementLoc
            
            # NOSE
            pos = pm.PyNode('LT_up_crease_pLoc').getRotatePivot(space='world')
            pos.x = 0
            placementLoc = pm.spaceLocator(n='CT_noseMover_pLoc')   
            placementLoc.t.set(pos)
            # create attribute to tell FRS what type of bind this will be
            placementLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=2)
            self.placementGrp | placementLoc
            
            # MOUTH
            pos = (pm.PyNode('CT_philtrum_pLoc').getRotatePivot(space='world') +
                   pm.PyNode('CT_chin_pLoc').getRotatePivot(space='world')) / 2.0
            pos.x = 0
            placementLoc = pm.spaceLocator(n='CT_mouthMover_pLoc')   
            placementLoc.t.set(pos)
            # create attribute to tell FRS what type of bind this will be
            placementLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=2)
            self.placementGrp | placementLoc
            
            # EYE
            placementLoc = pm.spaceLocator(n='LT_eyeMover_pLoc')
            cgmPos.moveParentSnap(placementLoc.name(), self.lf_eye.name())
            placementLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=2)
            self.placementGrp | placementLoc
            
            placementLoc = pm.spaceLocator(n='RT_eyeMover_pLoc')
            cgmPos.moveParentSnap(placementLoc.name(), self.rt_eye.name())
            placementLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=2)
            self.placementGrp | placementLoc
            
            '''
            placementGrp.snapPlacementsToMesh(self.placementGrp)
            placementGrp.mirrorAllPlacements(self.placementGrp)
            placementGrp.orientAllPlacements(self.placementGrp)
            
            
    def buildRig(self):
        '''
        '''
        # create progress window
        
        # build controls
        
        # [2,9,16,21] is a hard-coded override for badly topologized Sorceress char
        # bndGrp = face.createBndsFromPlacement(self.placementGrp, self.mesh, [2,9,16,21])
        
        # [8,12,0,4] is the override for dachshund
        # bndGrp = face.createBndsFromPlacement(self.placementGrp, self.mesh, [8,12,0,4])
        
        # [5,21,16,11] is the override for junnie
        # bndGrp = face.createBndsFromPlacement(self.placementGrp, self.mesh, [5,21,16,11])
        
        bndGrp = face.createBndsFromPlacement(self.placementGrp, self.mesh)
        
        face.buildSecondaryControlSystem(self.placementGrp, bndGrp, self.mesh)
        
        priCtls = face.buildPrimaryControlSystem()
        
        perimeterGrp = face.addPerimeterBndSystem(self.mesh)
        
        pm.progressWindow(title='Build Deformation System', progress=0, max=4)
        pm.progressWindow(e=True, step=1, status='Bind skinClusters...') # 1
        
        mll = face.createSkinLayers(self.mesh)
        face.smoothSkinLayers(mll)
        
        pm.progressWindow(e=True, step=1, status='Adapt motion systems...') # 6
        # set primary ctl weights
        allWeights = {u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.5, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.666, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.5, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rx': 0.8, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ry': 0.8, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rz': 0.8, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_rz': 0.1, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.333, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.333, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.333, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.666, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tx': 0.3, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ty': 0.3, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tz': 0.3, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.333, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.333, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.333, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_rz': 0.25, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_rx': 0.25, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_ry': 0.25, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.2, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.2, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.2, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tx': 0.55, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ty': 0.55, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tz': 0.55, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.666, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rz': 0.55, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_sz': 1.0, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_sx': 1.0, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_sy': 1.0, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tz': 0.3, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.5, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.666, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_sx': 0.05, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_sy': 0.05, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_sz': 0.05, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_ty': 1.0, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_tx': 1.0, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_tz': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tx': 0.3, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_tx': 0.05, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ry': 0.2, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.5, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.1, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.333, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_sy': 0.05, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_sx': 0.05, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_sz': 0.05, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_tz': 0.1, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.5, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.5, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.5, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.333, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sz': 0.1, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.05, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sx': 0.1, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sy': 0.1, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ry': 1.0, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tz': 0.333, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ty': 0.333, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tx': 0.333, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sz': 0.55, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sx': 1.0, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_ry': 0.8, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sy': 1.0, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_ry': 0.1, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.5, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.333, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.666, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ry': 0.55, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_ry': 0.05, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.666, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.666, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ry': 0.333, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ty': 0.3, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_ty': 0.15, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_tx': 0.15, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_tz': 0.15, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ry': 0.1, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rx': 0.1, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_sz': 0.4, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rz': 0.1, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tz': 1.0, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.95, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_rz': 1.0, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_ry': 1.0, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_rx': 1.0, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.88, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.1, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.1, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.1, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.15, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.1, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rz': 0.15, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sy': 1.0, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.1, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sz': 0.3, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sy': 0.3, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sx': 0.3, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_sy': 0.05, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.1, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ry': 1.0, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ry': 0.15, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rx': 1.0, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.666, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.666, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.666, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rz': 0.8, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.05, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tz': 1.0, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.05, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rz': 1.0, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.15, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_ty': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_tx': 1.0, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ry': 0.3, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_tz': 1.0, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.5, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_tz': 0.2, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_ty': 0.2, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_tx': 0.2, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.2, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.333, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.2, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.2, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.95, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.95, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.95, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_ry': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_rx': 1.0, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ry': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_rz': 1.0, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_rz': 0.05, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.666, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.666, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.666, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_sx': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_sy': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_sz': 1.0, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_tx': 0.88, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.5, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_ry': 0.05, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_tx': 0.88, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_ty': 0.05, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ty': 1.0, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.1, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_sz': 0.05, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.666, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tx': 0.8, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_sx': 0.05, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_ry': 0.2, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_rx': 0.2, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.5, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_rz': 0.2, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tx': 0.8, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ty': 0.333, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_ty': 0.05, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_tx': 0.05, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_tz': 0.05, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.5, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.5, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.5, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.15, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sy': 0.15, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.15, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.15, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_ry': 1.0, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_rx': 1.0, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.15, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_rz': 1.0, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.5, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.5, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sx': 1.0, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.5, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ty': 0.8, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.1, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.666, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.666, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rz': 0.55, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sz': 1.0, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.666, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.666, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.666, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sz': 0.2, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.05, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.666, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.95, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sx': 0.8, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.95, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_sy': 0.8, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_sx': 0.8, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.666, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_sz': 0.8, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.1, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.1, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.1, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.1, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sz': 1.0, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.666, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sx': 1.0, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sy': 1.0, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sx': 0.88, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ty': 0.15, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rz': 0.3, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.1, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sz': 0.8, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sy': 0.8, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sx': 0.8, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.22, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.333, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.333, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rz': 0.2, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sx': 1.0, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rx': 0.2, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ry': 0.2, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rz': 1.0, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ry': 1.0, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sy': 1.0, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rx': 1.0, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tz': 0.8, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_ty': 0.05, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_rx': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tx': 0.15, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_ry': 1.0, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.1, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_tx': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_rx': 1.0, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 1.0, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 1.0, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_tz': 0.2, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.666, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.88, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.666, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.5, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sy': 0.2, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sy': 0.8, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_rz': 1.0, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_tz': 1.0, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_ty': 1.0, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_tx': 1.0, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_rz': 0.25, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sz': 1.0, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_rx': 0.25, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_ry': 0.25, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_sx': 0.05, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_sy': 0.05, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_sz': 0.05, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_ry': 0.88, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_ty': 0.88, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sz': 0.8, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.1, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sx': 1.0, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.1, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_rz': 1.0, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sy': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_tz': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_tx': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_ty': 1.0, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_ty': 0.2, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_tx': 0.2, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tx': 0.333, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_tz': 0.2, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rx': 1.0, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.05, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_ty': 1.0, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_tx': 1.0, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_tx': 0.1, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_tz': 1.0, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.666, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sy': 0.15, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.05, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.05, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_ry': 1.0, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_rx': 1.0, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tx': 0.15, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_tx': 0.05, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_tx': 1.0, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_tz': 0.05, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_tz': 1.0, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ry': 0.3, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.1, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tz': 0.333, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.5, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.666, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.1, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.1, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_rz': 0.05, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_rx': 0.05, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_ry': 0.05, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_sx': 0.2, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_sy': 0.2, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_sz': 0.2, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.05, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.1, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.1, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sx': 1.0, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sy': 1.0, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sz': 1.0, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_ry': 1.0, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.2, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.5, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.2, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.666, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rx': 1.0, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.1, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_tx': 1.0, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.5, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.5, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ry': 0.8, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.5, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_tz': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_ry': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_rx': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_rz': 1.0, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.1, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.1, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.1, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tx': 0.8, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ty': 0.8, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tz': 0.8, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.666, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 1.0, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 1.0, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 1.0, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.2, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_tz': 0.1, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.2, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.2, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.88, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_sx': 0.05, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.88, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.88, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.5, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.666, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rz': 0.2, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.05, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_tx': 0.1, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_ty': 0.1, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_tz': 0.1, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.5, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rx': 0.2, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_ty': 1.0, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_tx': 1.0, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_tz': 1.0, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tz': 0.3, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tx': 0.3, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ty': 0.3, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_sz': 0.1, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rz': 0.3, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_tz': 0.1, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rx': 0.3, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_rz': 0.2, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tz': 0.1, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ty': 0.1, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tx': 0.1, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.333, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_ry': 0.2, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.333, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sy': 1.0, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_tx': 0.1, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_tx': 0.05, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_rx': 0.2, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.05, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sz': 0.2, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sy': 0.2, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sx': 0.2, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_sz': 0.8, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ry': 0.333, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_sy': 0.1, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sx': 0.3, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sy': 0.3, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sz': 0.3, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_sx': 0.1, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sz': 1.0, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_sx': 0.2, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_sy': 0.2, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_sz': 0.2, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sz': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_rz': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_ry': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_rx': 1.0, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sx': 1.0, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.5, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.1, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sz': 0.8, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sy': 0.8, u'RT_lower_pinch_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sx': 0.8, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.05, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.88, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_tz': 0.05, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.666, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sx': 1.0, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_rx': 0.05, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ry': 0.333, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rx': 0.333, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sx': 0.15, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rz': 0.333, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tz': 0.3, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sy': 0.55, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sx': 0.55, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sz': 0.55, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.333, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tz': 0.55, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.333, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.333, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_ry': 1.0, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_rx': 1.0, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ty': 1.0, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_rz': 1.0, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rz': 0.333, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rx': 0.333, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tz': 0.333, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_ry': 0.05, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 1.0, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_ry': 0.15, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_rx': 0.15, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_rz': 0.15, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.15, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.15, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.15, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.15, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_rx': 1.0, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tz': 0.2, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_rz': 1.0, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.1, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_sy': 0.8, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_sx': 0.8, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_sz': 0.8, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sy': 1.0, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tx': 0.2, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.333, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tx': 1.0, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rz': 0.333, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rx': 0.333, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ty': 0.2, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tx': 1.0, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ty': 1.0, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tz': 1.0, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sz': 0.88, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rx': 0.3, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ry': 0.3, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sy': 0.333, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rz': 0.2, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rz': 0.3, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_ty': 0.05, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_tx': 0.05, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_ry': 1.0, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_tz': 0.05, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_rz': 0.8, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tz': 0.1, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ty': 0.1, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tx': 0.1, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 1.0, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.1, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_rx': 0.8, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sz': 0.3, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.1, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.333, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_rz': 1.0, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ry': 0.3, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.1, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rx': 0.3, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sz': 0.1, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sz': 1.0, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sx': 0.1, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sy': 0.1, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ty': 0.3, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_rz': 0.05, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_ry': 0.05, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_rx': 0.05, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_sz': 0.05, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_sx': 0.05, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_ry': 0.8, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_tz': 0.8, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_rx': 0.8, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tx': 0.3, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ty': 0.3, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tz': 0.3, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.333, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.333, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.333, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.333, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_tx': 0.8, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_tx': 0.8, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_ty': 0.8, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_tz': 0.8, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_rz': 0.4, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_rz': 0.05, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_rz': 0.8, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_sz': 1.0, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.95, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_sx': 1.0, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_sy': 1.0, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.666, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.95, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_sz': 0.05, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.95, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_ry': 0.05, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.1, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_sx': 0.4, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.1, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_sy': 0.4, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ry': 0.333, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rx': 0.333, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_rz': 0.88, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rz': 0.333, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.666, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sy': 0.3, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_tx': 0.25, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_ty': 0.25, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_tz': 0.25, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sy': 0.55, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sz': 1.0, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sz': 0.55, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sz': 1.0, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sx': 1.0, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sy': 1.0, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.15, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.333, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.333, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.333, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sx': 0.55, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.95, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.95, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_tz': 0.88, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.666, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.5, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.666, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.1, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.1, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_sx': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_rz': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_ry': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_rx': 1.0, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.333, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.95, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_tx': 0.2, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.5, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_rx': 0.8, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.5, u'LT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.5, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_rx': 0.1, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_ry': 0.1, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_rz': 0.1, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_ry': 0.8, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.05, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.05, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.05, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_rz': 0.8, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tx': 0.55, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ty': 0.55, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tz': 0.55, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.2, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.1, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.2, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.2, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_sx': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_sy': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_sz': 1.0, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ry': 0.55, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.666, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.1, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tz': 0.1, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ty': 0.1, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tx': 0.1, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sy': 0.55, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sx': 0.55, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_tx': 0.1, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.666, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.1, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_sz': 0.1, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 1.0, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 1.0, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 1.0, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.2, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.2, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.2, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rx': 1.0, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.666, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sy': 0.55, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sx': 0.55, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sx': 0.8, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sz': 0.55, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.88, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.88, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_rx': 0.05, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.88, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_sy': 0.1, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_sx': 0.1, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_sz': 0.1, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_ty': 1.0, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_tx': 1.0, u'LT_eyelid_outer_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_tz': 1.0, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sz': 0.1, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sy': 1.0, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sx': 0.1, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_sy': 0.1, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_ry': 0.88, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_ry': 0.2, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_rx': 0.2, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_rz': 0.2, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.666, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.88, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.666, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.666, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_ty': 0.4, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_tx': 0.4, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_tz': 0.4, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_rx': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_ry': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_rz': 1.0, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sy': 0.333, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_sy': 0.05, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.05, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sx': 0.333, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.1, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_rz': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_sx': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_sy': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_sz': 1.0, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_ty': 0.1, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sz': 0.333, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rz': 0.8, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ty': 0.15, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'RT_chin_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.22, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tz': 0.15, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sx': 1.0, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sy': 1.0, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_sz': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_ty': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_tx': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_tz': 1.0, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.5, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_rx': 1.0, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.666, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.666, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 1.0, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 1.0, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_ry': 1.0, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rz': 0.15, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rx': 0.15, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ry': 0.15, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_rz': 1.0, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_sz': 0.1, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sz': 1.0, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.1, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sx': 1.0, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sy': 1.0, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_ty': 1.0, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_sy': 0.8, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_sx': 0.8, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_sy': 0.05, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_sx': 0.05, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_ty': 0.05, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_sx': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_sy': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_sz': 1.0, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.5, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sz': 0.333, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sx': 0.2, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sx': 0.333, u'LT_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sy': 0.333, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_sz': 0.15, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_sx': 0.15, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_sy': 0.15, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.2, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.1, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.2, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.2, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.15, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.95, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_tz': 0.2, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_ty': 0.2, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_tx': 0.2, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.05, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.05, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.05, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_ty': 0.88, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ty': 0.2, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tx': 1.0, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_tz': 0.8, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_tx': 0.8, u'RT_up_cheek_bnd.RT_cheek_pri_ctrl_weight_ty': 0.8, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.666, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_rx': 1.0, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rz': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_ty': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_tx': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_tz': 1.0, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_tx': 0.1, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_ty': 0.1, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_tz': 0.1, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sz': 1.0, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sy': 1.0, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_rx': 0.4, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.88, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_tz': 1.0, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_ty': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ry': 0.2, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rx': 0.2, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rz': 0.3, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_sy': 0.1, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_sx': 0.1, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.666, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_sz': 0.1, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tx': 0.333, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_sy': 0.1, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.1, u'RT_in_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ty': 0.333, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_rz': 1.0, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_ry': 1.0, u'RT_eyelid_outer_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_rx': 1.0, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_ty': 0.1, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'LT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.666, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_sz': 0.1, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.5, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.5, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_sx': 0.1, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sx': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_ty': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_tx': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_tz': 1.0, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.1, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.1, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.05, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.88, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sx': 0.88, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_rx': 0.88, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_rx': 1.0, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_sx': 0.05, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_rz': 0.15, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_ry': 0.15, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_rx': 0.15, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.1, u'RT_in_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rx': 0.55, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.1, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.1, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tx': 0.2, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ty': 0.2, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tz': 0.2, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'RT_philtrum_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.333, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.333, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.333, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_rz': 0.05, u'CT_upper_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.05, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sx': 1.0, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tx': 0.2, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_sy': 0.1, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tz': 0.2, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_sz': 0.4, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_sx': 0.4, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_sy': 0.4, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.666, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_tz': 1.0, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_ty': 1.0, u'LT_nostril_bnd.CT_noseTip_pri_ctrl_weight_tx': 1.0, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ty': 0.8, u'CT_lower_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sy': 0.3, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sx': 0.3, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.666, u'CT_upper_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sz': 0.3, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.1, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.1, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.1, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sz': 0.1, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sx': 0.1, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_sy': 0.1, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rx': 0.2, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ry': 0.2, u'LT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_rz': 0.2, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_rx': 0.05, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.666, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.05, u'RT_sneer_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.666, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tz': 0.8, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_rz': 0.2, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_ry': 0.2, u'RT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_rx': 0.2, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 1.0, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rz': 1.0, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.333, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.666, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_sx': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_sy': 1.0, u'RT_in_brow_bnd.RT_mid_brow_pri_ctrl_weight_sz': 1.0, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 1.0, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.05, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_rz': 0.05, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_ry': 0.05, u'RT_philtrum_bnd.RT_cheek_pri_ctrl_weight_rx': 0.05, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sx': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_ry': 1.0, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.333, u'RT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_rz': 1.0, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sz': 0.3, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sy': 0.3, u'CT_upper_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sx': 0.3, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_rz': 0.05, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_rx': 0.05, u'LT_up_crease_bnd.LT_cheek_pri_ctrl_weight_ry': 0.05, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 1.0, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rx': 0.3, u'LT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_ty': 0.2, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_rz': 1.0, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_ry': 1.0, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_rx': 1.0, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_tz': 0.05, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tz': 0.15, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_sy': 0.05, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_ty': 0.1, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_sy': 0.1, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_sx': 0.1, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ry': 0.1, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rx': 0.1, u'RT_in_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rz': 0.1, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.1, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.05, u'RT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.1, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_ry': 0.4, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_rx': 0.1, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 1.0, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.2, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.2, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.1, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.2, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'LT_chin_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_rx': 0.88, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.2, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.5, u'LT_low_crease_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.2, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.15, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_tz': 0.4, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_ty': 0.4, u'RT_low_crease_bnd.CT_jaw_pri_ctrl_weight_tx': 0.4, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_rz': 0.8, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.1, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_rx': 0.8, u'LT_mid_crease_bnd.LT_cheek_pri_ctrl_weight_ry': 0.8, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_tx': 0.55, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ty': 0.55, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ry': 0.55, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sy': 0.8, u'RT_corner_lip_bnd.RT_corner_lip_pri_ctrl_weight_tx': 1.0, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_rx': 0.1, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sz': 0.8, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tx': 0.55, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ty': 0.55, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tz': 0.55, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_sz': 1.0, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rz': 0.3, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sx': 0.333, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rx': 0.3, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ry': 0.3, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.333, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rz': 0.55, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.333, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.333, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sy': 0.88, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.15, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.22, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_ty': 1.0, u'LT_out_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rx': 0.55, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.15, u'LT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.15, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_ry': 0.1, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_rz': 1.0, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_ry': 1.0, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_rx': 1.0, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.5, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sx': 0.3, u'LT_upper_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.333, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.1, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.1, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.5, u'CT_lower_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.1, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rx': 0.3, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ry': 0.3, u'CT_lower_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rz': 0.3, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.1, u'LT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.1, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sz': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sy': 1.0, u'LT_eyelid_inner_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_sx': 1.0, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_rz': 0.1, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.1, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_rz': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_ry': 1.0, u'RT_out_brow_bnd.RT_mid_brow_pri_ctrl_weight_rx': 1.0, u'CT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_rx': 1.0, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rz': 1.0, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ry': 0.8, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tz': 0.1, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ty': 0.1, u'LT_in_forehead_bnd.LT_mid_brow_pri_ctrl_weight_tx': 0.1, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.1, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_rz': 1.0, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_ry': 1.0, u'RT_eyelid_outer_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_rx': 1.0, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.5, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_tx': 1.0, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.666, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.666, u'RT_upper_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.666, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_ty': 1.0, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_sz': 0.2, u'LT_corner_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 1.0, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_sx': 0.2, u'RT_up_jaw_bnd.CT_jaw_pri_ctrl_weight_sy': 0.2, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_ry': 1.0, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_rx': 1.0, u'LT_mid_brow_bnd.LT_mid_brow_pri_ctrl_weight_rz': 1.0, u'CT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tx': 0.3, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_rx': 0.8, u'RT_low_cheek_bnd.RT_cheek_pri_ctrl_weight_ry': 0.1, u'RT_lower_pinch_lip_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.666, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.1, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sz': 0.333, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.333, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sx': 0.333, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sy': 0.333, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_rx': 0.88, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_sx': 0.25, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_tz': 1.0, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rx': 0.15, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_sy': 0.25, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.1, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_ty': 0.1, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_tx': 0.1, u'RT_squint_bnd.RT_cheek_pri_ctrl_weight_sz': 0.25, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_rx': 0.2, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.2, u'RT_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.2, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.1, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rz': 0.55, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.333, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.333, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.666, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.333, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.05, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.05, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_ry': 0.88, u'RT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.05, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rx': 0.55, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.95, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_tz': 1.0, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.15, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_tx': 1.0, u'RT_eyelid_inner_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_ty': 1.0, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_sz': 1.0, u'LT_sneer_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.666, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_sx': 1.0, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_sy': 1.0, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sz': 1.0, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sy': 1.0, u'RT_eyelid_inner_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_sx': 1.0, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ty': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_tz': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_ty': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_tx': 1.0, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.95, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.95, u'LT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.95, u'RT_in_cheek_bnd.RT_cheek_pri_ctrl_weight_sz': 0.05, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ry': 1.0, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.666, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_tz': 0.1, u'RT_lower_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.95, u'RT_upper_sneer_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'RT_sneer_bnd.RT_cheek_pri_ctrl_weight_ty': 0.1, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tz': 0.3, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ty': 0.3, u'CT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_tx': 0.3, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_rz': 0.1, u'LT_in_low_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rx': 0.55, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_rx': 0.1, u'RT_low_crease_bnd.RT_cheek_pri_ctrl_weight_ry': 0.1, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sz': 0.88, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_rz': 0.1, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_sy': 0.05, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.666, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.666, u'LT_lower_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.666, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_sz': 0.05, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_sz': 0.8, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tx': 1.0, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ry': 1.0, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_tz': 0.05, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_tx': 0.8, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_ty': 0.8, u'RT_mid_crease_bnd.RT_cheek_pri_ctrl_weight_tz': 0.8, u'LT_lower_sneer_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rx': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_rz': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_ry': 1.0, u'LT_cheek_bnd.LT_cheek_pri_ctrl_weight_rx': 1.0, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.5, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_tx': 0.5, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_ty': 0.5, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_tz': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_ty': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_tx': 1.0, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.333, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.333, u'RT_upper_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.333, u'CT_mid_chin_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.1, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_ty': 0.05, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_tx': 0.05, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sz': 1.0, u'LT_philtrum_bnd.LT_cheek_pri_ctrl_weight_tz': 0.05, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_tz': 0.88, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_rz': 0.4, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_ry': 0.4, u'LT_low_crease_bnd.CT_jaw_pri_ctrl_weight_rx': 0.4, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_sx': 1.0, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_sy': 1.0, u'LT_corner_jaw_bnd.CT_jaw_pri_ctrl_weight_sz': 1.0, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sz': 0.15, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_sy': 1.0, u'RT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.666, u'CT_lower_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.1, u'LT_out_brow_bnd.LT_mid_brow_pri_ctrl_weight_sz': 1.0, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_rz': 0.1, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_tz': 1.0, u'RT_mid_brow_bnd.RT_mid_brow_pri_ctrl_weight_ty': 1.0, u'LT_low_crease_bnd.LT_cheek_pri_ctrl_weight_ry': 0.1, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tz': 1.0, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ry': 0.1, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rx': 0.1, u'LT_eyelid_outer_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_ry': 1.0, u'RT_out_forehead_bnd.RT_mid_brow_pri_ctrl_weight_rz': 0.1, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.1, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tz': 0.333, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_ty': 0.333, u'RT_philtrum_bnd.RT_upper_sneer_lip_pri_ctrl_weight_tx': 0.333, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.1, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_sy': 0.25, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_sx': 0.25, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_sz': 0.25, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_rx': 0.666, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_ry': 0.666, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.666, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_rx': 0.05, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'RT_upper_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.15, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_ry': 0.1, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rx': 0.1, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_tx': 1.0, u'LT_out_forehead_bnd.LT_mid_brow_pri_ctrl_weight_rz': 0.1, u'LT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_tz': 0.88, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'RT_sneer_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'RT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_rz': 0.05, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'LT_sneer_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.1, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.1, u'LT_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.1, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ty': 1.0, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tx': 1.0, u'RT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tz': 1.0, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.333, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.333, u'RT_mid_crease_bnd.RT_corner_lip_pri_ctrl_weight_tz': 0.333, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_ty': 0.8, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_tx': 0.2, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_ty': 0.2, u'LT_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.2, u'LT_sneer_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sz': 0.15, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sz': 1.0, u'RT_upper_sneer_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sy': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sx': 1.0, u'LT_eyelid_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_sy': 1.0, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tz': 0.2, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_ty': 0.2, u'RT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_tx': 0.2, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_ry': 1.0, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_rx': 1.0, u'LT_eyelid_lower_bnd.LT_eyelid_lower_pri_ctrl_weight_rz': 1.0, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_tx': 0.05, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_ty': 0.05, u'RT_up_crease_bnd.RT_cheek_pri_ctrl_weight_tz': 0.05, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_ty': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_tx': 1.0, u'RT_nostril_bnd.CT_noseTip_pri_ctrl_weight_tz': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_rz': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_ry': 1.0, u'RT_cheek_bnd.RT_cheek_pri_ctrl_weight_rx': 1.0, u'RT_out_low_forehead_bnd.RT_mid_brow_pri_ctrl_weight_ry': 0.55, u'LT_up_cheek_bnd.CT_jaw_pri_ctrl_weight_ry': 0.05, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sy': 1.0, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_sx': 0.1, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_tz': 0.15, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_ty': 0.15, u'RT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_tx': 0.15, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.2, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.2, u'LT_lower_sneer_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.333, u'RT_low_crease_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.2, u'RT_corner_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.5, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_sz': 0.2, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_sx': 0.2, u'LT_up_crease_bnd.CT_noseTip_pri_ctrl_weight_sy': 0.2, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_tx': 0.1, u'LT_upper_sneer_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sz': 1.0, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_tx': 0.25, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_ty': 0.25, u'LT_squint_bnd.LT_cheek_pri_ctrl_weight_tz': 0.25, u'RT_lower_sneer_lip_bnd.RT_corner_lip_pri_ctrl_weight_ty': 0.22, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_sz': 1.0, u'CT_chin_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_sx': 1.0, u'CT_noseTip_bnd.CT_noseTip_pri_ctrl_weight_sy': 1.0, u'LT_in_philtrum_bnd.LT_upper_sneer_lip_pri_ctrl_weight_sz': 0.333, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sz': 0.88, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sy': 0.88, u'RT_lower_pinch_lip_bnd.CT_jaw_pri_ctrl_weight_sx': 0.88, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tx': 0.8, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_ty': 0.8, u'LT_upper_pinch_lip_bnd.LT_upper_sneer_lip_pri_ctrl_weight_tz': 0.8, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_tx': 0.1, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_ty': 0.1, u'LT_philtrum_bnd.CT_jaw_pri_ctrl_weight_tz': 0.1, u'LT_mid_chin_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sx': 1.0, u'RT_mid_chin_bnd.RT_lower_sneer_lip_pri_ctrl_weight_rz': 1.0, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_tz': 1.0, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_ty': 1.0, u'RT_eyelid_upper_bnd.RT_eyelid_upper_pri_ctrl_weight_tx': 1.0, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sy': 0.3, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sx': 0.3, u'CT_mid_chin_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.1, u'CT_lower_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_sz': 0.3, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.333, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.333, u'LT_mid_crease_bnd.LT_corner_lip_pri_ctrl_weight_sz': 0.333, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_tz': 1.0, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_tx': 1.0, u'LT_eyelid_inner_upper_bnd.LT_eyelid_upper_pri_ctrl_weight_ty': 1.0, u'RT_sneer_bnd.RT_upper_sneer_lip_pri_ctrl_weight_sx': 0.15, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_sx': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_sy': 0.1, u'LT_out_cheek_bnd.CT_jaw_pri_ctrl_weight_sz': 0.1, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_sz': 0.1, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_sx': 1.0, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_sy': 1.0, u'LT_in_brow_bnd.LT_mid_brow_pri_ctrl_weight_sz': 1.0, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_sy': 0.1, u'LT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_sy': 0.88, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_tz': 0.666, u'CT_upper_lip_bnd.RT_corner_lip_pri_ctrl_weight_sx': 0.1, u'LT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_rz': 0.5, u'RT_in_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.1, u'LT_in_philtrum_bnd.CT_jaw_pri_ctrl_weight_tx': 0.05, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_sy': 0.8, u'LT_up_cheek_bnd.LT_cheek_pri_ctrl_weight_sx': 0.8, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_tz': 1.0, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_ty': 1.0, u'RT_eyelid_lower_bnd.RT_eyelid_lower_pri_ctrl_weight_tx': 1.0, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_sy': 0.1, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rx': 0.8, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_ry': 0.8, u'LT_lower_pinch_lip_bnd.LT_lower_sneer_lip_pri_ctrl_weight_rz': 0.8, u'LT_in_philtrum_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.1, u'LT_sneer_bnd.LT_cheek_pri_ctrl_weight_tx': 0.1, u'LT_upper_pinch_lip_bnd.LT_corner_lip_pri_ctrl_weight_sx': 0.666, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_sx': 0.15, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_sy': 0.15, u'LT_mid_crease_bnd.CT_jaw_pri_ctrl_weight_sz': 0.15, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sy': 0.2, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sx': 0.2, u'RT_mid_chin_bnd.CT_jaw_pri_ctrl_weight_rz': 0.88, u'RT_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sz': 0.2, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_ry': 0.1, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_rx': 0.1, u'RT_upper_pinch_lip_bnd.RT_upper_sneer_lip_pri_ctrl_weight_rx': 0.8, u'RT_philtrum_bnd.RT_corner_lip_pri_ctrl_weight_rz': 0.1, u'LT_low_cheek_bnd.LT_cheek_pri_ctrl_weight_rx': 0.1, u'LT_in_cheek_bnd.LT_cheek_pri_ctrl_weight_ty': 0.05, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tz': 1.0, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_ty': 1.0, u'RT_lower_sneer_lip_bnd.RT_lower_sneer_lip_pri_ctrl_weight_tx': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_ty': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_tx': 1.0, u'LT_low_jaw_bnd.CT_jaw_pri_ctrl_weight_tz': 1.0, u'RT_low_cheek_bnd.CT_jaw_pri_ctrl_weight_tz': 0.5, u'CT_upper_lip_bnd.LT_corner_lip_pri_ctrl_weight_rz': 0.1, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sx': 0.2, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sy': 0.2, u'LT_in_philtrum_bnd.CT_noseTip_pri_ctrl_weight_sz': 0.2}
        for attr, val in allWeights.items():
            pm.Attribute(attr).set(val)
        
        pm.progressWindow(e=True, step=1, status='Rig cleanup...') # 7
        # rig cleanup
        face.cleanFaceRig()
        
        # add left eye deformer
        placementGrp = pm.PyNode('CT_placement_grp')
        edgeLoop = [pm.PyNode(edge) for edge in placementGrp.leftEyelidLoop.get()]
        eyePivot = pm.PyNode('l_eyeball_geo')
        rigidLoops = 2
        falloffLoops = 4
        eye.buildEyeRigCmd('LT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)
        
        # right eye deformer
        symTable = sym.buildSymTable('body_geo')
        pm.select(edgeLoop)
        mel.ConvertSelectionToVertices()
        vertsLoop = mc.ls(sl=True, fl=True)
        sym.flipSelection(vertsLoop, symTable)
        mel.ConvertSelectionToContainedEdges()
        edgeLoop = pm.ls(sl=True)
        eyePivot = pm.PyNode('r_eyeball_geo')
        eye.buildEyeRigCmd('RT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)
        
        weights.setEyelidLoopWeights('LT')
        weights.setEyelidLoopWeights('RT')
        
        # eyeball rig (simple aim constraints)
        eye.buildEyeballRig()
        
        pm.progressWindow(e=True, endProgress=True) 
        
        pm.select(cl=True)
            
    
        

class UI(pm.uitypes.Window):
    """
    """
    
    # constants 
    _TITLE = 'lsFaceRig Modules'
    _WINDOW = 'lsFR_win'
    
    _LTPREFIX = 'LT_'
    _RTPREFIX = 'RT_'
    
    def __new__(cls):
        '''
        delete old window and create new instance
        '''
        if pm.window(cls._WINDOW, exists=True):
            pm.deleteUI(cls._WINDOW)
            
        self = pm.window(cls._WINDOW, title=cls._TITLE, menuBar=True)
        return pm.uitypes.Window.__new__(cls, self)
    
    def __init__(self):
        '''
        create UI
        '''
        with pm.menu(l='Options') as menuOptions:
            pm.menuItem(l='Symmetry', checkBox=True)
            pm.menuItem(divider=True)
            pm.menuItem(l='Refresh')
            pm.menuItem(l='Reset')
        
        with pm.menu(l='Help') as menuHelp:
            pm.menuItem(l='Documentation')
            pm.menuItem(l='About')
        
        with pm.tabLayout() as mainTab:

            with pm.columnLayout(adj=True) as jawLayout:
                pass
            
            with pm.columnLayout(adj=True) as lipsLayout:
                pass
            
            with pm.columnLayout(adj=True) as eyeLayout:
                
                with pm.frameLayout(label='Geometry', cll=True) as geoFrame:
                    with pm.verticalLayout() as geoLayout:
                        self.sel_eyeball = uitypes.Selector(l='Eyeball')
                        self.sel_edgeloop = uitypes.Selector(l='Edge loop', bc=pm.Callback(self.initJointPlacement))
                        
                with pm.frameLayout(label='Joint Placement', cll=True, visible=False) as jntFrame:
                    with pm.verticalLayout() as jntLayout:
                        self.sel_innerVtx = uitypes.Selector(l='Inner Vtx')
                        self.sel_upperVtx = uitypes.Selector(l='Upper Vtx')
                        self.sel_outerVtx = uitypes.Selector(l='Outer Vtx')
                        self.sel_lowerVtx = uitypes.Selector(l='Lower Vtx')
                        
                with pm.frameLayout(label='Deformation', cll=True) as skinFrame:
                    with pm.verticalLayout() as skinLayout:
                        self.float_blinkHeight = pm.floatSliderGrp(l='Blink height', field=True, cw3=(60,40,140), 
                                                                   min=0, max=1, v=0.25, precision=2)
                        self.int_rigidLoops = pm.intSliderGrp(l='Rigid loops', field=True, cw3=(60,40,140),
                                                                 min=1, max=12, fieldMaxValue=99, v=4)
                        self.int_falloffLoops = pm.intSliderGrp(l='Falloff loops', field=True, cw3=(60,40,140),
                                                                 min=1, max=12, fieldMaxValue=99, v=4)
                        self.btn_updateEyelidCrv = pm.button(l='Show Eyelid Curve', en=False)
                        self.btn_updateMidCrv = pm.button(l='Show Mid Curve', en=False)
                        self.btn_updateWeights = pm.button(l='Update Skin Weights', en=False)
                        self.chk_useSkinLayers = pm.checkBox(l='Use ngSkinLayers', v=True)
                        
                with pm.frameLayout(label='Rig', cll=True) as rigFrame:
                    with pm.verticalLayout() as rigLayout:
                        self.btn_namePrefix = pm.textFieldGrp(l='Name Prefix', adj=2, cw2=(60,60))
                        self.btn_createRig = pm.button(l='Build Rig', c=pm.Callback(self.createEyeRigCmd))
            
            with pm.columnLayout(adj=True) as browsLayout:
                pass
        
        mainTab.setTabLabel((jawLayout,'Jaw'))
        mainTab.setTabLabel((lipsLayout,'Lips'))
        mainTab.setTabLabel((eyeLayout,'Eyes'))
        mainTab.setTabLabel((browsLayout,'Brows'))
        mainTab.setSelectTab(eyeLayout)
        
        self.show()
    
    def initJointPlacement(self):
        '''
        '''
        edgeLoop = self.sel_edgeloop.getSelection()
        pm.select(edgeLoop, r=True)
        meval('ConvertSelectionToVertices')
        vertLoop = pm.ls(sl=True, fl=True)
        
        # determine inner, upper, outer and lower verts
        # find upper, outer, lower first
        upperVtx = max(vertLoop, key=lambda vtx: vtx.getPosition()[1])
        outerVtx = min(vertLoop, key=lambda vtx: vtx.getPosition()[2])
        lowerVtx = min(vertLoop, key=lambda vtx: vtx.getPosition()[1])

        # find out which side is outer on
        if outerVtx.getPosition().x > upperVtx.getPosition().x:
            # inner should be on min x
            innerVtx = min(vertLoop, key=lambda vtx: vtx.getPosition()[0])
        else:
            # inner should be on max x
            innerVtx = max(vertLoop, key=lambda vtx: vtx.getPosition()[0])
            
        # select/display verts
        # pm.select(innerVtx, upperVtx, outerVtx, lowerVtx)
        # reselect edge loop, so it looks like nothing happened
        pm.select(edgeLoop, r=True)
        
        # update display
        self.sel_innerVtx.setSelection(innerVtx)
        self.sel_upperVtx.setSelection(upperVtx)
        self.sel_outerVtx.setSelection(outerVtx)
        self.sel_lowerVtx.setSelection(lowerVtx)
    
    def getClosestCV(self, crv, pt):
        '''
        crv - nt.nurbsCurve
        pt - pm.dt.Point
        returns nt.nurbsCurveCV closest to pt
        '''
        allCVPts = crv.getCVs()
        cvId = allCVPts.index(min(allCVPts, key=lambda p: (pt-p).length()))
        return crv.cv[cvId]
    
    def createEyeRigCmd(self):
        
        # hard code name for now
        name = self.btn_namePrefix.getText()
        if name == '':
            name = 'LT_eye'
        # get data from ui
        eyePivot = self.sel_eyeball.getSelection()[0]
        edgeLoop = self.sel_edgeloop.getSelection()
        blinkLine = self.float_blinkHeight.getValue()
        rigidLoops = self.int_rigidLoops.getValue()
        falloffLoops = self.int_falloffLoops.getValue()
        influenceLoops = rigidLoops + falloffLoops
        
        pm.progressWindow(title='Rigging eyelid', max=3, status='\nCreate bind joints...')
        # first run will mess up UI, refresh to redraw window properly
        pm.refresh()
        
        aimLocs, aimJnts, drvCrv = eye.constructEyelidsDeformer(name, eyePivot, edgeLoop)
        
        pm.progressWindow(e=True, step=1, status='\nCreate driver joints...')
        
        # get cv selections for inner, upper, outer, lower
        innerPos = self.sel_innerVtx.getSelection().getPosition()
        innerCV = self.getClosestCV(drvCrv, innerPos)
        upperPos = self.sel_upperVtx.getSelection().getPosition()
        upperCV = self.getClosestCV(drvCrv, upperPos)
        outerPos = self.sel_outerVtx.getSelection().getPosition()
        outerCV = self.getClosestCV(drvCrv, outerPos)
        lowerPos = self.sel_lowerVtx.getSelection().getPosition()
        lowerCV = self.getClosestCV(drvCrv, lowerPos)
        
        # select cvs for inner upper outer lower
        cornerCVs = [innerCV, upperCV, outerCV, lowerCV]
        eyePivotVec, sections, targetCrv, drvJnts, drvSkn = eye.constructEyelidsRig(name, eyePivot, cornerCVs)
        # returned variables above need to be connected to masterGrp
        # so that we can reweight later
        
        pm.progressWindow(e=True, step=1, status='\nWeight driver joints...')
        
        # reweighting (just to get the angles)
        # though it would be better to get the angles from the previous function
        # but that was not done properly
        up, lw, drvSkn = eye.reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn)
        upperAngle = max(up) * 1.05
        lowerAngle = max(lw) * 1.05
        
        pm.progressWindow(e=True, endProgress=True)
        
        # get vertex loops
        pm.select(edgeLoop, r=True)
        meval('ConvertSelectionToVertices')
        root = eye.constructVertexLoops(influenceLoops)
        pm.select(cl=True)
        
        # calculate generation weights (for layer mask)
        generationWeights = [1] * rigidLoops
        linearFalloff = [float(index)/(falloffLoops+1) for index in range(falloffLoops,0,-1)]
        smoothFalloff = pm.dt.smoothmap(0, 1, linearFalloff)
        generationWeights += smoothFalloff
        
        # assume that skn weights are already set up
        eye.setMeshWeights(root, aimJnts, generationWeights)
        
        masterGrp = eye.rigCleanup(name, aimJnts, drvJnts, aimLocs, drvSkn, targetCrv)
        
        # build eyeball rig
        grp_eye, grp_aimEyeTgt = eye.buildEyeballRig(name, eyePivot, masterGrp, cornerCVs)
        
        eye.setConnections(masterGrp, drvJnts, upperAngle, lowerAngle, blinkLine)
        
        eye.addAutoEyelids(name, masterGrp)
        
        eye.createGUI(name, masterGrp)

        # update UI buttons
        self.btn_updateWeights.setEnable(True)
        self.btn_updateMidCrv.setEnable(True)
        self.btn_updateEyelidCrv.setEnable(True)
        self.btn_createRig.setLabel('Rebuild Rig')
        