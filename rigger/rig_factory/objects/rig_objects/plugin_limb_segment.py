import copy
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory as rig_factory


class PluginLimbSegment(Transform):

    joints = ObjectListProperty( name='joints' )
    handles = ObjectListProperty( name='joints' )
    nurbs_curve = ObjectProperty( name='nurbs_curve' )
    owner = ObjectProperty( name='owner' )
    spline_node = ObjectProperty( name='spline_node' )
    joint_count = DataProperty( name='joint_count', default_value=6 )

    matrices = []

    def __init__(self, **kwargs):
        super(PluginLimbSegment, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        owner = kwargs.get('owner')
        if not owner:
            raise Exception('You must provide an "owner" keyword argument')
        matrices = kwargs.pop('matrices', [])
        if len(matrices) != 2:
            raise Exception('You must provide exactly two matrices')
        this = super(PluginLimbSegment, cls).create(**kwargs)
        segment_name = this.segment_name
        size = this.size
        side = this.side
        owner = this.hierarchy_parent
        root = owner.get_root()
        positions = [x.get_translation() for x in matrices]
        start_matrix, end_matrix = matrices
        flipped_end_matrix = copy.copy(start_matrix)
        flipped_end_matrix.set_translation(end_matrix.get_translation())
        center_matrix = copy.copy(start_matrix)
        length_vector = positions[1] - positions[0]
        segment_vector = length_vector / 4
        segment_length = segment_vector.mag()
        curve_points = [positions[0] + (segment_vector * x) for x in range(5)]
        center_matrix.set_translation(curve_points[2])
        base_handle = owner.create_handle(
            handle_type=GroupedHandle,
            segment_name='{0}Base'.format(segment_name),
            shape='circle',
            matrix=start_matrix
        )
        side_segment_length = segment_length * -1 if side == 'right' else segment_length
        base_handle.multiply_shape_matrix(Matrix([0.0, side_segment_length/size, 0.0]))
        end_handle = owner.create_handle(
            handle_type=GroupedHandle,
            segment_name='{0}End'.format(segment_name),
            shape='circle',
            matrix=flipped_end_matrix
        )
        end_handle.multiply_shape_matrix(Matrix([0.0, side_segment_length/size*-1.0, 0.0]))
        center_handle = owner.create_handle(
            handle_type=GroupedHandle,
            segment_name=segment_name,
            shape='ball',
            size=size,
            matrix=center_matrix,
            functionality_name=this.functionality_name
        )
        base_tangent_transform = base_handle.create_child(
            Transform,
            segment_name='{0}BaseTangent'.format(segment_name),
            matrix=curve_points[1]
        )
        end_tangent_transform = end_handle.create_child(
            Transform,
            segment_name='{0}EndTangent'.format(segment_name),
            matrix=curve_points[3]
        )
        spline_node = this.create_child(
            DependNode,
            node_type='rigSpline',
            segment_name='{0}Spline'.format(segment_name),
        )
        start_point = matrices[0].get_translation()
        end_point = matrices[-1].get_translation()
        spline_node.plugs['originalLength'].set_value((end_point-start_point).mag())
        spline_node.plugs['matrixType'].set_value(1)
        spline_node.plugs['distributionType'].set_value(2)
        spline_node.plugs['squashType'].set_value(2)
        spline_node.plugs['scaleType'].set_value(0)
        spline_node.plugs['twistType'].set_value(0)
        spline_node.plugs['degree'].set_value(3)
        spline_node.plugs['sourceUpVector'].set_value(5 if this.side == 'right' else 2)  # Z
        spline_node.plugs['upVector'].set_value(1 if this.side == 'right' else 0)  # Z
        spline_node.plugs['aimVector'].set_value(1 if this.side == 'right' else 0)  # Y
        spline_node.plugs['fitCurve'].set_value(False)
        spline_node.plugs['jointsTranslateOnSurface'].set_value(False)
        spline_node.plugs['projectCurveOnSurface'].set_value(False)
        spline_node.plugs['jointsOrientToSurface'].set_value(False)
        curve_control_transforms = [
            base_handle,
            base_tangent_transform,
            center_handle,
            end_tangent_transform,
            end_handle
        ]

        segment_joints = []
        joint_parent = this
        joint_spacing_vector = length_vector / this.joint_count
        for i in range(this.joint_count):
            index_character = rig_factory.index_dictionary[i].title()
            matrix = copy.copy(matrices[0])
            matrix.set_translation(matrix.get_translation() + (joint_spacing_vector*i))
            joint = joint_parent.create_child(
                Joint,
                segment_name='{0}Secondary{1}'.format(segment_name, index_character),
                matrix=matrix
            )
            joint.zero_rotation()
            if i > 0:
                segment_joints[-1].plugs['scale'].connect_to(
                    joint.plugs['inverseScale'],
                )

            blend_x = joint_parent.create_child(
                DependNode,
                node_type='blendWeighted',
                segment_name='{0}SecondaryX{1}'.format(segment_name, index_character),
            )
            blend_y = joint_parent.create_child(
                DependNode,
                node_type='blendWeighted',
                segment_name='{0}SecondaryY{1}'.format(segment_name, index_character),
            )
            blend_z = joint_parent.create_child(
                DependNode,
                node_type='blendWeighted',
                segment_name='{0}SecondaryZ{1}'.format(segment_name, index_character),
            )

            spline_node.plugs['outTranslate'].element(i).connect_to(joint.plugs['translate'])
            spline_node.plugs['outRotate'].element(i).connect_to(joint.plugs['jointOrient'])
            spline_node.plugs['outScale'].element(i).child(0).connect_to(blend_x.plugs['input'].element(0))
            spline_node.plugs['outScale'].element(i).child(1).connect_to(blend_y.plugs['input'].element(0))
            spline_node.plugs['outScale'].element(i).child(2).connect_to(blend_z.plugs['input'].element(0))
            blend_x.plugs['output'].connect_to(joint.plugs['sx'])
            blend_y.plugs['output'].connect_to(joint.plugs['sy'])
            blend_z.plugs['output'].connect_to(joint.plugs['sz'])

            parameter_plug = joint.create_plug('Parameter', at='double')
            parameter_plug.set_value(1.0 / (this.joint_count - 1) * i)
            parameter_plug.connect_to(spline_node.plugs['inParameters'].element(i))

            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz'],
                keyable=False
            )
            segment_joints.append(joint)
            joint_parent = joint

        for i, transform in enumerate(curve_control_transforms):
            transform.plugs['worldMatrix'].element(0).connect_to(spline_node.plugs['inMatrices'].element(i))

        for i in range(len(segment_joints)):
            this_position = segment_joints[i].get_translation()
            if i == len(segment_joints) - 1:
                other_position = segment_joints[i - 1].get_translation()
            else:
                other_position = segment_joints[i + 1].get_translation()
            spline_node.plugs['segmentLengths'].element(i).set_value((this_position - other_position).mag())

        root.add_plugs(
            base_handle.plugs['rx'],
            base_handle.plugs['ry'],
            base_handle.plugs['rz'],
            base_handle.plugs['sx'],
            base_handle.plugs['sz'],
            end_handle.plugs['rx'],
            end_handle.plugs['ry'],
            end_handle.plugs['rz'],
            end_handle.plugs['sx'],
            end_handle.plugs['sz'],
            center_handle.plugs['tx'],
            center_handle.plugs['ty'],
            center_handle.plugs['tz'],
            center_handle.plugs['sx'],
            center_handle.plugs['sz']
        )


        auto_volume_plug = this.create_plug(
            'AutoVolume',
            at='double',
            dv=1.0,
            k=True,
            min=0.0,
            max=10.0
        )
        min_auto_volume_plug = this.create_plug(
            'MinAutoVolume',
            at='double',
            dv=-0.5,
            k=True
        )
        max_auto_volume_plug = this.create_plug(
            'MaxAutoVolume',
            at='double',
            dv=0.5,
            k=True
        )

        auto_volume_plug.connect_to(spline_node.plugs['squashFactor'])
        min_auto_volume_plug.connect_to(spline_node.plugs['squashMin'])
        max_auto_volume_plug.connect_to(spline_node.plugs['squashMax'])


        this.joints = segment_joints
        this.handles = [base_handle, center_handle, end_handle]
        this.spline_node = spline_node
        return this