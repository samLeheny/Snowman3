# Title: root_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of character body rig's root controls.


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.utilities.node_utils as node_utils
reload(node_utils)

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman.riggers.dictionaries.body_attributes as body_attributes
reload(body_attributes)
attrNom = body_attributes.create_dict()
###########################
###########################


###########################
######## Variables ########
setupNamespace = '{0}:'.format(nom.setupRigNamespace)
vis_switch_enum_strings = {
    "placers" : "PlacersVis",
    "controls" : "ControlsVis"
}

ctrl_vis_switch_enum_strings = [
    "All",
    "Root",
    "Spine",
    "Neck - Head",
    "IK Limbs",
    "FK Limbs",
    "Hands - Feet",
    "Tweakers"
]
###########################
###########################





########################################################################################################################
def build_conditions(attr_node, grps):



    # Vis mode switch
    pm.addAttr(attr_node, longName=attrNom.setupMode, attributeType="enum", keyable=0,
               enumName="{0}:{1}".format(vis_switch_enum_strings["placers"],
                                         vis_switch_enum_strings["controls"])
               )
    pm.setAttr(attr_node + '.' + attrNom.setupMode, channelBox=1)


    setup_vis_conditions = {
        "placers": node_utils.condition(name="setupMode_placers_COND",
                                        firstTerm=attr_node + '.' + attrNom.setupMode,
                                        secondTerm=0, colorIfTrue=[1, 0, 0], colorIfFalse=[0, 1, 1],
                                        operation=0, outColor=[
                                             [grps["placers"] + ".visibility", grps["contact_curves"] + ".visibility"],
                                             None, None]),

        "controls": node_utils.condition(name="setupMode_controls_COND",
                                         firstTerm=attr_node + '.' + attrNom.setupMode,
                                         secondTerm=1, colorIfTrue=[1, 0, 0], colorIfFalse=[0, 1, 1],
                                         operation=0, outColor=[grps["controls"] + ".visibility", None, None])
    }


    # Controls vis
    pm.addAttr(attr_node, longName=attrNom.ctrlsVis, attributeType="enum", keyable=0,
               enumName="{0}:{1}:{2}:{3}:{4}:{5}:{6}:{7}".format(
                   ctrl_vis_switch_enum_strings[0],
                   ctrl_vis_switch_enum_strings[1],
                   ctrl_vis_switch_enum_strings[2],
                   ctrl_vis_switch_enum_strings[3],
                   ctrl_vis_switch_enum_strings[4],
                   ctrl_vis_switch_enum_strings[5],
                   ctrl_vis_switch_enum_strings[6],
                   ctrl_vis_switch_enum_strings[7]
               ))
    pm.setAttr(attr_node + '.' + attrNom.ctrlsVis, channelBox=1)

    ctrls_vis_condition_string = 'setupMode_ctrlsVis_COND'

    all_ctrls_vis_condition = node_utils.condition(name="{0}_{1}".format(ctrls_vis_condition_string,
                                                                         ctrl_vis_switch_enum_strings[0]), firstTerm=attr_node + '.' + attrNom.ctrlsVis,
                                                   secondTerm=0, colorIfTrue=[1, 0, 0], colorIfFalse=[0, 1, 1],
                                                   operation=0, outColor=[[grps["placers"] + ".visibility", grps["contact_curves"] + ".visibility"], None, None])

    ctrl_vis_conditions = []

    def condition_node(name, second_term):
        node = node_utils.condition(
            name="{0}_{1}".format(name, ctrls_vis_condition_string),
            firstTerm=attr_node + '.' + attrNom.ctrlsVis,
            secondTerm=second_term,
            colorIfTrue=[1, 0, 0],
            colorIfFalse=[all_ctrls_vis_condition + '.outColor.outColorR', 1, 1],
        )
        ctrl_vis_conditions.append(node)

    for i in xrange(0, len(ctrl_vis_switch_enum_strings) - 1):
        condition_node(ctrl_vis_switch_enum_strings[i+1], i + 1)




    return ctrl_vis_conditions, setup_vis_conditions