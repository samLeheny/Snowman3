import traceback
from math import cos, pi

from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
from Snowman3.rigger.rig_factory.objects.part_objects.part_array import PartArrayGuide, PartArray
from Snowman3.rigger.rig_factory.objects.creature_objects.feather_part import FeatherPart
from Snowman3.rigger.rig_factory.objects.creature_objects.feather_ribbon_part import FeatherRibbonPart
from Snowman3.rigger.rig_factory.objects.creature_objects.feather_simple_part import FeatherSimplePart
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm_bendy import BipedArmBendyGuide, BipedArmBendy
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm import BipedArmGuide, BipedArm
from Snowman3.rigger.rig_factory.objects.part_objects.fk_chain import FkChain
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator

import Snowman3.rigger.rig_math.vector as vec

from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory as rig_factory


class BaseWingGuide(PartArrayGuide):
    default_settings = {
        'root_name': 'Wing',
        'size': 1.0,
        'side': 'left',
        'primary_digit_count': 5,
        'secondary_digit_count': 5,
        'tertiary_digit_count': 5,
        'use_bendy_arm': False,
        'ribbon_joint_count': 10,
        'use_legacy_digit_aim': False,  # Legacy feathers aim at a linearly blended point, so rotationBlending moves the default orientation. RIG-3686
        'use_virtual_digit_length': True  # Use length to aim point as bend length, with some shortening to account for closer mesh divisions, to move feathers uniformly RIG-3686
    }
    primary_digit_count = DataProperty( name='primary_digit_count' )
    secondary_digit_count = DataProperty( name='secondary_digit_count' )
    tertiary_digit_count = DataProperty( name='tertiary_digit_count' )
    primary_length = DataProperty( name='primary_length', default_value=13.0 )
    secondary_length = DataProperty( name='secondary_length', default_value=10.0 )
    tertiary_length = DataProperty( name='tertiary_length', default_value=8.0 )
    use_bendy_arm = DataProperty( name='use_bendy_arm', default_value=False )
    digit_class = DataProperty( name='digit_class', default_value='FkChainGuide' )
    ribbon_joint_count = DataProperty( name='ribbon_joint_count', default_value=10 )
    use_legacy_digit_aim = DataProperty( name='use_legacy_digit_aim', default_value=False )
    use_virtual_digit_length = DataProperty( name='use_virtual_digit_length', default_value=True )

    def __init__(self, **kwargs):
        super(BaseWingGuide, self).__init__(**kwargs)
        self.toggle_class = BaseWing.__name__

    def create_members(self):
        if self.side not in ['left', 'right']:
            raise Exception('Invalid side "%s"' % self.side)
        limb_chain = self.create_part(
            BipedArmBendyGuide if self.use_bendy_arm else BipedArmGuide,
            root_name='%sLimb' % self.root_name,
            size=self.size * 2,
            side=self.side,
            count=5,
            create_bendy_hand=True,
            proxy=False
        )

        for i in range(self.primary_digit_count):
            digit = self.create_part(
                self.digit_class,
                root_name='%sDigit%s' % (self.root_name, rig_factory.index_dictionary[i].capitalize()),
                differentiation_name='Primary',
                size=self.size * 0.25,
                side=self.side,
                count=self.ribbon_joint_count,
                ribbon_joint_count=self.ribbon_joint_count,
                create_gimbals=False,
                create_tweaks=True,
                proxy=False
            )
            if self.use_bendy_arm:
                digit.set_hierarchy_parent(limb_chain.joints[15])  # Hard coded ints based on bendy segment counts
            else:
                digit.set_hierarchy_parent(limb_chain.joints[3])  # Hard coded ints based on arm joint count

        for i in range(self.secondary_digit_count):
            digit = self.create_part(
                self.digit_class,
                root_name='%sDigit%s' % (self.root_name, rig_factory.index_dictionary[i].capitalize()),
                differentiation_name='Secondary',
                size=self.size * 0.25,
                side=self.side,
                count=self.ribbon_joint_count,
                ribbon_joint_count=self.ribbon_joint_count,
                create_gimbals=False,
                create_tweaks=True,
                proxy=False
            )
            if self.use_bendy_arm:
                digit.set_hierarchy_parent(limb_chain.joints[8])  # Hard coded ints based on bendy segment counts
            else:
                digit.set_hierarchy_parent(limb_chain.joints[2])  # Hard coded ints based on arm joint count

        for i in range(self.tertiary_digit_count):
            digit = self.create_part(
                self.digit_class,
                root_name='%sDigit%s' % (self.root_name, rig_factory.index_dictionary[i].capitalize()),
                differentiation_name='Tertiary',
                size=self.size * 0.25,
                side=self.side,
                count=self.ribbon_joint_count,
                ribbon_joint_count=self.ribbon_joint_count,
                create_gimbals=False,
                create_tweaks=True,
                proxy=False
            )
            if self.use_bendy_arm:
                digit.set_hierarchy_parent(limb_chain.joints[1])  # Hard coded ints based on bendy segment counts
            else:
                digit.set_hierarchy_parent(limb_chain.joints[1])  # Hard coded ints based on arm joint count

        sm = -1.0 if self.side == 'right' else 1.0
        limb_chain.base_handles[0].plugs['translate'].set_value([1.0 * self.size * sm, 0.0, 0.0])
        limb_chain.base_handles[1].plugs['translate'].set_value([6.0 * self.size * sm, 0.0, 0.0])
        limb_chain.base_handles[2].plugs['translate'].set_value([16.0 * self.size * sm, 0.0, -5.0 * self.size])
        limb_chain.base_handles[3].plugs['translate'].set_value([26.0 * self.size * sm, 0.0, 0.0])
        limb_chain.base_handles[4].plugs['translate'].set_value([30.0 * self.size * sm, 0.0, -1.0 * self.size])
        limb_chain.up_handles[0].plugs['translate'].set_value([0.0, 0.0, -20.0 * self.size])
        self.calculate_positions()

    def calculate_positions(self):
        limb_chain = self.find_first_part(BipedArmGuide)
        if not limb_chain:
            self.controller.raise_warning(
                '%s was unable to find a %s in its member parts. unable to make connections.' % (
                    self.name,
                    limb_chain.__class__.__name__
                )
            )
            return
        if len(limb_chain.base_joints) != 5:
            self.controller.raise_warning(
                '%s found %s, but it had %s base joints. (it should have 5) Unable to calculate digit position' % (
                    self.name,
                    limb_chain.name,
                    len(limb_chain.base_joints)
                )
            )
            return
        if self.ribbon_joint_count < 2:
            self.controller.raise_warning(
                '%s has a ribbon_joint_count of %s. (it should not have less than 2)  Unable to calculate spacing.' % (
                    self,
                    self.ribbon_joint_count
                )
            )
            return

        primary_digits = find_digit_parts(self, differentiation_name='Primary')
        secondary_digits = find_digit_parts(self, differentiation_name='Secondary')
        tertiary_digits = find_digit_parts(self, differentiation_name='Tertiary')

        digit_lengths = [self.tertiary_length, self.tertiary_length, self.secondary_length, self.primary_length]
        for d, digits in enumerate([tertiary_digits, secondary_digits, primary_digits]):
            if digits:
                side_multiply = -1.0 if digits[0].side == 'right' else 1.0
                digit_count = len(digits)
                joint_1 = limb_chain.base_joints[d]
                joint_2 = limb_chain.base_joints[d + 1]
                joint_3 = limb_chain.base_joints[d + 2]
                vector_1 = vec.Vector(joint_1.get_matrix().data[2][0:3]) * -1.0
                vector_2 = vec.Vector(joint_2.get_matrix().data[2][0:3]) * -1.0
                vector_3 = vec.Vector(joint_3.get_matrix().data[2][0:3]) * -1.0
                start_vector = (vector_1 + vector_2).normalize() * side_multiply
                if d == 2:
                    end_vector = (joint_3.get_translation() - joint_2.get_translation()).normalize()
                else:
                    end_vector = (vector_2 + vector_3).normalize() * side_multiply
                for i, digit in enumerate(digits):
                    percentage = 1.0 / digit_count * i
                    digit_vector = (end_vector * percentage) + (start_vector * (1.0 - percentage))
                    start_offset = (joint_3.get_translation() - joint_2.get_translation()) * 1.0 / digit_count / 2
                    digit_position = start_offset + (joint_3.get_translation() * percentage) + (joint_2.get_translation() * (1.0 - percentage))
                    digit_length = (digit_lengths[d + 1] * percentage) + (digit_lengths[d] * (1.0 - percentage))
                    current_aim_position = digit_position + (digit_vector * (digit_length * self.size))
                    current_up_position = digit_position + vec.Vector([0.0, self.size * 4.0, 0.0])
                    base_handles = digit.base_handles
                    up_handle = digit.up_handles[0]
                    base_handles[0].plugs['translate'].set_value(digit_position)
                    base_handles[-1].plugs['translate'].set_value(current_aim_position)
                    set_even_spacing(base_handles)
                    up_handle.plugs['translate'].set_value(current_up_position)


