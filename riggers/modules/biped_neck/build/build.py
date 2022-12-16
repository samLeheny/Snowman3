# Title: neck_build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds biped_neck rig module.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.modules.biped_neck.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as control_colors
importlib.reload(control_colors)
ctrl_colors = control_colors.create_dict()
###########################
###########################


###########################
######## Variables ########
jnt_resolution = 5
tweak_ctrl_color = ctrl_colors[nom.midSideTag3]
###########################
###########################





########################################################################################################################
#def build(rig_module, rig_parent=None, rig_space_connector=None):
def build(rig_module, rig_parent=None):


    temp_nodes_to_delete = []
    ctrls = rig_module.ctrls


    ctrls["settings"].setParent(rig_module.transform_grp)

    ctrls["neck"].setParent(rig_module.transform_grp)

    up_obj = pm.spaceLocator(name="neckRibbon_up_{}".format(nom.locator))
    up_obj.setParent(ctrls["neck"])
    gen_utils.zero_out(up_obj)
    up_obj.tz.set(gen_utils.distance_between(obj_1=ctrls["neck"], obj_2=ctrls["head"]))
    up_obj.setParent(rig_module.transform_grp)
    temp_nodes_to_delete.append(up_obj)


    ctrls["head"].setParent(ctrls["neck"])
    gen_utils.buffer_obj(ctrls["head"])





    # ...Bind joints ---------------------------------------------------------------------------------------------------
    jnts = {"head": rig_utils.joint(name="head", joint_type=nom.bindJnt, radius=1.25, side=rig_module.side)}

    jnts["head"].setParent(ctrls["head"])
    gen_utils.zero_out(jnts["head"])



    # ...
    temp_neck_aimer = pm.spaceLocator(name="neck_aimer_TEMP")
    pm.delete(pm.pointConstraint(ctrls["neck"], temp_neck_aimer))
    pm.delete(pm.aimConstraint(ctrls["head"], temp_neck_aimer, worldUpType="object", worldUpObject=up_obj,
                               aimVector=(0, 1, 0), upVector=(0, 0, 1)))
    temp_nodes_to_delete.append(temp_neck_aimer)




    stretch_socket = pm.shadingNode("transform", name="stretch_socket_start", au=1)
    stretch_socket.setParent(temp_neck_aimer)
    gen_utils.zero_out(stretch_socket)
    stretch_socket.setParent(ctrls["neck"])

    stretch_out_socket = pm.shadingNode("transform", name="stretch_socket_end", au=1)
    stretch_out_socket.setParent(ctrls["head"])
    gen_utils.zero_out(stretch_out_socket)
    pm.delete(pm.orientConstraint(temp_neck_aimer, stretch_out_socket))




    # ...Roll joint system ---------------------------------------------------------------------------------------------
    pm.addAttr(ctrls["settings"], longName="NeckLen", attributeType="float", minValue=0.001, defaultValue=1, keyable=1)


    # ...Rollers
    neck_roller = rig_utils.limb_rollers(start_node=stretch_socket,
                                         end_node=stretch_out_socket,
                                         roller_name="neck",
                                         start_rot_match=ctrls["neck"],
                                         end_rot_match=ctrls["head"],
                                         ctrl_mid_influ=True,
                                         populate_ctrls=(0, 1, 0),
                                         roll_axis=(0, 1, 0),
                                         up_axis=(0, 0, 1),
                                         ctrl_color=15,
                                         parent=rig_module.no_transform_grp,
                                         side=rig_module.side)

    # ...Ribbon
    ribbon_up_vector = (0, 0, -1)
    if rig_module.side == nom.rightSideTag:
        ribbon_up_vector = (0, 0, 1)

    # ...Create ribbons
    neck_ribbon = rig_utils.ribbon_plane(name="neck", start_obj=stretch_socket, end_obj=stretch_out_socket,
                                         up_obj=up_obj, density=jnt_resolution, side=rig_module.side,
                                         up_vector=ribbon_up_vector)
    neck_ribbon["nurbsStrip"].setParent(rig_module.no_transform_grp)
    neck_ribbon["nurbsStrip"].scale.set(1, 1, 1)


    # ...Skin ribbons
    pm.select(neck_roller["start_jnt"], neck_roller["mid_jnt"], neck_roller["end_jnt"], replace=1)
    pm.select(neck_ribbon["nurbsStrip"], add=1)
    pm.skinCluster(maximumInfluences=1, toSelectedBones=1)


    # ...Tweak ctrls
    neck_length = node_utils.multDoubleLinear(input1=ctrls["settings"] + "." + "NeckLen",
                                              input2= gen_utils.distance_between(obj_1=ctrls["neck"],
                                                                                 obj_2=ctrls["head"]))



    # ------------------------------------------------------------------------------------------------------------------
    pm.addAttr(ctrls["settings"], longName="Volume", attributeType="float", minValue=0, maxValue=10, defaultValue=0,
               keyable=1)

    neck_tweak_ctrls = rig_utils.ribbon_tweak_ctrls(
        ribbon=neck_ribbon["nurbsStrip"], ctrl_name="neck", length_ends=(ctrls["neck"], ctrls["head"]),
        length_attr=neck_length.output, attr_ctrl=ctrls["settings"], side=rig_module.side, ctrl_color=tweak_ctrl_color,
        ctrl_resolution=jnt_resolution, parent=rig_module.no_transform_grp, ctrl_size=5.0)



    # Adjustable biped_neck length -------------------------------------------------------------------------------------
    rig_module.neck_len_start_node = pm.shadingNode("transform", name="neck_length_start", au=1)
    rig_module.neck_len_end_node = pm.shadingNode("transform", name="neck_length_end", au=1)
    rig_module.neck_len_end_node.setParent(rig_module.neck_len_start_node)

    pm.matchTransform(rig_module.neck_len_start_node, ctrls["neck"])
    pm.delete(pm.aimConstraint(ctrls["head"], rig_module.neck_len_start_node, worldUpType="object",
                               worldUpObject=up_obj, aimVector=(0, 1, 0), upVector=(0, 0, 1)))
    pm.matchTransform(rig_module.neck_len_end_node, ctrls["head"])

    neck_length.output.connect(rig_module.neck_len_end_node.ty)
    rig_module.neck_len_start_node.setParent(ctrls["neck"])


    ctrls["head"].getParent().setParent(rig_module.neck_len_end_node)




    # Finalize controls ------------------------------------------------------------------------------------------------
    '''ctrls["neckBend"] = ctrl_data["neckBend"].initialize_anim_ctrl(existing_obj=neck_roller["mid_ctrl"])


    ctrl_pairs = (("neck",),
                  ("neckBend", neck_roller["mid_ctrl"]),
                  ("head",))

    for key in ctrl_data:
        ctrl_data[key].finalize_anim_ctrl(delete_existing_shapes=True)'''


    [gen_utils.zero_offsetParentMatrix(ctrl) for ctrl in ctrls.values()]




    # ...Attach neck rig to greater rig --------------------------------------------------------------------------------
    '''if rig_space_connector:
        gen_utils.matrix_constraint(objs=[rig_space_connector, rig_connector], decompose=True,
                                    translate=True, rotate=True, scale=False, shear=False, maintain_offset=True)'''




    # ------------------------------------------------------------------------------------------------------------------
    pm.delete(temp_nodes_to_delete)
    pm.select(clear=1)
    return rig_module
