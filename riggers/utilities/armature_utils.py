# Title: armature_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)
###########################
###########################


# Global variables ########

###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
get_modules_in_armature
get_module_type
check_if_constrained
check_if_placer
check_if_constrained_to_placer
get_driver_placer
get_module_from_placer
get_placers_in_module
get_ctrl_from_module
get_piece_keys_from_module
connect_pair
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################




########################################################################################################################
def get_modules_in_armature(armature):

    #...Get all attributes in the provided armature MObject
    search = pm.listAttr(armature)

    #...Isolate only those attributes starting with "Module_"
    module_hooks = []
    for attr in search:
        if attr.startswith("Module_"):
            module_hooks.append(attr)

    #...Follow those attributes to module MObjects, and use the attributes as tags
    modules = {}
    for attr_name in module_hooks:
        search = pm.listConnections(armature + "." + attr_name, s=1, d=0)
        if search:
            module_tag = attr_name.split("Module_")[1]
            modules[module_tag] = search[0]


    return modules





########################################################################################################################
def get_module_type(module):

    return pm.getAttr(module + "." + "ModuleType")





########################################################################################################################
def check_if_constrained(obj):

    constrained_status = False

    #...Get all nodes driving provided object via translation
    connected_nodes = []
    for attr_name in ("translate", "tx", "ty", "tz"):
        possible_connection = pm.listConnections(obj + "." + attr_name, s=1, d=0)
        connected_nodes.append(possible_connection[0]) if possible_connection else None

    #...Check if any of these nodes are constraint nodes
    for node in connected_nodes:
        if node.nodeType() in ("pointConstraint", "parentConstraint"):
            constrained_status = True
            break


    return constrained_status





def get_outgoing_constraints(obj):

    driver_status = False

    #...Get any nodes coming from object's translation
    constraint_nodes = []
    for attr_name in ("translate", "rotate", "scale"):
        connected_nodes = pm.listConnections(obj + "." + attr_name, d=1, s=0)
        if not connected_nodes:
            return None
        else:
            for node in connected_nodes:
                if node.nodeType() in ("pointConstraint", "orientConstraint", "parentConstraint", "scaleConstraint"):
                    constraint_nodes.append(node)

    return constraint_nodes






########################################################################################################################
def check_if_placer(obj):

    placer_status = False

    if str(obj.name()).endswith("_PLC"):
        placer_status = True


    return placer_status





########################################################################################################################
def check_if_constrained_to_placer(obj):

    return_status = False
    armature_node = None
    constraint_node = None

    armature_node = get_driver_placer(obj)
    if armature_node:
        return_status = True


    return {"success_state": return_status,
            "driver_placer": armature_node}





########################################################################################################################
def get_driver_placer(obj):

    return_node = None
    constraint_node = None

    for attr_name in ("translate", "tx", "ty", "tz"):
        possible_connection = pm.listConnections(obj + "." + attr_name, s=1, d=0)
        if possible_connection:
            connected_node = possible_connection[0]
            if connected_node.nodeType() in ("pointConstraint", "parentConstraint"):
                constraint_node = connected_node
                break

    constraint_driver = None
    if constraint_node:
        constraint_driver = pm.listConnections(f'{constraint_node}.target[0].targetTranslate', source=1)[0]

    if check_if_placer(constraint_driver):

        return_node = constraint_driver


    return return_node





########################################################################################################################
def get_module_from_placer(obj, return_tag=False):

    module_ctrl = None
    connections = pm.listConnections(obj.message, d=1, s=0)
    for c in connections:
        if c.nodeType() == "transform":
            module_ctrl = c
            break

    module = None
    connections = pm.listConnections(module_ctrl.message, d=1, s=0)
    for c in connections:
        if c.nodeType() == "transform":
            module = c
            break

    if return_tag:
        return pm.getAttr(module + "." + "ModuleName")

    return module





########################################################################################################################
def get_placers_in_module(module):

    #...Get module control
    ctrl = pm.listConnections(module + ".ModuleRootCtrl", s=1, d=0)[0]

    #...Get placers
    placers = {}
    attr_string = "PlacerNodes"
    for attr_name in pm.listAttr(ctrl + "." + attr_string):
        if attr_name != attr_string:
            placers[attr_name] = pm.listConnections(ctrl + "." + attr_string + "." + attr_name, s=1, d=0)[0]

    return placers





########################################################################################################################
def get_ctrl_from_module(module):

    ctrl = pm.listConnections(f'{module}.ModuleRootCtrl', s=1, d=0)[0]

    return ctrl





########################################################################################################################
def get_piece_keys_from_module(module):

    ctrl = get_ctrl_from_module(module)

    keys = []

    attr_string = "PlacerNodes"

    for attr_name in pm.listAttr(ctrl + "." + attr_string):
        if attr_name != attr_string:
            keys.append(attr_name)

    return keys





########################################################################################################################
def connect_pair(obj, attrs=()):

    #...Determine driver and follower placers in placer pair
    driver_obj = obj
    receiver_obj = gen_utils.get_opposite_side_obj(driver_obj)

    #...Drive translation
    for attr in attrs:
        if not pm.attributeQuery(attr, node=driver_obj, exists=1):
            continue
        if not pm.getAttr(receiver_obj + "." + attr, lock=1):
            pm.connectAttr(driver_obj + "." + attr, receiver_obj + "." + attr, f=1)