class BaseWing(PartArray):
    aim_handles = ObjectListProperty(
        name='aim_handles'
    )
    use_legacy_digit_aim = DataProperty(
        name='use_legacy_digit_aim',
        default_value=True  # default for backwards compatibility
    )
    use_virtual_digit_length = DataProperty(
        name='use_virtual_digit_length',
        default_value=False  # default for backwards compatibility
    )

    def finish_create(self, **kwargs):
        limb_part = self.find_first_part(BipedArm, BipedArmBendy)
        if not limb_part:
            raise Exception('Limb not found. Unable to locate sub-parts of type: (BipedArm, BipedArmBendy)')
        if isinstance(limb_part, BipedArmBendy) and len(limb_part.limb_segments) != 3:
            raise Exception('BipedArmBendy does not have three bendy segments. Please set "create_bendy_hand" to True')

        # find feathers
        primary_digits = find_digit_parts(self, differentiation_name='Primary')
        secondary_digits = find_digit_parts(self, differentiation_name='Secondary')
        tertiary_digits = find_digit_parts(self, differentiation_name='Tertiary')

        # get inputs
        clavicle_joint = limb_part.base_joints[0]
        shoulder_joint = limb_part.base_joints[1]
        forearm_joint = limb_part.base_joints[2]
        wrist_joint = limb_part.base_joints[3]
        wrist_tip_joint = limb_part.base_joints[4]
        settings_handle = limb_part.settings_handle
        arm_joints = [clavicle_joint, shoulder_joint, forearm_joint, wrist_joint, wrist_tip_joint]
        root = self.get_root()
        aim_handles = []
        position_getters = []
        tertiary_vector = tertiary_digits[0].joints[-1].get_translation() - tertiary_digits[0].joints[0].get_translation()
        secondary_vector = secondary_digits[0].joints[-1].get_translation() - secondary_digits[0].joints[0].get_translation()
        primary_vector = primary_digits[0].joints[-1].get_translation() - primary_digits[0].joints[0].get_translation()
        primary_tip_vector = primary_digits[-1].joints[-1].get_translation() - primary_digits[-1].joints[0].get_translation()
        digit_groups = [tertiary_digits, secondary_digits, primary_digits, None]
        digit_vectors = [tertiary_vector, secondary_vector, primary_vector, primary_tip_vector]

        # Create plug to hide feather controls
        feather_plug = settings_handle.create_plug(
            'featherCtrlVis',
            at='long',
            min=0,
            max=1,
            dv=1,
            keyable=True
        )

        # Create plug to hide feather tweak controls
        feather_tweak_plug = settings_handle.create_plug(
            'featherTweakCtrlVis',
            at='long',
            min=0,
            max=1,
            dv=1,
            keyable=True
        )

        self.controller.root.add_plugs(
            feather_plug,
            feather_tweak_plug,
            keyable=False
        )
        for part in primary_digits + secondary_digits + tertiary_digits:
            feather_plug.connect_to(part.plugs['visibility'])

            for tweak_handle in [x for x in part.get_handles() if 'Tweak' in x.name]:
                feather_tweak_plug.connect_to(tweak_handle.plugs['visibility'])

        # create offset bend and twist nodes so we can control feather deformation using wing controls too
        bend_x_remap = self.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='BendX',
        )

        bend_z_remap = self.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='BendZ',
        )

        twist_remap = self.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='Twist',
        )

        base_twist_remap = self.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='BaseTwist',
        )

        bend_x_remap_nodes = []
        bend_z_remap_nodes = []
        twist_remap_nodes = []
        base_twist_remap_nodes = []
        up_transforms = []

        # go through wing joints (shoulder, elbow, hand)
        for i in range(len(arm_joints) - 1):
            digits = digit_groups[i]
            joint = arm_joints[i]
            next_joint = arm_joints[i + 1]
            next_joint_position = next_joint.get_translation()
            aim_transform = self.create_child(
                Transform,
                segment_name='%sAim' % next_joint.segment_name,
                matrix=Matrix(next_joint_position + (digit_vectors[i] * 2.0))
            )
            joint_constraint = self.controller.create_parent_constraint(
                joint, next_joint,
                aim_transform,
                mo=True
            )
            angle_transform = self.create_child(
                Transform,
                segment_name='%sAngle' % joint.segment_name,
                matrix=Matrix(next_joint_position),
                parent=next_joint
            )

            up_transform = joint.create_child(
                Transform,
                segment_name='%sUpGetter' % joint.segment_name,
                matrix=joint.get_matrix()
            )
            up_transforms.append(up_transform)
            orient_constraint = self.controller.create_orient_constraint(
                joint,
                next_joint,
                up_transform,
                mo=False
            )
            orient_constraint.plugs['interpType'].set_value(2)
            self.controller.create_aim_constraint(
                aim_transform,
                angle_transform,
                aimVector=env.side_aim_vectors[self.side],
                upVector=env.side_up_vectors[self.side],
                worldUpObject=up_transform,
                worldUpType='objectrotation',
                worldUpVector=[1.0, 0.0, 0.0] if self.side == 'right' else [-1.0, 0.0, 0.0],
                mo=False
            )
            handle_positon = angle_transform.get_matrix()
            if self.side == 'right':
                handle_positon.flip_y()
            handle_positon.set_translation(next_joint_position + (digit_vectors[i] * 1.1))
            aim_handle = self.create_handle(
                shape='marker',
                axis='z',
                segment_name='%sAim' % joint.segment_name,
                matrix=handle_positon,
                parent=angle_transform,
                size=self.size * 2.5
            )
            aim_handle.plugs['rotateOrder'].set_value(1)
            if self.side not in 'right':
                aim_handle.multiply_shape_matrix(Matrix(scale=[1.0, 1.0, -1.0]))
            rotation_blending_plug = aim_handle.create_plug(
                'RotationBlending',
                at='double',
                dv=0.5,
                min=0.0,
                max=1.0,
                k=True
            )
            blending_reverse = joint.create_child(
                DependNode,
                node_type='reverse'
            )
            rotation_blending_plug.connect_to(blending_reverse.plugs['inputX'])
            blending_reverse.plugs['outputX'].connect_to(joint_constraint.get_weight_plug(joint))
            rotation_blending_plug.connect_to(joint_constraint.get_weight_plug(next_joint))
            root.add_plugs(
                aim_handle.plugs['tx'],
                aim_handle.plugs['ty'],
                aim_handle.plugs['tz'],
                aim_handle.plugs['rx'],
                aim_handle.plugs['ry'],
                aim_handle.plugs['rz']
            )
            bend_x_plug = aim_handle.create_plug(
                'BendX',
                at='double',
                keyable=True
            )
            bend_z_plug = aim_handle.create_plug(
                'BendZ',
                at='double',
                keyable=True
            )
            twist_plug = aim_handle.create_plug(
                'Twist',
                at='double',
                keyable=True
            )
            base_twist_plug = aim_handle.create_plug(
                'BaseTwist',
                at='double',
                keyable=True
            )
            root.add_plugs(
                rotation_blending_plug,
                bend_x_plug,
                bend_z_plug,
                twist_plug,
                base_twist_plug,
            )

            # Adding 3 extra attributes to the driver null: twist, bend x , bend z:
            aim_drv_null = aim_handle.drv
            aim_drv_bendx_plug = aim_drv_null.create_plug(
                'BendX',
                at='double',
                keyable=True,
                dv=0
            )
            aim_drv_bendz_plug = aim_drv_null.create_plug(
                'BendZ',
                at='double',
                keyable=True,
                dv=0
            )
            aim_drv_twist_plug = aim_drv_null.create_plug(
                'Twist',
                at='double',
                keyable=True,
                dv=0
            )
            aim_drv_base_twist_plug = aim_drv_null.create_plug(
                'BaseTwist',
                at='double',
                keyable=True,
                dv=0
            )
            root.add_plugs(
                aim_drv_bendx_plug,
                aim_drv_bendz_plug,
                aim_drv_twist_plug,
                aim_drv_base_twist_plug,
            )
            aim_handles.append(aim_handle)
            if digits is None or len(digits) < 2:
                getter = aim_handle.create_child(
                    Transform,
                    segment_name='%sGetter' % aim_handle.segment_name,
                    parent=self
                )
                self.controller.create_point_constraint(
                    aim_handle,
                    getter,
                    mo=False
                )
                position_getters.append((getter, getter))
            else:
                start_handle = self.create_handle(
                    shape='circle',
                    axis='z',
                    segment_name='%sStartAim' % joint.segment_name,
                    matrix=handle_positon,
                    parent=aim_handle,
                    size=self.size,
                    create_gimbal=False
                )
                start_handle.multiply_shape_matrix(Matrix([self.size * -1.0 if self.side == 'right' else self.size, self.size, 0.0]))
                end_handle = self.create_handle(
                    shape='circle',
                    axis='z',
                    segment_name='%sEndAim' % joint.segment_name,
                    matrix=handle_positon,
                    parent=aim_handle,
                    size=self.size,
                    create_gimbal=False
                )
                root.add_plugs(
                    start_handle.plugs['tx'],
                    start_handle.plugs['ty'],
                    start_handle.plugs['tz'],
                    end_handle.plugs['tx'],
                    end_handle.plugs['ty'],
                    end_handle.plugs['tz'],
                )
                end_handle.multiply_shape_matrix(Matrix([self.size if self.side == 'right' else self.size * -1.0, self.size, 0.0]))
                start_getter = start_handle.create_child(
                    Transform,
                    segment_name='%sGetter' % start_handle.segment_name,
                    parent=self
                )
                end_getter = end_handle.create_child(
                    Transform,
                    segment_name='%sGetter' % end_handle.segment_name,
                    parent=self
                )
                self.controller.create_point_constraint(
                    start_handle,
                    start_getter,
                    mo=False
                )
                self.controller.create_point_constraint(
                    end_handle,
                    end_getter,
                    mo=False
                )
                position_getters.append((start_getter, end_getter))

            # Adding an blendWeighted in between the control+drv and the remap node to add offset nulls
            aim_drv_null = aim_handle.drv
            aim_bend_x_drv_plug = aim_drv_null.plugs['BendX']
            aim_bend_z_drv_plug = aim_drv_null.plugs['BendZ']
            aim_twist_drv_plug = aim_drv_null.plugs['Twist']
            aim_base_twist_drv_plug = aim_drv_null.plugs['BaseTwist']
            aim_base_twist_add = aim_base_twist_drv_plug.add(base_twist_plug)
            if self.side == 'left':
                aim_rx_negative = aim_handle.plugs['rx'].multiply(-1.0)
                aim_rz_negative = aim_handle.plugs['rz'].multiply(-1.0)
                aim_bendx_add = aim_bend_x_drv_plug.blend_weighted(bend_x_plug, aim_rz_negative)
                aim_bendz_add = aim_bend_z_drv_plug.blend_weighted(bend_z_plug, aim_rx_negative)
            else:
                aim_bendx_add = aim_bend_x_drv_plug.blend_weighted(bend_x_plug, aim_handle.plugs['rz'])
                aim_bendz_add = aim_bend_z_drv_plug.blend_weighted(bend_z_plug, aim_handle.plugs['rx'])
            aim_ry_negative = aim_handle.plugs['ry'].multiply(-1.0)
            aim_twist_add = aim_twist_drv_plug.blend_weighted(twist_plug, aim_ry_negative)

            # Connecting remap nodes to out addDoubleLinear instead
            in_value = 1.0 / (len(arm_joints) - 2) * i

            bend_x_remap.plugs['value'].element(i).child(0).set_value(in_value)
            aim_bendx_add.connect_to(bend_x_remap.plugs['value'].element(i).child(1))
            bend_x_remap.plugs['value'].element(i).child(2).set_value(2)
            bend_x_remap_nodes.append(bend_x_remap)

            bend_z_remap.plugs['value'].element(i).child(0).set_value(in_value)
            aim_bendz_add.connect_to(bend_z_remap.plugs['value'].element(i).child(1))
            bend_z_remap.plugs['value'].element(i).child(2).set_value(2)
            bend_z_remap_nodes.append(bend_z_remap)

            twist_remap.plugs['value'].element(i).child(0).set_value(in_value)
            aim_twist_add.connect_to(twist_remap.plugs['value'].element(i).child(1))
            twist_remap.plugs['value'].element(i).child(2).set_value(2)
            twist_remap_nodes.append(twist_remap)

            base_twist_remap.plugs['value'].element(i).child(0).set_value(in_value)
            aim_base_twist_add.connect_to(base_twist_remap.plugs['value'].element(i).child(1))
            base_twist_remap.plugs['value'].element(i).child(2).set_value(2)
            base_twist_remap_nodes.append(base_twist_remap)

        overall_maintain_offset_plug = None
        if not self.use_legacy_digit_aim:
            overall_maintain_offset_plug = self.create_plug(
                'MaintainAimOffsets',
                attributeType='double',
                min=0.0,
                max=1.0,
                dv=1.0,
                keyable=True
            )

        limb_locators = []
        limb_joints = limb_part.base_joints
        for limb_joint in limb_joints:
            locator = limb_joint.create_child(
                Locator,
                segment_name='%sBendyGetter' % limb_joint.segment_name
            )
            locator.plugs['visibility'].set_value(False)
            limb_locators.append(locator)
        all_digits = digit_groups[0] + digit_groups[1] + digit_groups[2]
        ad = 0
        for d in range(3):
            start_getter = position_getters[d][1]  # 'end getter' of current joint
            end_getter = position_getters[d + 1][0]  # 'start getter' of next joint
            start_getter_position = start_getter.get_translation()
            end_getter_position = end_getter.get_translation()
            fist_tip_position = digit_groups[d][0].joints[-1].get_translation()
            last_tip_position = digit_groups[d][-1].joints[-1].get_translation()
            tip_span_vector = (last_tip_position - fist_tip_position)
            tip_span_length = tip_span_vector.mag()

            limb_joint_1 = limb_part.base_joints[d + 1]
            limb_joint_2 = limb_part.base_joints[d + 2]
            joint_position_1 = limb_joint_1.get_translation()
            joint_position_2 = limb_joint_2.get_translation()
            getter_vec_1 = (start_getter_position - joint_position_1)
            getter_vec_2 = (end_getter_position - joint_position_2)
            start_len = getter_vec_1.mag()
            end_len = getter_vec_2.mag()

            # Extrapolate feather vector to meet line if not legacy settings (assume a None means legacy ie. True)
            extend_aim_to_line = bool(self.use_virtual_digit_length or (self.use_legacy_digit_aim is False))
            if extend_aim_to_line:
                # Needs to have a line to place the aim objects on, seeing as they won't be auto-placed by the blend;
                # Use line between main handles. (Default would place aim objects at feather ends instead)
                fist_tip_position = start_getter_position
                last_tip_position = end_getter_position
                tip_span_vector = (last_tip_position - fist_tip_position)
                tip_span_length = tip_span_vector.mag()

            if isinstance(limb_part, BipedArmBendy) and len(limb_part.limb_segments) > d:
                segment_curve = limb_part.limb_segments[d].nurbs_curve
            else:
                limb_locator_1 = limb_locators[d + 1]
                limb_locator_2 = limb_locators[d + 2]
                segment_curve_transform = self.create_child(
                    Transform,
                    segment_name='BendyCurve%s' % rig_factory.index_dictionary[d]
                )
                segment_curve = segment_curve_transform.create_child(
                    NurbsCurve,
                    degree=1,
                    positions=[
                        joint_position_1,
                        joint_position_2
                    ]
                )
                segment_curve_transform.plugs['inheritsTransform'].set_value(False)
                segment_curve_transform.plugs['visibility'].set_value(False)
                limb_locator_1.plugs['worldPosition'].element(0).connect_to(
                    segment_curve.plugs['controlPoints'].element(0))
                limb_locator_2.plugs['worldPosition'].element(0).connect_to(
                    segment_curve.plugs['controlPoints'].element(1))

            for i, digit in enumerate(digit_groups[d]):
                start_position = digit.joints[0].get_translation()
                end_position = digit.joints[-1].get_translation()
                sec_last_position = digit.joints[-2].get_translation()

                bone_vector = joint_position_2 - joint_position_1
                if bone_vector.mag() == 0.0:
                    raise Exception('Bone has zero length.')

                closest_point_on_digit = end_position
                last_iter_result = closest_point_on_digit
                # Iterate back and forth more times for non-legacy, for increased precision of line intersection;
                for j in range(12 if extend_aim_to_line else 2):
                    edge_point = vec.find_closest_point_on_line(
                        closest_point_on_digit,
                        fist_tip_position,
                        last_tip_position
                    )
                    closest_point_on_digit = vec.find_closest_point_on_line(
                        edge_point,
                        start_position,
                        end_position,
                        extrapolate_line=extend_aim_to_line
                    )
                    # Check whether the result is within 0.5% wing section length of last iteration, as accuracy measure
                    # On test asset, this was reached within max 11 iterations
                    if (closest_point_on_digit - last_iter_result).mag() / tip_span_length < 0.005:
                        break

                    last_iter_result = closest_point_on_digit

                segment_span_length = (closest_point_on_digit - fist_tip_position).mag()
                if segment_span_length == 0.0 or tip_span_length == 0.0:
                    percentage_down_edge = 0.0
                else:
                    percentage_down_edge = segment_span_length / tip_span_length

                if self.use_virtual_digit_length and isinstance(digit, (FeatherPart, FeatherRibbonPart)):
                    # Set the length of the bend and twist deformers to closer to the longer joint length
                    # to ensure that bending all feathers together gives a reasonable result
                    # if there are both short and long ones, (as opposed to just using the feather length)
                    actual_length = (end_position - start_position).mag()
                    getter_gradient_length = start_len*(1.0-percentage_down_edge) + end_len*percentage_down_edge
                    virtual_length = 0.23*actual_length + 0.77*getter_gradient_length  # Weighted average to account for mesh spans being closer on shorter feathers
                    for nonlinear_def in digit.deformers:
                        nonlinear_def.plugs['ty'].set_value(
                            virtual_length * (-0.25 if digit.side == 'right' else 0.25))  # from ribbon part
                        nonlinear_def.plugs['sx'].set_value(virtual_length * 0.75)  # part uses length*0.75
                        nonlinear_def.plugs['sy'].set_value(virtual_length * 0.75)
                        nonlinear_def.plugs['sz'].set_value(virtual_length * 0.75)

                handle_position = digit.joints[0].get_matrix()
                handle_position.set_translation(
                    end_position + ((end_position - sec_last_position).normalize() * self.size))
                rotation_blending_plug = digit.create_plug(
                    'RotationBlending',
                    attributeType='double',
                    min=0.0,
                    max=1.0,
                    dv=0.0,
                    keyable=True
                )
                maintain_offset_plug = digit.create_plug(
                    'MaintainOffset',
                    attributeType='double',
                    min=0.0,
                    max=1.0,
                    dv=1.0,
                    keyable=True
                )
                rotation_blending_plug.set_value(percentage_down_edge)

                aim_object = digit.create_child(
                    Transform,
                    segment_name='AimObject',
                    parent=self
                )
                aim_pt_con = None
                if self.use_legacy_digit_aim:
                    # Linear blend of translate between start and end controls
                    blend_colors = aim_object.create_child(
                        DependNode,
                        node_type='blendColors',
                    )
                    end_getter.plugs['translate'].connect_to(blend_colors.plugs['color1'])
                    start_getter.plugs['translate'].connect_to(blend_colors.plugs['color2'])
                    blend_colors.plugs['output'].connect_to(aim_object.plugs['translate'])
                    rotation_blending_plug.connect_to(blend_colors.plugs['blender'])
                else:
                    # Constrain aim target with an offset per driver, so that the target doesn't move when blended
                    aim_object.set_matrix(Matrix(closest_point_on_digit))  # A point near the line between the first and last feather tips, on the feather vector
                    aim_pt_con = self.controller.create_parent_constraint(
                        start_getter,
                        end_getter,
                        aim_object,
                        skipRotate=['x', 'y', 'z'],
                        mo=True
                    )
                    aim_pt_con.plugs['interpType'].set_value(2)

                    rotation_blending_plug.reverse().connect_to(aim_pt_con.plugs['w0'])
                    rotation_blending_plug.connect_to(aim_pt_con.plugs['w1'])

                # Aim the feather at the aim object
                aim_constraint = self.controller.create_aim_constraint(
                    aim_object,
                    digit.handles[0].groups[0],
                    aimVector=env.side_aim_vectors[self.side],
                    upVector=env.side_up_vectors[self.side],
                    worldUpObject=up_transforms[d],
                    worldUpType='objectrotation',
                    worldUpVector=[1.0, 0.0, 0.0] if self.side == 'right' else [-1.0, 0.0, 0.0],
                    mo=True
                )
                if self.use_legacy_digit_aim:
                    pair_blend = digit.create_child(
                        DependNode,
                        node_type='pairBlend',
                        segment_name='OrientBlend%s' % digit.segment_name
                    )
                    pair_blend.plugs['rotInterpolation'].set_value(1)
                    pair_blend.plugs['inRotate1'].set_value([0.0, 0.0, 0.0])
                    pair_blend.plugs['inRotate2'].set_value(aim_constraint.plugs['offset'].get_value())
                    pair_blend.plugs['outRotate'].connect_to(aim_constraint.plugs['offset'])
                    maintain_offset_plug.connect_to(pair_blend.plugs['weight'])
                else:
                    for con_i in range(2):
                        # offset_t_plug = aim_pt_con.plugs['target'][con_i]['targetOffsetTranslate']  # Fails for unknown reason (RIG-2495)
                        offset_t_plug = aim_pt_con.plugs['target'][con_i].element(6)

                        mult_blend = digit.create_child(
                            DependNode,
                            node_type='multiplyDivide',
                            segment_name='OffsetBlend%s%s' % (digit.segment_name, 'AB'[con_i])
                        )
                        mult_blend.plugs['input1'].set_value(offset_t_plug.get_value())
                        maintain_offset_plug.connect_to(mult_blend.plugs['input2X'])
                        maintain_offset_plug.connect_to(mult_blend.plugs['input2Y'])
                        maintain_offset_plug.connect_to(mult_blend.plugs['input2Z'])
                        mult_blend.plugs['output'].connect_to(offset_t_plug)

                        overall_maintain_offset_plug.connect_to(maintain_offset_plug)

                point_on_curve_info = digit.create_child(
                    DependNode,
                    node_type='pointOnCurveInfo',
                    segment_name='%sBendy' % digit.segment_name
                )
                translate_getter_transform = digit.create_child(
                    Transform,
                    segment_name='%sBendyGetter' % digit.segment_name
                )
                translate_getter_transform.plugs['inheritsTransform'].set_value(False)
                segment_curve.plugs['worldSpace'].element(0).connect_to(point_on_curve_info.plugs['inputCurve'])
                point_on_curve_info.plugs['turnOnPercentage'].set_value(True)
                point_on_curve_info.plugs['parameter'].set_value(percentage_down_edge)
                point_on_curve_info.plugs['result'].child(0).connect_to(translate_getter_transform.plugs['translate'])
                self.controller.create_point_constraint(
                    translate_getter_transform,
                    digit.handles[0].groups[0],
                    mo=True
                )

                if isinstance(digit, (FeatherPart, FeatherRibbonPart)):
                    feather_bend_x_remap = self.create_child(
                        DependNode,
                        node_type='remapValue',
                        segment_name='FeatherBendX%s' % rig_factory.index_dictionary[ad],
                    )
                    feather_bend_z_remap = self.create_child(
                        DependNode,
                        node_type='remapValue',
                        segment_name='FeatherBendZ%s' % rig_factory.index_dictionary[ad],
                    )
                    feather_twist_remap = self.create_child(
                        DependNode,
                        node_type='remapValue',
                        segment_name='FeatherTwist%s' % rig_factory.index_dictionary[ad],
                    )
                    feather_base_twist_remap = self.create_child(
                        DependNode,
                        node_type='remapValue',
                        segment_name='FeatherBaseTwist%s' % rig_factory.index_dictionary[ad],
                    )

                    fraction = 1.0 / (len(all_digits) - 1) * ad
                    feather_bend_x_remap.plugs['inputValue'].set_value(fraction)
                    feather_bend_z_remap.plugs['inputValue'].set_value(fraction)
                    feather_twist_remap.plugs['inputValue'].set_value(fraction)
                    feather_base_twist_remap.plugs['inputValue'].set_value(fraction)

                    feather_bend_x_remap.plugs['outValue'].connect_to(digit.handles[0].plugs['BendXInput'])
                    feather_bend_z_remap.plugs['outValue'].connect_to(digit.handles[0].plugs['BendZInput'])
                    feather_twist_remap.plugs['outValue'].connect_to(digit.handles[0].plugs['TwistInput'])
                    feather_base_twist_remap.plugs['outValue'].connect_to(digit.handles[0].plugs['BaseTwistInput'])

                    for e in range(4):
                        for c in range(3):
                            bx = feather_bend_x_remap.plugs['value'].element(e).child(c)
                            bend_x_remap_nodes[d].plugs['value'].element(e).child(c).connect_to(bx)

                            bz = feather_bend_z_remap.plugs['value'].element(e).child(c)
                            bend_z_remap_nodes[d].plugs['value'].element(e).child(c).connect_to(bz)

                            tz = feather_twist_remap.plugs['value'].element(e).child(c)
                            twist_remap_nodes[d].plugs['value'].element(e).child(c).connect_to(tz)

                            tz = feather_base_twist_remap.plugs['value'].element(e).child(c)
                            base_twist_remap_nodes[d].plugs['value'].element(e).child(c).connect_to(tz)
                ad += 1

        # Check if using FkChain
        digit_part = self.find_first_part(
            root_name='{}DigitA'.format(
                self.root_name
            ),
            differentiation_name='Primary'
        )
        if isinstance(digit_part, (FkChain, FeatherSimplePart)):
            fk_feather_rotations(
                self.controller,
                aim_handles,
                tertiary_digits,
                secondary_digits,
                primary_digits
            )

        self.aim_handles = aim_handles
        limb_part.fk_handles[-1].plugs['rotateOrder'].set_value(5)

    def get_toggle_blueprint(self):
        blueprint = super(BaseWing, self).get_toggle_blueprint()
        # Store rig state values to maintain backwards compatibility for old blueprints
        blueprint['use_legacy_digit_aim'] = self.use_legacy_digit_aim
        blueprint['use_virtual_digit_length'] = self.use_virtual_digit_length
        return blueprint


