import logging

import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.rig_objects.capsule import Capsule
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
import Snowman3.rigger.rig_factory.utilities.node_utilities.ik_handle_utilities as ikh_utils
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.rig_objects.guide_handle import GuideHandle


class SplineChainGuide(PartGuide):

    capsules = ObjectListProperty( name='capsules' )
    locators = ObjectListProperty( name='locators' )
    spline_joints = ObjectListProperty( name='spline_joints' )
    count = DataProperty( name='count', default_value=5 )
    joint_count = DataProperty( name='joint_count', default_value=9 )
    default_settings = dict( root_name='Chain', size=1.0, side='center', joint_count=9, count=5 )
    segment_names = DataProperty( name='segment_names' )
    up_handles = ObjectListProperty( name='up_handles' )
    base_handles = ObjectListProperty( name='base_handles' )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = SplineChain.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)

        nodes = cls.build_nodes(
            part=this,
            count=this.count,
            joint_count=this.joint_count,
            segment_names=this.segment_names,
            up_vector_indices=kwargs.pop('up_vector_indices', None),
            handle_positions=kwargs.get('handle_positions', None)
        )
        joints = nodes['joints']
        spline_joints = nodes['spline_joints']
        up_handles = nodes['up_handles']
        base_handles = nodes['base_handles']
        handles = nodes['handles']
        root = this.get_root()

        for up_handle in up_handles:
            root.add_plugs(
                [ up_handle.plugs['tx'],
                  up_handle.plugs['ty'],
                  up_handle.plugs['tz'] ]
            )
        for base_handle in base_handles:
            root.add_plugs(
                [ base_handle.plugs['tx'],
                  base_handle.plugs['ty'],
                  base_handle.plugs['tz'] ]
            )
        this.set_handles(handles)
        this.spline_joints = spline_joints
        this.up_handles = up_handles
        this.base_handles = base_handles
        this.joints = joints
        return this

    @staticmethod
    def build_nodes(
            part,
            count=5,
            joint_count=9,
            up_vector_indices=None,
            segment_names=None,
            handle_positions=None,
            degree=None
    ):
        if degree is None:
            if count < 3:
                degree = 1
            elif count < 4:
                degree = 2
            else:
                degree = 3
        controller = part.controller
        root = part.get_root()  # this should happen in create function
        side = part.side
        size = part.size
        root_name = part.root_name
        side_vectors = env.side_world_vectors[side]
        spacing = size * 5.0
        size_plug = part.plugs['size']
        joint_parent = part
        aim_vector = env.aim_vector
        up_vector = env.up_vector
        if up_vector_indices is None:
            up_vector_indices = [0]
        if handle_positions is None:
            handle_positions = dict()
        if side == 'right':
            aim_vector = [x * -1.0 for x in env.aim_vector]
            up_vector = [x * -1.0 for x in env.up_vector]
        joints = []
        handles = []
        locators = []
        up_handles = []
        base_handles = []
        segment_up_handles = []
        capsules = []
        up_handle_lines = dict()

        size_multiply = part.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='Size'
        )
        size_plug.connect_to(size_multiply.plugs['input1X'])
        size_plug.connect_to(size_multiply.plugs['input1Y'])
        size_multiply.plugs['input2X'].set_value(0.5)
        size_multiply.plugs['input2Y'].set_value(0.25)
        current_up_handle = None
        for i in range(count):
            if segment_names and i < len(segment_names):
                segment_name = segment_names[i]
            else:
                segment_name = rig_factory.index_dictionary[i].title()
            if i in up_vector_indices:
                up_handle = part.create_child(
                    GuideHandle,
                    index=len(up_handles),
                    segment_name=segment_name,
                    functionality_name='UpVector'
                )
                if up_handle.name not in handle_positions:
                    logging.getLogger('rig_build').info(
                        'SplineChainGuide: positions for "%s" not found' % up_handle.name
                    )
                position = handle_positions.get(
                    up_handle.name,
                    [0.0, spacing*i, spacing]
                )
                up_handle.plugs['translate'].set_value(position)
                up_handle.mesh.assign_shading_group(root.shaders[side].shading_group)  # Move to create function
                size_multiply.plugs['outputY'].connect_to(up_handle.plugs['size'])
                up_handles.append(up_handle)

                current_up_handle = up_handle
            segment_up_handles.append(current_up_handle)
            if i > 0:
                joint_parent = joints[i - 1]
            joint = joint_parent.create_child(
                Joint,
                segment_name=segment_name
            )
            handle = part.create_child(
                GuideHandle,
                segment_name=segment_name
            )
            position = handle_positions.get(handle.name, [0.0, spacing*i, 0.0])
            handle.plugs['translate'].set_value(position)

            index_character = rig_factory.index_dictionary[i].title()
            cone_x = joint.create_child(
                Cone,
                segment_name='%sConeX' % index_character,
                index=i,
                size=size,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                segment_name='%sConeY' % index_character,
                index=i,
                size=size,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                segment_name='%sConeZ' % index_character,
                index=i,
                size=size,
                axis=[0.0, 0.0, 1.0]
            )
            locator = joint.create_child(
                Locator
            )
            controller.create_point_constraint(
                handle,
                joint,
                mo=False
            )
            size_multiply.plugs['outputY'].connect_to(handle.plugs['size'])
            size_multiply.plugs['outputX'].connect_to(cone_x.plugs['size'])
            size_multiply.plugs['outputX'].connect_to(cone_y.plugs['size'])
            size_multiply.plugs['outputX'].connect_to(cone_z.plugs['size'])
            joint.plugs.set_values(
                drawStyle=2
            )
            cone_x.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_y.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_z.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            locator.plugs.set_values(
                visibility=False
            )
            locator.plugs['visibility'].set_value(False)
            handle.mesh.assign_shading_group(root.shaders[side].shading_group)  # Move to create function
            cone_x.mesh.assign_shading_group(root.shaders['x'].shading_group)  # Move to create function
            cone_y.mesh.assign_shading_group(root.shaders['y'].shading_group)  # Move to create function
            cone_z.mesh.assign_shading_group(root.shaders['z'].shading_group)  # Move to create function
            joints.append(joint)
            locators.append(locator)
            handles.append(handle)
            base_handles.append(handle)
        for i in range(count):
            up_handle = segment_up_handles[i]
            if i < count - 1:
                controller.create_aim_constraint(
                    handles[i + 1],
                    joints[i],
                    worldUpType='object',
                    worldUpObject=up_handle.get_selection_string(),
                    aimVector=aim_vector,
                    upVector=up_vector
                )
            else:
                controller.create_aim_constraint(
                    handles[i - 1],
                    joints[i],
                    worldUpType='object',
                    worldUpObject=up_handle,
                    aimVector=[x * -1 for x in aim_vector],
                    upVector=up_vector
                )
            if up_handle not in up_handle_lines:
                line = part.create_child(Line, index=i)
                locator_1 = locators[i]
                locator_2 = up_handle.create_child(Locator)
                locator_2.plugs.set_values(visibility=False)
                locator_1.plugs.set_values(visibility=False)
                locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
                locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
                up_handle_lines[up_handle] = line

        # this.locators = locators
        # this.capsules = capsules
        # this.base_handles = base_handles
        # root_name = this.root_name
        # handles = this.handles
        # spine_handles = handles[1:]
        # up_vector_handle = handles[0]

        matrices = [x.get_matrix() for x in joints]
        positions = [x.get_translation() for x in matrices]

        nurbs_curve_transform = part.create_child(
            Transform,
            segment_name='Spline'
        )
        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=degree,
            root_name=root_name,
            positions=positions
        )
        nurbs_curve.plugs['v'].set_value(False)
        curve_info = part.create_child(
            DependNode,
            segment_name='CurveInfo',
            node_type='curveInfo'
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])
        for i, base_handle in enumerate(base_handles):
            position_locator = locators[i]
            position_locator.plugs['worldPosition'].element(0).connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )
            position_locator.plugs['visibility'].set_value(False)
        length_divide = part.create_child(
            DependNode,
            segment_name='LengthDivide',
            node_type='multiplyDivide'
        )
        curve_info.plugs['arcLength'].connect_to(length_divide.plugs['input1X'])
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2X'].set_value(joint_count - 1)
        spline_joints = []
        joint_parent = base_handles[0]
        spline_locators = []
        for i in range(joint_count):
            index_character = rig_factory.index_dictionary[i].title()
            spline_joint = joint_parent.create_child(
                Joint,
                segment_name='%sSpline' % index_character,
            )
            spline_joints.append(spline_joint)
            spline_locator = spline_joint.create_child(
                Locator
            )
            spline_locator.plugs['visibility'].set_value(False)
            spline_locators.append(spline_locator)
            if i != 0:
                length_divide.plugs['outputX'].connect_to(spline_joint.plugs['t{0}'.format(env.aim_vector_axis)])
                capsule = part.create_child(
                    Capsule,
                    segment_name='Segment%s' % index_character,
                    size=size * 0.5
                )
                capsule.poly_cylinder.plugs['roundCap'].set_value(0)
                capsule.mesh.assign_shading_group(root.shaders[side].shading_group)  # Move to create function
                size_plug.connect_to(capsule.plugs['size'])
                locator_1 = spline_locators[i - 1]
                locator_2 = spline_locators[i]
                joint_1 = spline_joints[i - 1]
                joint_2 = spline_joints[i]
                locator_1.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position1'])
                locator_2.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position2'])
                controller.create_point_constraint(joint_1, joint_2, capsule)
                controller.create_aim_constraint(
                    joint_2,
                    capsule,
                    aimVector=env.aim_vector
                )
            cone_y = spline_joint.create_child(
                Cone,
                segment_name='%sAxisY' % index_character,
                axis=[0.0, 1.0, 0.0],
                size=size * 0.25
            )
            cone_y.poly_cone.plugs['subdivisionsAxis'].set_value(4)
            size_multiply.plugs['outputX'].connect_to(cone_y.plugs['size'])
            cone_y.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_y.mesh.assign_shading_group(root.shaders['black'].shading_group)  # Move to create function
            root.add_plugs(  # Move to create function
                [
                    spline_joint.plugs['rx'],
                    spline_joint.plugs['ry'],
                    spline_joint.plugs['rz']
                ],
                keyable=False,
                visible=False
            )
            spline_joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                radius=0.0,
                overrideRGBColors=True,
                overrideColorR=0.0,
                overrideColorG=0.0,
                overrideColorB=0.0
            )
            joint_parent = spline_joint
        if spline_joints:
            spline_ik_handle = ikh_utils.create_spline_ik(
                spline_joints[0],
                spline_joints[-1],
                nurbs_curve,
                world_up_object=up_handles[0],
                world_up_object_2=up_handles[0],
                up_vector=[0.0, 0.0, -1.0],
                up_vector_2=[0.0, 0.0, -1.0],
                world_up_type=4
            )
            spline_ik_handle.plugs['v'].set_value(False)

        all_handles = list(base_handles)
        all_handles.extend(up_handles)
        return dict(
            joints=joints,
            spline_joints=spline_joints,
            handles=all_handles,
            up_handles=up_handles,
            base_handles=base_handles,
            capsules=capsules,
            locators=locators
        )


    def get_blueprint(self):
        if self.toggle_class is None:
            raise Exception('You must subclass this and set the toggle_class')
        blueprint = super().get_blueprint()
        blueprint.update(dict(
            count=self.count,
            joint_count=self.joint_count
        ))
        return blueprint


    def get_toggle_blueprint(self):
        if self.toggle_class is None:
            raise Exception('You must subclass this and set the toggle_class')

        blueprint = super().get_toggle_blueprint()
        position_1 = self.handles[0].get_matrix().get_translation()
        position_2 = self.handles[1].get_matrix().get_translation()
        blueprint.update(
            joint_matrices=[list(x.get_matrix()) for x in self.spline_joints],
            matrices=[list(x.get_matrix()) for x in self.joints],
            up_vector=(position_2 - position_1).normalize().data
        )
        return blueprint


    def prepare_for_toggle(self):
        super().prepare_for_toggle()
        self.controller.snap_handles_to_mesh_positions(self.get_root())


class SplineChain(Part):
    """
    Added Part for consistency with other rig_factory objects
    Not intended for actual use
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        joint_matrices = kwargs.pop('joint_matrices', [])
        this = super().create(**kwargs)
        root_name = this.root_name
        joints = []
        spline_joint_parent = this.joint_group
        for i, matrix in enumerate(this.matrices):
            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_spline' % root_name,
                index=i,
                matrix=matrix
            )
            spline_joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                visibility=0.0
            )
            joints.append(spline_joint)
            spline_joint_parent = spline_joint
        this.joints = joints
        return this
