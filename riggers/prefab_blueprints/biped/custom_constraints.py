# Title: custom_constraints.py
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


'''@dataclass
class CustomConstraintCreatorInput:
    driver_part_name: str
    driver_node_name: str
    driven_part_name: str
    driven_node_name: str
    match_transform: bool
    constraint_type: str'''

@dataclass
class CustomConstraintInput:
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



inputs = [
    CustomConstraintInput(name='x1',
                          constraint_type='parentConstraint',
                          target_list=['SubRoot_CTRL'],
                          constrained_node='Cog_CONNECTOR'),
    CustomConstraintInput(name='x2',
                          constraint_type='parentConstraint',
                          target_list=['Cog_CTRL'],
                          constrained_node='M_Spine_CONNECTOR'),
    CustomConstraintInput(name='x3',
                          constraint_type='parentConstraint',
                          target_list=['M_IkChest_CTRL'],
                          constrained_node='M_Neck_CONNECTOR'),
    CustomConstraintInput(name='x4',
                          constraint_type='parentConstraint',
                          target_list=['M_IkChest_CTRL'],
                          constrained_node='L_Clavicle_CONNECTOR'),
    CustomConstraintInput(name='x5',
                          constraint_type='parentConstraint',
                          target_list=['M_IkChest_CTRL'],
                          constrained_node='R_Clavicle_CONNECTOR'),
    CustomConstraintInput(name='x6',
                          constraint_type='parentConstraint',
                          target_list=['L_ClavicleEnd_BIND'],
                          constrained_node='L_Arm_CONNECTOR'),
    CustomConstraintInput(name='x7',
                          constraint_type='parentConstraint',
                          target_list=['R_ClavicleEnd_BIND'],
                          constrained_node='R_Arm_CONNECTOR'),
    CustomConstraintInput(name='x8',
                          constraint_type='parentConstraint',
                          target_list=['L_Hand_blend_JNT'],
                          constrained_node='L_Hand_CONNECTOR'),
    CustomConstraintInput(name='x9',
                          constraint_type='parentConstraint',
                          target_list=['R_Hand_blend_JNT'],
                          constrained_node='R_Hand_CONNECTOR'),
    CustomConstraintInput(name='x10',
                          constraint_type='parentConstraint',
                          target_list=['M_IkPelvis_CTRL'],
                          constrained_node='L_Leg_CONNECTOR'),
    CustomConstraintInput(name='x11',
                          constraint_type='parentConstraint',
                          target_list=['M_IkPelvis_CTRL'],
                          constrained_node='R_Leg_CONNECTOR'),
    CustomConstraintInput(name='x12',
                          constraint_type='parentConstraint',
                          target_list=['L_IkFoot_CTRL'],
                          constrained_node='L_FootRollSoleHeel_JNT_OFFSET'),
    CustomConstraintInput(name='x13',
                          constraint_type='parentConstraint',
                          target_list=['R_IkFoot_CTRL'],
                          constrained_node='R_FootRollSoleHeel_JNT_OFFSET'),
    CustomConstraintInput(name='x14',
                          constraint_type='parentConstraint',
                          target_list=['L_Foot_blend_JNT'],
                          constrained_node='L_Tarsus_BIND_buffer'),
    CustomConstraintInput(name='x15',
                          constraint_type='parentConstraint',
                          target_list=['R_Foot_blend_JNT'],
                          constrained_node='R_Tarsus_BIND_buffer'),
    CustomConstraintInput(name='x16',
                          constraint_type='parentConstraint',
                          target_list=['L_FkFoot_CTRL'],
                          constrained_node='L_FkFootSpace'),
    CustomConstraintInput(name='x17',
                          constraint_type='parentConstraint',
                          target_list=['R_FkFoot_CTRL'],
                          constrained_node='R_FkFootSpace'),
    CustomConstraintInput(name='x18',
                          constraint_type='parentConstraint',
                          target_list=['L_FootRollTarsus_JNT'],
                          constrained_node='L_Leg_IKH'),
    CustomConstraintInput(name='x19',
                          constraint_type='parentConstraint',
                          target_list=['R_FootRollTarsus_JNT'],
                          constrained_node='R_Leg_IKH'),
    CustomConstraintInput(name='x20',
                          constraint_type='parentConstraint',
                          target_list=['L_FootRollTarsus_JNT'],
                          constrained_node='L_Foot_IKH'),
    CustomConstraintInput(name='x21',
                          constraint_type='parentConstraint',
                          target_list=['R_FootRollTarsus_JNT'],
                          constrained_node='R_Foot_IKH'),
]



########################################################################################################################
########################################################################################################################
########################################################################################################################

def get_constrained_node(self, constraint):
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



def get_constraint_data(self, constraint):
    constraint_name = constraint.nodeName()
    constraint_type = constraint.nodeType()
    parent = constraint.getParent()
    if constraint_type == 'pointConstraint':
        return dict(
            name=constraint_name,
            constraint_type=constraint_type,
            mo=True,
            target_list=pm.pointConstraint(constraint_name, q=True, tl=True),
            constrained_node=self.get_constrained_node(constraint),
            parent=parent
        )
    elif constraint_type == 'parentConstraint':
        return dict(
            name=constraint_name,
            constraint_type=constraint_type,
            mo=True,
            target_list=pm.parentConstraint(constraint, q=True, tl=True),
            constrained_node=self.get_constrained_node(constraint),
            interpType=constraint.interpType.get(),
            parent=parent
        )
    elif constraint_type == 'orientConstraint':
        return dict(
            name=constraint_name,
            constraint_type=constraint_type,
            mo=True,
            target_list=pm.orientConstraint(constraint, q=True, tl=True),
            constrained_node=self.get_constrained_node(constraint),
            interpType=constraint.interpType.get(),
            parent=parent
        )
    elif constraint_type == 'scaleConstraint':
        return dict(
            name=constraint_name,
            constraint_type=constraint_type,
            mo=True,
            target_list=pm.scaleConstraint(constraint, q=True, tl=True),
            interpType=None,
            constrained_node=self.get_constrained_node(constraint),
            parent=parent
        )
    elif constraint_type == 'geometryConstraint':
        return dict(
            name=constraint_name,
            constraint_type=constraint_type,
            target_list=pm.geometryConstraint(constraint, q=True, tl=True),
            interpType=None,
            constrained_node=self.get_constrained_node(constraint),
            parent=parent
        )
    elif constraint_type == 'aimConstraint':
        data = dict(
            name=constraint_name,
            constraint_type=constraint_type,
            mo=True,
            target_list=pm.aimConstraint(constraint, q=True, tl=True),
            interpType=None,
            constrained_node=self.get_constrained_node(constraint),
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
        #self.logger.info(f"Warning: Constraint type '{constraint_type}' not supported. skipping...")



def create_constraint(self, constraint_type, *transforms, **kwargs):
    name = kwargs.pop('name', None)
    parent_name = kwargs.pop('parent', None)
    interpolation_type = kwargs.pop('interpType', None)
    targets = [self.get_selection_string(x) for x in transforms]
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
