# Title: root_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of character body rig's root controls.


###########################
##### Import Commands #####
import importlib

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.root.setup.subModules.ctrl_vis_conditions as vis_conditions
importlib.reload(vis_conditions)

import Snowman3.riggers.dictionaries.body_attributes as body_attributes
importlib.reload(body_attributes)
attrNom = body_attributes.create_dict()

import Snowman3.riggers.modules.root.data.placers as armature_module_placers
import Snowman3.riggers.modules.root.data.ctrl_data as root_prelimControls
importlib.reload(armature_module_placers)
importlib.reload(root_prelimControls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    #armature_module.populate_module()

    #...Position module
    armature_module.position_module()


    #...Connect to another module if specified ------------------------------------------------------------------------
    armature_module.connect_modules()



    #...Preliminary controls -------------------------------------------------------------------------------------------
    armature_module.ctrl_data = root_prelimControls.create_ctrl_data(
        side=armature_module.side,
        is_driven_side=armature_module.is_driven_side,
        module_ctrl=armature_module.module_ctrl
    )

    armature_module.create_prelim_ctrls()





    """
    ctrls = {}
    grps = {}
    objs_to_lock = []




    # Create setup root control ----------------------------------------------------------------------------------------
    ctrls["setup_root"] = root_pieces["setup_root"].create_ctrl()


    # Root controls
    ctrls["root"] = root_pieces["character_root"].create_ctrl()
    ctrls["root_offset"] = root_pieces['character_root_offset'].create_ctrl()





    # Create groups under setup root -----------------------------------------------------------------------------------
    grps["transform"] = pm.group(name="transform_{0}".format(nom.group), em=1, p=ctrls["setup_root"])

    grps["no_transform"] = pm.group(name="noTransform_{0}".format(nom.group), em=1, p=ctrls["setup_root"])
    pm.setAttr(grps["no_transform"] + ".inheritsTransform", 0, lock=1)

    grps["placers"] = pm.group(name="placers_{0}".format(nom.group), em=1, p=grps["transform"])

    grps["skeleton"] = pm.group(name="skeleton_{0}".format(nom.group), em=1, p=grps["transform"])

    grps["controls"] = pm.group(name="controls_{0}".format(nom.group), em=1, p=grps["transform"])

    grps["contact_curves"] = pm.group(name="contactCrvs_{0}".format(nom.group), em=1, p=grps["transform"])

    grps["modules"] = pm.group(name="setupRigModules_{0}".format(nom.group), em=1, p=ctrls["setup_root"])


    # Mark all groups except 'modules' as needing to have their transforms locked off
    for key in ["transform", "no_transform", "placers", "skeleton", "controls", "contact_curves"]:
        objs_to_lock.append(grps[key])





    # Attributes -------------------------------------------------------------------------------------------------------
    # Scale
    pm.addAttr(ctrls["setup_root"], longName=attrNom.rigScale, attributeType="float", defaultValue=1, minValue=0,
               keyable=0)
    pm.setAttr(ctrls["setup_root"] + '.' + attrNom.rigScale, channelBox=1)

    for attr in gen_utils.scale_attrs:
        pm.connectAttr(ctrls["setup_root"] + "." + attrNom.rigScale, ctrls["setup_root"] + "." + attr)

    for attr in gen_utils.rotate_attrs + gen_utils.scale_attrs:
        pm.setAttr(ctrls["setup_root"] + "." + attr, lock=1, keyable=0)



    # Setup vis conditions ---------------------------------------------------------------------------------------------
    ctrl_vis_conditions, setup_vis_conditions = vis_conditions.build_conditions( attr_node=ctrls["setup_root"],
                                                                                 grps=grps)



    # Scale driving ----------------------------------------------------------------------------------------------------
    attr_names = [attrNom.PlacerScale]
    for attr_name in attr_names:
        pm.addAttr(ctrls["setup_root"], longName=attr_name, attributeType='float', defaultValue=1, minValue=0,
                   keyable=0)
        pm.setAttr(ctrls["setup_root"] + "." + attr_name, channelBox=1)


    # Controls
    # Group to hold root controls
    root_ctrls_grp = pm.group(name='rootCtrls_{0}'.format(nom.group), em=1, p=grps["controls"])
    pm.connectAttr(ctrl_vis_conditions[0].outColor.outColorR, root_ctrls_grp + '.visibility')
    # Root control parentage
    ctrls["root"].setParent(root_ctrls_grp)
    ctrls["root_offset"].setParent(root_ctrls_grp)


    # Lock down objects whose transforms should be left alone
    [ [ pm.setAttr(obj + "." + attr, lock=1, keyable=0) for attr in gen_utils.keyable_attrs ] for obj in objs_to_lock ]


    # Hidden attributes
    # Symmetry
    driver_side = None
    if symmetry == 'Left drives Right':
        driver_side = nom.leftSideTag
    elif symmetry == 'Right drives Left':
        driver_side = nom.rightSideTag


    pm.addAttr(ctrls["setup_root"], longName=attrNom.driverSide, dataType="string", keyable=0)
    driver_side_string = "None"
    if driver_side:
        driver_side_string = driver_side
    pm.setAttr(ctrls["setup_root"] + '.' + attrNom.driverSide, driver_side_string, type="string", lock=1)





    return {
                "controls": ctrls,
                "groups": grps,
                "ctrl_vis_conditions": ctrl_vis_conditions,
                "setup_vis_conditions": setup_vis_conditions,
    }"""

    return armature_module
