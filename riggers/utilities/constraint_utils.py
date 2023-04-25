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



def create_constraint(constraint_type, *transforms, **kwargs):
    name = kwargs.pop('name', None)
    parent_name = kwargs.pop('parent', None)
    interpolation_type = kwargs.pop('interpType', None)
    targets = [pm.PyNode(obj) for obj in transforms]
    clean_kwargs = dict()

    for key in kwargs:
        clean_kwargs[str(key)] = kwargs[key]
    short_name = pm.__dict__[constraint_type](*targets, **clean_kwargs)[-1]
    long_names = pm.ls(short_name, long=True)
    constraint_name = long_names[-1]
    constraint_node = pm.PyNode(constraint_name)
    if parent_name:
        parent = pm.PyNode(parent_name)
        get_parent = constraint_node.getParent()
        if get_parent is None or get_parent != parent:
            constraint_node.setParent(parent)
    if interpolation_type:
        constraint_node.interpType.set(interpolation_type)

    return constraint_node