def set_even_spacing(transforms):
    if len(transforms) < 2:
        raise Exception('Not enough handles to space evenly')
    position_1 = transforms[0].get_translation()
    position_2 = transforms[-1].get_translation()
    center_handles = transforms[1:-1]
    for i in range(len(center_handles)):
        fraction = 1.0 / (len(center_handles) + 1) * (i + 1)
        center_handles[i].set_matrix(Matrix((position_1 * (1.0 - fraction)) + (position_2 * fraction)))


def find_digit_parts(part, differentiation_name):
    digits = []
    for i in range(100):
        digit = part.find_first_part(
            root_name='{}Digit{}'.format(
                part.root_name,
                rig_factory.index_dictionary[i].capitalize()
            ),
            differentiation_name=differentiation_name
        )
        if digit:
            digits.append(digit)
        else:
            break
    return digits


def fk_feather_rotations(controller, aim_handles, tertiary_digits, secondary_digits, primary_digits):
    """
    :param controller: rig controller
    :type controller: rig controller

    :param aim_handles: list of aim controls in order, from clavicle down to hand
    :type aim_handles: list

    :param tertiary_digits: list of digit parts in order, from A -> Z
    :type tertiary_digits: list

    :param secondary_digits: list of digit parts in order, from A -> Z
    :type secondary_digits: list

    :param primary_digits: list of digit parts in order, from A -> Z
    :type primary_digits: list
    """

    chain_rotation_values = []  # For the difference in rotation down the fk chain
    base_twist_values = []  # For the difference in BaseTwist down the fk chain
    chain_translation_values = []  # For the difference in tranlation XYZ down the fk chain
    chain_increment = 0
    fk_handles = [x for x in tertiary_digits[0].get_handles() if 'Gimbal' not in x.name
                  and 'Tweak' not in x.name]
    ribbon_joint_count = len(fk_handles)

    for i in range(1, ribbon_joint_count + 1):
        cos_value = (-0.5 * cos(chain_increment) + 0.5) * 0.25  # x0.25 because rotating too much
        base_twist_value = (-0.5 * cos(chain_increment + pi) + 0.5) * 0.25  # x0.25 because rotating too much
        chain_rotation_values.append(cos_value)
        base_twist_values.append(base_twist_value)
        chain_translation_values.append([
            cos_value * (tertiary_digits[0].size * 0.0015) * (float(i) / ribbon_joint_count),
            cos_value * (tertiary_digits[0].size * 0.006) * (float(i) / ribbon_joint_count),
            cos_value * (tertiary_digits[0].size * 0.0015) * (float(i) / ribbon_joint_count)
        ])

        chain_increment += pi / (ribbon_joint_count - 1)

    clav_aim_handle = aim_handles[0]
    shoulder_aim_handle = aim_handles[1]
    elbow_aim_handle = aim_handles[2]
    hand_aim_handle = aim_handles[3]
    all_pmas_dict = dict()
    aim_handle_outputs = dict()

    # Create multiplier plug to adjust rotational values during anim
    for aim_handle in [clav_aim_handle, shoulder_aim_handle, elbow_aim_handle, hand_aim_handle]:
        multipler_plug = aim_handle.create_plug(
            'Multiplier',
            at='float',
            dv=1.0,
            min=0.0,
            keyable=True
        )
        controller.root.add_plugs(multipler_plug)

        # Combine the plugs/channels that do the same thing and store in aim_handle_outputs
        for plug_name, target_plug in {
            'BendX': 'rotateZ',
            'Twist': 'rotateY',
            'BaseTwist': None,
            'BendZ': 'rotateX'
        }.items():
            # plug_name value needs to be reversed(negative) to match behaviour of target_plug
            negative_plug_value_mdl = aim_handle.create_child(
                DependNode,
                node_type='multDoubleLinear',
                segment_name='{0}Negative{1}'.format(aim_handle.name, plug_name)
            )
            aim_handle.plugs[plug_name].connect_to(negative_plug_value_mdl.plugs['input1'])
            negative_plug_value_mdl.plugs['input2'].set_value(-1.0)

            # Skip combining BaseTwist and rotateY are will get double transforms from Twist+rotateY
            if plug_name == 'BaseTwist':
                aim_handle_outputs[aim_handle.plugs[plug_name]] = negative_plug_value_mdl.plugs['output']

            else:
                # Combine the two values
                aim_handle_combined_values = aim_handle.create_child(
                    DependNode,
                    node_type='addDoubleLinear',
                    segment_name='{0}{1}{2}Combined'.format(aim_handle.name, plug_name, target_plug)
                )
                aim_handle.plugs[target_plug].connect_to(aim_handle_combined_values.plugs['input1'])
                negative_plug_value_mdl.plugs['output'].connect_to(aim_handle_combined_values.plugs['input2'])

                # Save into dictionary for later use
                aim_handle_outputs[aim_handle.plugs[plug_name]] = aim_handle_combined_values.plugs['output']

    # Create dictionary to store all plusMinusAverage nodes for Fk chains
    for digit in tertiary_digits + secondary_digits + primary_digits:
        fk_handles = [x for x in digit.get_handles() if 'Gimbal' not in x.name
                      and 'Tweak' not in x.name]
        tweak_handles = [x for x in digit.get_handles() if 'Tweak' in x.name]

        for i, fk_handle in enumerate(fk_handles):
            total_translation_pma = digit.create_child(
                DependNode,
                node_type='plusMinusAverage',
                segment_name='{0}TranslateTotal'.format(fk_handle.segment_name)
            )
            total_rotation_pma = digit.create_child(
                DependNode,
                node_type='plusMinusAverage',
                segment_name='{0}RotateTotal'.format(fk_handle.segment_name)
            )

            total_translation_pma.plugs['output3D'].connect_to(fk_handle.ofs.plugs['translate'])

            # Connect rotateY separately due to it having to be on tweak controls
            for axis in ['X', 'Y', 'Z']:
                if axis == 'Y':
                    total_rotation_pma.plugs['output3D{0}'.format(axis.lower())].connect_to(
                        tweak_handles[i].ofs.plugs['rotate{0}'.format(axis)]
                    )
                else:
                    total_rotation_pma.plugs['output3D{0}'.format(axis.lower())].connect_to(
                        fk_handle.ofs.plugs['rotate{0}'.format(axis)]
                    )

            all_pmas_dict[fk_handle] = [total_translation_pma, total_rotation_pma]

    # Define data needed for each segment
    digit_dict = {
        clav_aim_handle: {
            'remap_values': [
                {0.0: 1.0},
                {1.0: 0.0}
            ],
            'digits': tertiary_digits
        },
        shoulder_aim_handle: {
            'remap_values': [
                {0.0: 0.0},
                {0.5: 1.0},
                {1.0: 0.0}
            ],
            'digits': tertiary_digits + secondary_digits
        },
        elbow_aim_handle: {
            'remap_values': [
                {0.0: 0.0},
                {0.5: 1.0},
                {1.0: 0.0}
            ],
            'digits': secondary_digits + primary_digits
        },
        hand_aim_handle: {
            'remap_values': [
                {0.0: 0.0},
                {1.0: 1.0}
            ],
            'digits': primary_digits
        }
    }

    # Create nodes for calculation
    for aim_handle, data in digit_dict.items():
        segment_value = 0.0
        remap_values = data['remap_values']
        digits = data['digits']

        # Create remap node to differentiate movement between digits down the arm
        for digit in digits:
            fk_handles = [x for x in digit.get_handles() if 'Gimbal' not in x.name
                          and 'Tweak' not in x.name]

            rotate_remap = digit.create_child(
                DependNode,
                node_type='remapValue',
                segment_name='{0}Rotation'.format(aim_handle.segment_name)
            )
            for i, remap_data in enumerate(remap_values):
                position = remap_data.keys()[0]
                value = remap_data[position]
                rotate_remap.plugs['value'].child(i).element(0).set_value(position)
                rotate_remap.plugs['value'].child(i).element(1).set_value(value)
                rotate_remap.plugs['value'].child(i).element(2).set_value(2)

            rotate_remap.plugs['inputValue'].set_value(segment_value)

            # Create nodes for each fk chain control
            for i, fk_handle in enumerate(fk_handles):
                total_translation_pma, total_rotation_pma = all_pmas_dict[fk_handle]

                # Value to multiply values depending on index of fk chain
                chain_rotate_value = chain_rotation_values[i]
                base_twist_value = base_twist_values[i]
                chain_translate_value = chain_translation_values[i]
                fk_rotate_z_value = aim_handle_outputs[aim_handle.plugs['BendX']]
                fk_rotate_x_value = aim_handle_outputs[aim_handle.plugs['BendZ']]
                fk_twist_value = aim_handle_outputs[aim_handle.plugs['Twist']]

                for rotate_value in [fk_rotate_x_value, fk_twist_value, fk_rotate_z_value]:
                    # Define variables needed depending on value being passed in
                    if rotate_value == fk_rotate_x_value:
                        rotate_segment = 'RotateX'
                        translate_segment = 'TranslateYZ'
                        rotate_plug_index = 0
                        translate_plug_index = [1, 2]
                    elif rotate_value == fk_twist_value:
                        rotate_segment = 'Twist'
                        translate_segment = ''
                        rotate_plug_index = 1
                        translate_plug_index = []
                    else:
                        rotate_segment = 'RotateZ'
                        translate_segment = 'TranslateXY'
                        rotate_plug_index = 2
                        translate_plug_index = [0, 1]

                    # ROTATION
                    # Multiply the value from the aim handle rotation/plugs with the chain rotate value
                    rotated_mdl = fk_handle.create_child(
                        DependNode,
                        node_type='multDoubleLinear',
                        segment_name='{0}{1}{2}'.format(aim_handle.name, fk_handle.segment_name, rotate_segment)
                    )
                    rotate_value.connect_to(rotated_mdl.plugs['input1'])
                    rotated_mdl.plugs['input2'].set_value(chain_rotate_value)

                    # Now multiply that value with the remap value
                    digit_rotated_mdl = fk_handle.create_child(
                        DependNode,
                        node_type='multDoubleLinear',
                        segment_name='{0}{1}{2}DigitRemap'.format(aim_handle.name, fk_handle.segment_name,
                                                                  rotate_segment)
                    )
                    rotated_mdl.plugs['output'].connect_to(digit_rotated_mdl.plugs['input1'])
                    rotate_remap.plugs['outValue'].connect_to(digit_rotated_mdl.plugs['input2'])

                    # Now multiply that value again with the multiplier
                    multiplied_rotated_mdl = fk_handle.create_child(
                        DependNode,
                        node_type='multDoubleLinear',
                        segment_name='{0}{1}{2}Multiplied'.format(aim_handle.name, fk_handle.segment_name,
                                                                  rotate_segment)
                    )
                    digit_rotated_mdl.plugs['output'].connect_to(multiplied_rotated_mdl.plugs['input1'])
                    aim_handle.plugs['Multiplier'].connect_to(multiplied_rotated_mdl.plugs['input2'])

                    # Connect this final value into the pma that is already connected into ofs groups
                    for index in range(0, 999):  # Use to check if input already has connection
                        if not total_rotation_pma.plugs['input3D'].element(index).child(rotate_plug_index).is_connected():
                            multiplied_rotated_mdl.plugs['output'].connect_to(
                                total_rotation_pma.plugs['input3D'].element(index).child(rotate_plug_index)
                            )
                            break

                    # TRANSLATION
                    # Create similar nodes as rotation for translation, but using multiplyDivide instead due to more
                    # than one axis to affect
                    translated_md = fk_handle.create_child(
                        DependNode,
                        node_type='multiplyDivide',
                        segment_name='{0}{1}{2}'.format(aim_handle.name, fk_handle.segment_name, rotate_segment,
                                                        translate_segment)
                    )
                    for axis in translate_segment[-2:]:
                        rotate_value.connect_to(translated_md.plugs['input1{0}'.format(axis)])
                        translated_md.plugs['input2'].set_value(chain_translate_value)

                    digit_translated_md = fk_handle.create_child(
                        DependNode,
                        node_type='multiplyDivide',
                        segment_name='{0}{1}{2}{3}DigitRemap'.format(aim_handle.name, fk_handle.segment_name,
                                                                     rotate_segment, translate_segment)
                    )
                    translated_md.plugs['output'].connect_to(digit_translated_md.plugs['input1'])
                    for axis in translate_segment[-2:]:
                        rotate_remap.plugs['outValue'].connect_to(digit_translated_md.plugs['input2{0}'.format(axis)])

                    multiplied_translated_md = fk_handle.create_child(
                        DependNode,
                        node_type='multiplyDivide',
                        segment_name='{0}{1}{2}{3}Multiplied'.format(aim_handle.name, fk_handle.segment_name,
                                                                     rotate_segment, translate_segment)
                    )
                    digit_translated_md.plugs['output'].connect_to(multiplied_translated_md.plugs['input1'])
                    for axis in translate_segment[-2:]:
                        aim_handle.plugs['Multiplier'].connect_to(
                            multiplied_translated_md.plugs['input2{0}'.format(axis)])

                    # Create setup to make sure values are always positive during certain scenarios
                    translated_squared_md = fk_handle.create_child(
                        DependNode,
                        node_type='multiplyDivide',
                        segment_name='{0}{1}{2}{3}Squared'.format(aim_handle.name, fk_handle.segment_name,
                                                                  rotate_segment, translate_segment)
                    )
                    translated_squared_md.plugs['operation'].set_value(3)
                    for axis in translate_segment[-2:]:
                        multiplied_translated_md.plugs['output{0}'.format(axis)].connect_to(
                            translated_squared_md.plugs['input1{0}'.format(axis)]
                        )
                        if axis != 'Y':
                            translated_squared_md.plugs['input2{0}'.format(axis)].set_value(1.0)
                        else:
                            translated_squared_md.plugs['input2{0}'.format(axis)].set_value(2.0)

                    translated_square_rooted_md = fk_handle.create_child(
                        DependNode,
                        node_type='multiplyDivide',
                        segment_name='{0}{1}{2}{3}SquareRooted'.format(aim_handle.name, fk_handle.segment_name,
                                                                       rotate_segment, translate_segment)
                    )
                    translated_square_rooted_md.plugs['operation'].set_value(3)
                    for axis in translate_segment[-2:]:
                        translated_squared_md.plugs['output{0}'.format(axis)].connect_to(
                            translated_square_rooted_md.plugs['input1{0}'.format(axis)]
                        )
                        if axis != 'Y':
                            translated_square_rooted_md.plugs['input2{0}'.format(axis)].set_value(1.0)
                        else:
                            translated_square_rooted_md.plugs['input2{0}'.format(axis)].set_value(0.5)

                    # Connect this final value into the pma that is already connected into ofs groups
                    for target_plug in translate_plug_index:
                        for index in range(0, 999):  # Use to check if input already has connection
                            if not total_translation_pma.plugs['input3D'].element(index).child(
                                    target_plug
                            ).is_connected():
                                translated_square_rooted_md.plugs['output'].child(target_plug).connect_to(
                                    total_translation_pma.plugs['input3D'].element(index).child(target_plug)
                                )
                                break

                # Add BaseTwist into digits now
                base_twist_mdl = fk_handle.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}{1}BaseTwist'.format(aim_handle.name, fk_handle.segment_name)
                )
                aim_handle_outputs[aim_handle.plugs['BaseTwist']].connect_to(base_twist_mdl.plugs['input1'])
                base_twist_mdl.plugs['input2'].set_value(base_twist_value)

                # Now multiply that value with the remap value
                digit_base_twist_mdl = fk_handle.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}{1}BaseTwistDigitRemap'.format(aim_handle.name, fk_handle.segment_name)
                )
                base_twist_mdl.plugs['output'].connect_to(digit_base_twist_mdl.plugs['input1'])
                rotate_remap.plugs['outValue'].connect_to(digit_base_twist_mdl.plugs['input2'])

                # Now multiply that value again with the multiplier
                multiplied_base_twist_mdl = fk_handle.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}{1}BaseTwistMultiplied'.format(aim_handle.name, fk_handle.segment_name)
                )
                digit_base_twist_mdl.plugs['output'].connect_to(multiplied_base_twist_mdl.plugs['input1'])
                aim_handle.plugs['Multiplier'].connect_to(multiplied_base_twist_mdl.plugs['input2'])

                # Connect this final value into the pma that is already connected into ofs groups
                for index in range(0, 999):  # Use to check if input already has connection
                    if not total_rotation_pma.plugs['input3D'].element(index).child(1).is_connected():  # Plug into Y
                        multiplied_base_twist_mdl.plugs['output'].connect_to(
                            total_rotation_pma.plugs['input3D'].element(index).child(1)
                        )
                        break

            segment_value += 1.0 / len(digits)
