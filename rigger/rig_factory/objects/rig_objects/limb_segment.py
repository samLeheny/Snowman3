import copy
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
import Snowman3.rigger.rig_factory.utilities.node_utilities.ik_handle_utilities as iks
import Snowman3.rigger.rig_factory.utilities.joint_volume_utilities as jvu
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory as rig_factory


class LimbSegment(Transform):

    joints = ObjectListProperty(
        name='joints'
    )

    handles = ObjectListProperty(
        name='handles'
    )

    nurbs_curve = ObjectProperty(
        name='nurbs_curve'
    )

    owner = ObjectProperty(
        name='owner'
    )

    joint_count = DataProperty(
        name='joint_count',
        default_value=6
    )

    new_twist_system = DataProperty(
        name='new_twist_system',
        default_value=True
    )

    ignore_parent_twist = DataProperty(
        name='ignore_parent_twist',
        default_value=False
    )

    start_joint = ObjectProperty(
        name='start_joint'
    )

    end_joint = ObjectProperty(
        name='end_joint'
    )

    matrices = []

    def __init__(self, **kwargs):
        super(LimbSegment, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        owner = kwargs.get('owner')
        if not owner:
            raise Exception('You must provide an "owner" keyword argument')
        matrices = kwargs.pop('matrices', [])
        if len(matrices) != 2:
            raise Exception('You must provide exactly two matrices')
        this = super(LimbSegment, cls).create(**kwargs)
        controller = this.controller

        start_joint = this.start_joint
        end_joint = this.end_joint
        new_twist_system = this.new_twist_system
        ignore_parent_twist = this.ignore_parent_twist
        segment_name = this.segment_name
        size = this.size
        side = this.side
        owner = this.owner
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

        side_segment_length = segment_length * -1 if side == 'right' else segment_length

        # base control
        base_handle = owner.create_handle(
            handle_type=GroupedHandle,
            segment_name='{0}Base'.format(segment_name),
            shape='circle',
            matrix=start_matrix
        )
        base_handle.multiply_shape_matrix(Matrix([0.0, side_segment_length/size, 0.0]))

        # end control
        end_handle = owner.create_handle(
            handle_type=GroupedHandle,
            segment_name='{0}End'.format(segment_name),
            shape='circle',
            matrix=flipped_end_matrix
        )
        end_handle.multiply_shape_matrix(Matrix([0.0, side_segment_length/size*-1.0, 0.0]))

        # center control
        center_handle = owner.create_handle(
            handle_type=GroupedHandle,
            segment_name=segment_name,
            shape='ball',
            size=size,
            matrix=center_matrix,
            functionality_name=this.functionality_name
        )

        # base tangent
        base_tangent_transform = base_handle.create_child(
            Transform,
            segment_name='{0}BaseTangent'.format(segment_name),
            matrix=curve_points[1]
        )

        # end tangent
        end_tangent_transform = end_handle.create_child(
            Transform,
            segment_name='{0}EndTangent'.format(segment_name),
            matrix=curve_points[3]
        )

        # create nurbsCurve
        nurbs_curve_transform = this.create_child(
            Transform,
            segment_name='{0}Spline'.format(segment_name),
        )
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)
        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=3,
            segment_name=segment_name,
            positions=curve_points
        )

        # curve info
        curve_info = this.create_child(
            DependNode,
            segment_name='{0}Segment'.format(segment_name),
            node_type='curveInfo',

        )

        # scale
        scale_divide = this.create_child(
            DependNode,
            segment_name='{0}Segment'.format(segment_name),
            node_type='multiplyDivide'
        )
        scale_divide.plugs['operation'].set_value(2)
        curve_info.plugs['arcLength'].connect_to(
            scale_divide.plugs['input1X'],
        )
        curve_info.plugs['arcLength'].connect_to(
            scale_divide.plugs['input1Y'],
        )
        curve_info.plugs['arcLength'].connect_to(
            scale_divide.plugs['input1Z'],
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(
            curve_info.plugs['inputCurve'],
        )
        owner.scale_multiply_transform.plugs['scale'].connect_to(
            scale_divide.plugs['input2'],
        )
        length_divide = this.create_child(
            DependNode,
            segment_name='{0}BendyLength'.format(segment_name),
            node_type='multiplyDivide',
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(
            (this.joint_count - 1) * -1
            if side == 'right' else
            this.joint_count - 1
        )
        scale_divide.plugs['output'].connect_to(
            length_divide.plugs['input1'],
        )

        # drive curve points using controls
        curve_control_transforms = [
            base_handle,
            base_tangent_transform,
            center_handle,
            end_tangent_transform,
            end_handle
        ]
        for i, transform in enumerate(curve_control_transforms):
            locator = transform.create_child(Locator)
            locator.plugs['visibility'].set_value(False)
            locator.plugs['worldPosition'].element(0).connect_to(nurbs_curve.plugs['controlPoints'].element(i))

        # create twist joints
        segment_joints = []
        joint_parent = this.start_joint
        joint_spacing_vector = length_vector / this.joint_count
        for i in range(this.joint_count):
            index_character = rig_factory.index_dictionary[i].title()
            matrix = copy.copy(matrices[0])
            matrix.set_translation(matrix.get_translation() + (joint_spacing_vector*i))
            joint = joint_parent.create_child(
                Joint,
                segment_name='{0}Secondary{1}'.format(segment_name, index_character),
                functionality_name='{0}WithTwist'.format(this.functionality_name),
                matrix=matrix
            )
            joint.zero_rotation()
            if i > 0:
                segment_joints[-1].plugs['scale'].connect_to(
                    joint.plugs['inverseScale'],
                )
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz'],
                keyable=False
            )
            segment_joints.append(joint)
            joint_parent = joint

        # create ik spline joints
        twist_joints = []
        joint_parent = this.start_joint
        for i in range(len(segment_joints)):
            index_character = rig_factory.index_dictionary[i].title()
            joint = joint_parent.create_child(
                Joint,
                segment_name='{0}Secondary{1}'.format(segment_name, index_character),
                matrix=segment_joints[i].get_matrix()
            )
            if i > 0:
                joint_parent.plugs['scale'].connect_to(
                    joint.plugs['inverseScale']
                )
                length_divide.plugs['outputY'].connect_to(
                    joint.plugs['translateY'],
                )
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz'],
                keyable=False
            )
            twist_joints.append(joint)
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz']
            )
            joint_parent = joint

        # drive joints using curve
        spline_ik_handle = iks.create_spline_ik(
            twist_joints[0],
            twist_joints[-1],
            nurbs_curve,
            side=side,
            world_up_object=this.start_joint if new_twist_system else base_handle,
            world_up_object_2=this.start_joint if new_twist_system else end_handle,
            advanced_twist=True
        )

        spline_ik_handle.plugs['v'].set_value(0)
        controller.create_point_constraint(
            base_handle,
            twist_joints[0],
            mo=False
        )

        # drive segment_joints using twist_joints + twist reader
        twist_plugs = []
        if new_twist_system:
            twist_plugs = get_twist_plugs(
                part=this,
                start=start_joint,
                end=end_joint,
                side=side,
                segment_name=segment_name,
                count=this.joint_count,
                ignore_parent_twist=ignore_parent_twist,
            )
        for i in range(len(segment_joints)):
            cns = controller.create_parent_constraint(
                twist_joints[i],
                segment_joints[i],
            )
            if this.new_twist_system:
                twist_plugs[i].connect_to(cns.plugs['target'].element(0).child(10).child(1))

            # Only connect scaleY as there are connections into scaleX and scaleZ from pma nodes
            twist_joints[i].plugs['scaleY'].connect_to(segment_joints[i].plugs['scaleY'])
            twist_joints[i].plugs['drawStyle'].set_value(2)

        # hide curve and ik handle
        nurbs_curve.plugs['visibility'].set_value(False)
        spline_ik_handle.plugs['visibility'].set_value(False)

        # make plugs keyable
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

        this.joints = segment_joints
        this.handles = [base_handle, center_handle, end_handle]
        this.nurbs_curve = nurbs_curve
        return this

    def setup_scale_joints(self):

        auto_volume_plug = self.create_plug(
            'AutoVolume',
            at='double',
            dv=1.0,
            k=True,
            min=0.0,
            max=10.0
        )
        min_auto_volume_plug = self.create_plug(
            'MinAutoVolume',
            at='double',
            dv=-0.5,
            k=True
        )
        max_auto_volume_plug = self.create_plug(
            'MaxAutoVolume',
            at='double',
            dv=0.5,
            k=True
        )
        base_handle, center_handle, end_handle = self.handles

        base_scale_x_plug = base_handle.create_plug(
            'EndScaleX',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )
        base_scale_z_plug = base_handle.create_plug(
            'EndScaleZ',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )
        end_scale_x_plug = end_handle.create_plug(
            'EndScaleX',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )
        end_scale_z_plug = end_handle.create_plug(
            'EndScaleZ',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        for i, handle in enumerate([base_handle, center_handle, end_handle]):
            segment_character = rig_factory.index_dictionary[i].upper()
            paremeter_plug = handle.create_plug(
                'parameter_driver',
                at='double',
                dv=0.0
            )
            tweak_getter = handle.create_child(
                Locator,
                segment_name='%sGetter%s' % (self.segment_name, segment_character)
            )
            nearest_point = handle.create_child(
                DependNode,
                node_type='nearestPointOnCurve'
            )
            tweak_getter.plugs['visibility'].set_value(False)
            self.nurbs_curve.plugs['worldSpace'].element(0).connect_to(nearest_point.plugs['inputCurve'])
            tweak_getter.plugs['worldPosition'].element(0).connect_to(nearest_point.plugs['inPosition'])
            nearest_point.plugs['parameter'].connect_to(paremeter_plug)
        span_segment = float(self.nurbs_curve.plugs['spans'].get_value()) / (len(self.joints))
        scale_x_secondary_plugs = jvu.generate_distribution_plugs(
            self.nurbs_curve,
            [span_segment * i for i in range(len(self.joints))],
            [
                base_handle.plugs['sx'],
                center_handle.plugs['sx'],
                end_handle.plugs['sx']
            ],
            'SecondarySX%s' % self.segment_name,
            subtract_value=1.0
        )
        scale_z_secondary_plugs = jvu.generate_distribution_plugs(
            self.nurbs_curve,
            [span_segment * i for i in range(len(self.joints))],
            [
                base_handle.plugs['sz'],
                center_handle.plugs['sz'],
                end_handle.plugs['sz']
            ],
            'SecondarySZ%s' % self.segment_name,
            subtract_value=1.0
        )
        scale_x_plugs = jvu.generate_distribution_plugs(
            self.nurbs_curve,
            [span_segment * i for i in range(len(self.joints))],
            [
                base_scale_x_plug,
                end_scale_x_plug
            ],
            'SX%s' % self.segment_name,
            subtract_value=1.0,
            tangent_type=0
        )
        scale_z_plugs = jvu.generate_distribution_plugs(
            self.nurbs_curve,
            [span_segment * i for i in range(len(self.joints))],
            [
                base_scale_z_plug,
                end_scale_z_plug
            ],
            'SZ%s' % self.segment_name,
            subtract_value=1.0,
            tangent_type=0
        )
        squash_plugs = jvu.generate_volume_plugs(
            self.nurbs_curve,
            [span_segment * i for i in range(len(self.joints))]
        )
        if not len(self.joints) == len(scale_x_plugs):
            raise Exception('Mismatched scale x plugs')
        if not len(self.joints) == len(scale_z_plugs):
            raise Exception('Mismatched scale z plugs')
        if not len(self.joints) == len(scale_x_secondary_plugs):
            raise Exception('Mismatched scale x secondary plugs')
        if not len(self.joints) == len(scale_z_secondary_plugs):
            raise Exception('Mismatched scale z_secondary plugs')
        if not len(self.joints) == len(squash_plugs):
            raise Exception('Mismatched squash plugs')
        for i in range(len(self.joints)):
            index_character = rig_factory.index_dictionary[i].upper()
            add_default = self.create_child(
                DependNode,
                segment_name='%sAddDefault%s' % (index_character, self.segment_name),
                node_type='plusMinusAverage'
            )
            squash_plugs[i][0].connect_to(add_default.plugs['input2D'].element(0).child(0))
            squash_plugs[i][1].connect_to(add_default.plugs['input2D'].element(0).child(1))
            scale_x_secondary_plugs[i].connect_to(add_default.plugs['input2D'].element(1).child(0))
            scale_z_secondary_plugs[i].connect_to(add_default.plugs['input2D'].element(1).child(1))
            scale_x_plugs[i].connect_to(add_default.plugs['input2D'].element(2).child(0))
            scale_z_plugs[i].connect_to(add_default.plugs['input2D'].element(2).child(1))
            add_default.plugs['input2D'].element(3).child(0).set_value(1.0)
            add_default.plugs['input2D'].element(3).child(1).set_value(1.0)
            add_default.plugs['output2D'].child(0).connect_to(self.joints[i].plugs['sx'])
            add_default.plugs['output2D'].child(1).connect_to(self.joints[i].plugs['sz'])

        self.owner.scale_multiply_transform.plugs['scaleY'].connect_to(self.nurbs_curve.plugs['GlobalScale'])
        auto_volume_plug.connect_to(self.nurbs_curve.plugs['AutoVolume'])
        min_auto_volume_plug.connect_to(self.nurbs_curve.plugs['MinAutoVolume'])
        max_auto_volume_plug.connect_to(self.nurbs_curve.plugs['MaxAutoVolume'])
        root = self.owner.get_root()
        root.add_plugs(
            auto_volume_plug
        )


def get_twist_plugs(part, start, end, side, segment_name, count, ignore_parent_twist):
    full_twist_plug = create_twist_reader(
        part=part,
        start=start,
        end=end,
        side=side,
        segment_name=segment_name,
    )

    # twist per joint
    twist_plugs_nodes = []
    for i in range(count):
        x = full_twist_plug.multiply(float(i) / count)
        twist_plugs_nodes.append(x)

    # twist minus start joint twist
    if ignore_parent_twist:
        parent_twist_plug = create_twist_reader(
            part=part,
            start=start.parent,
            end=start,
            side=side,
            segment_name='{}ParentTwist'.format(segment_name),
        )
        for i in range(count):
            negate_mdn = parent_twist_plug.multiply(1.0 - (float(i) / count))
            twist_plugs_nodes[i] = twist_plugs_nodes[i].subtract(negate_mdn)

    return twist_plugs_nodes


def create_twist_reader(part, start, end, side, segment_name):
    aimVec = [0, 1, 0] if side == 'left' else [0, -1, 0]

    # top group
    twstGrp = part.create_child(
        Transform,
        segment_name=segment_name,
        differentiation_name='TwistReader',
        matrix=end.get_matrix()
    )
    part.controller.create_parent_constraint(
        start,
        twstGrp,
        mo=True
    )

    # end child
    end_child = [x for x in end.children if isinstance(x, Transform)][0]

    # find aim location
    end_vec = end.get_translation()
    end_child_vec = end_child.get_translation()
    vec = end_child_vec - end_vec
    pos = end_vec + (vec * 1.5)

    # aim
    aimGrp = part.create_child(
        Transform,
        segment_name=segment_name,
        differentiation_name='TwistReaderAim',
        matrix=end.get_matrix().set_translation(pos),
        parent=twstGrp,
    )
    part.controller.create_parent_constraint(
        end,
        aimGrp,
        mo=True
    )

    # twist zero
    twstZro = part.create_child(
        Transform,
        segment_name=segment_name,
        differentiation_name='TwistReaderZro',
        matrix=end.get_matrix().set_translation(end_child.get_translation()),
        parent=twstGrp,
    )
    part.controller.create_parent_constraint(
        end,
        twstZro,
        sr=['x', 'y', 'z'],
    )
    part.controller.create_aim_constraint(
        aimGrp,
        twstZro,
        worldUpType="none",
        aim=aimVec,
        mo=False
    )

    # twist reference
    twstRef = part.create_child(
        Transform,
        segment_name=segment_name,
        differentiation_name='TwistReaderRef',
        matrix=twstZro.get_matrix(),
        parent=twstGrp,
    )
    part.controller.create_parent_constraint(
        end,
        twstRef,
        mo=True
    )

    # twist reader
    twst = part.create_child(
        Transform,
        segment_name=segment_name,
        differentiation_name='TwistReaderSrt',
        matrix=twstZro.get_matrix(),
        parent=twstZro
    )
    cns = part.controller.create_orient_constraint(
        twstRef,
        twstZro,
        twst
    )
    cns.plugs['interpType'].set_value(2)

    # full twist
    full_twist_plug = twst.plugs['rotateY'].multiply(2.0)

    return full_twist_plug
