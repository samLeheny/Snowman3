# Title: constraint_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
from dataclasses import dataclass
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)
###########################
###########################


###########################
######## Variables ########

###########################
###########################



########################################################################################################################
@dataclass
class CustomConstraint:
    name: str
    constraint_type: str
    target_list: list
    constrained_node: str
    maintain_offset: bool = True
    interpType: int = 2
    worldUpType: int = 0
    worldUpVector: tuple = None
    upVector: tuple = None
    aimVector: tuple = None
    parent: str = None




def get_constrained_node(constraint):
    constraint_type = constraint.nodeType()

    type_out_attributes = {
        'pointConstraint': ('constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ'),
        'parentConstraint': ('constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ',
                             'constraintRotateX', 'constraintRotateY', 'constraintRotateZ'),
        'orientConstraint': ('constraintRotateX', 'constraintRotateY', 'constraintRotateZ'),
        'scaleConstraint': ('constraintScaleX', 'constraintScaleY', 'constraintScaleZ'),
        'aimConstraint': ('constraintRotateX', 'constraintRotateY', 'constraintRotateZ'),
        'geometryConstraint': ('constraintGeometry',)
    }
    if constraint_type not in type_out_attributes.keys():
        raise Exception(f"Unsupported constraint type: '{constraint_type}'")
    out_attributes = type_out_attributes[constraint_type]

    connected_nodes = set()
    for attribute in out_attributes:
        nodes = pm.listConnections(f'{constraint.nodeName()}.{attribute}', d=1, s=0, scn=1, p=0)
        connected_nodes.update(nodes) if nodes else None

    if len(connected_nodes) > 1:
        raise Exception('Multiple constrained nodes not supported.')
    if len(connected_nodes) < 1:
        raise Exception('No node was controlled by the constraint')

    return list(connected_nodes)[0]



def create_constraint_data(constraint):
    data = None
    constraint_name = constraint.nodeName()
    constraint_type = constraint.nodeType()
    parent = constraint.getParent().nodeName()
    if constraint_type == 'pointConstraint':
        data = CustomConstraint(
            name=constraint_name,
            constraint_type=constraint_type,
            maintain_offset=True,
            target_list=[node.nodeName() for node in pm.pointConstraint(constraint_name, q=1, tl=1)],
            constrained_node=get_constrained_node(constraint).nodeName(),
            parent=parent
        )
    elif constraint_type == 'parentConstraint':
        data = CustomConstraint(
            name=constraint_name,
            constraint_type=constraint_type,
            maintain_offset=True,
            target_list=[node.nodeName() for node in pm.parentConstraint(constraint, q=1, tl=1)],
            constrained_node=get_constrained_node(constraint).nodeName(),
            interpType=constraint.interpType.get(),
            parent=parent
        )
    elif constraint_type == 'orientConstraint':
        data = CustomConstraint(
            name=constraint_name,
            constraint_type=constraint_type,
            maintain_offset=True,
            target_list=[node.nodeName() for node in pm.orientConstraint(constraint, q=1, tl=1)],
            constrained_node=get_constrained_node(constraint).nodeName(),
            interpType=constraint.interpType.get(),
            parent=parent
        )
    elif constraint_type == 'scaleConstraint':
        data = CustomConstraint(
            name=constraint_name,
            constraint_type=constraint_type,
            maintain_offset=True,
            target_list=[node.nodeName() for node in pm.scaleConstraint(constraint, q=1, tl=1)],
            constrained_node=get_constrained_node(constraint).nodeName(),
            parent=parent
        )
    elif constraint_type == 'geometryConstraint':
        data = CustomConstraint(
            name=constraint_name,
            constraint_type=constraint_type,
            target_list=[node.nodeName() for node in pm.geometryConstraint(constraint, q=1, tl=1)],
            constrained_node=get_constrained_node(constraint).nodeName(),
            parent=parent
        )
    elif constraint_type == 'aimConstraint':
        data = CustomConstraint(
            name=constraint_name,
            constraint_type=constraint_type,
            maintain_offset=True,
            target_list=[node.nodeName() for node in pm.aimConstraint(constraint, q=1, tl=1)],
            constrained_node=get_constrained_node(constraint).nodeName(),
            worldUpType=constraint.worldUpType.get(),
            worldUpVector=constraint_name.worldUpVector.get()[0],
            upVector=constraint.upVector.get()[0],
            aimVector=constraint_name.aimVector.get()[0],
            parent=parent
        )
        connected = pm.listConnections(f'{constraint_name}.worldUpMatrix', s=1, d=0, scn=1, plugs=0)
        if connected:
            data['worldUpObject'] = connected[0]
        return data
    else:
        pass
        # self.logger.info(f"Warning: Constraint type '{constraint_type}' not supported. skipping...")
    return data



def enact_constraint(data):
    constraint_node = None
    targets = [pm.PyNode(obj) for obj in data.target_list]
    constrained_node = pm.PyNode(data.constrained_node)
    if data.constraint_type == 'parentConstraint':
        constraint_node = pm.parentConstraint(*targets, constrained_node, mo=data.maintain_offset)
    elif data.constraint_type == 'pointConstraint':
        constraint_node = pm.pointConstraint(*targets, constrained_node, mo=data.maintain_offset)
    elif data.constraint_type == 'scaleConstraint':
        constraint_node = pm.scaleConstraint(*targets, constrained_node, mo=data.maintain_offset)
    ### Still more constraints to add!
    if data.parent:
        if pm.objExists(data.parent):
            constraint_node.setParent(pm.PyNode(data.parent))
    if data.interpType:
        constraint_node.interpType.set(data.interpType)
    pm.rename(constraint_node, data.name)
    return constraint_node



def create_constraint_data_from_dict(constraint_dict):
    constraint_data = CustomConstraint(**constraint_dict)
    return constraint_data



def remove_constraint(constraint_name, custom_constraint_list):
    for item in custom_constraint_list:
        if not item['name'] == constraint_name:
            continue
        custom_constraint_list.remove(item)
        break
    return custom_constraint_list



def check_for_constraint(constraint_node):
    pass
