# Title: spine_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.riggers.modules.biped_spine.setup.subModules.waist_ribbon as waist_ribbon
importlib.reload(waist_ribbon)

import Snowman3.riggers.modules.biped_spine.utilities.prelimCtrls as prelimCtrls
importlib.reload(prelimCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    #...Ribbon system -------------------------------------------------------------------------------------------------
    ribbon_sys = waist_ribbon.install(spine_module=armature_module, symmetry=armature_module.symmetry)
    ribbon_sys["nurbsPlane"].setParent(armature_module.module_ctrl.mobject)
    ribbon_sys["nurbsPlane"].visibility.set(0, lock=1)
    ribbon_sys["nurbsPlane"].inheritsTransform.set(0, lock=1)

    ribbon_sys["joints_group"].setParent(armature_module.module_ctrl.mobject)


    #...Position module
    armature_module.position_module()



    #...Spine ribbon --------------------------------------------------------------------------------------------------
    armature_module.ribbon = ribbon_sys["nurbsPlane"]



    #...Preliminary controls ------------------------------------------------------------------------------------------
    ctrls_dict = prelimCtrls.create_prelim_ctrls(side=armature_module.side,
                                                 is_driven_side=armature_module.is_driven_side)
    armature_module.create_prelim_ctrls()

    #... Pin ctrls to ribbon
    i = 0
    '''for pair in (("COG", 0.0),'''
    for pair in (("ik_waist", 0.5),
                 ("ik_chest", 1.0),
                 ("fk_hips", 0.25),
                 ("ik_pelvis", 0.0),
                 ("fk_spine_3", 0.89),
                 ("fk_spine_2", 0.64),
                 ("fk_spine_1", 0.3)):
        pin = gen_utils.point_on_surface_matrix(ribbon_sys["nurbsPlane"].getShape() + ".worldSpace",
                                                parameter_U=0.5, parameter_V=pair[1], decompose=True)
        armature_module.prelim_ctrls[pair[0]].ctrl_obj.inheritsTransform.set(0)
        pin.outputTranslate.connect(armature_module.prelim_ctrls[pair[0]].ctrl_obj.translate)
        i += 1


    spine_seg_count = len(armature_module.placers)
    for i in range(spine_seg_count+1):

        pin = gen_utils.point_on_surface_matrix(ribbon_sys["nurbsPlane"].getShape() + ".worldSpace",
                                                parameter_U=0.5, parameter_V=(1.0 / spine_seg_count) * i,
                                                decompose=True)

        pin.outputTranslate.connect(armature_module.prelim_ctrls["spine_tweak_{}".format(i+1)].ctrl_obj.translate)
        armature_module.prelim_ctrls["spine_tweak_{}".format(i+1)].ctrl_obj.inheritsTransform.set(0)




    return armature_module
