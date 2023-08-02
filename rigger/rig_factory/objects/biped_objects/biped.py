import copy
from Snowman3.rigger.rig_math.vector import Vector
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.positions as pos
from Snowman3.rigger.rig_factory.objects.base_objects.weak_list import WeakList
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm import BipedArm
from Snowman3.rigger.rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm_bendy import BipedArmBendy
from Snowman3.rigger.rig_factory.objects.part_objects.container_array import ContainerArray, ContainerArrayGuide


class BipedGuide(ContainerArrayGuide):

    use_t_pose = DataProperty( name='use_t_pose', default_value=True )

    def __init__(self, **kwargs):
        super(BipedGuide, self).__init__(**kwargs)
        self.toggle_class = Biped.__name__

    def create_members(self):
        super(BipedGuide, self).create_members()
        main = self.create_part(
            'BipedMainGuide',
            root_name='main',
            size=15.0
        )

        spine = self.create_part(
            'BipedSpineGuide',
            root_name='spine',
            size=15.0
        )
        neck = self.create_part(
            'BipedNeckFkSplineGuide',
            root_name='neck',
            size=5.0
        )
        left_arm = self.create_part(
            'BipedArmBendyGuide',
            root_name='arm',
            side='left',
            size=7.0
        )
        right_arm = self.create_part(
            'BipedArmBendyGuide',
            root_name='arm',
            side='right',
            size=7.0
        )
        left_leg = self.create_part(
            'BipedLegBendyGuide',
            root_name='leg',
            side='left',
            size=9.0
        )
        right_leg = self.create_part(
            'BipedLegBendyGuide',
            root_name='leg',
            side='right',
            size=9.0
        )
        left_hand = self.create_part(
            'BipedHandGuide',
            root_name='hand',
            side='left',
            size=2.5
        )

        left_hand.create_part(
            'BipedFingerGuide',
            side=left_hand.side,
            size=left_hand.size,
            root_name='thumb',
            count=4
        )

        for index_name in ['pointer', 'middle', 'ring', 'pinky']:
            left_hand.create_part(
                'BipedFingerGuide',
                side=left_hand.side,
                size=left_hand.size,
                root_name='finger_%s' % index_name
            )
        right_hand = self.create_part(
            'BipedHandGuide',
            root_name='hand',
            side='right',
            size=2.5
        )

        right_hand.create_part(
            'BipedFingerGuide',
            side=right_hand.side,
            size=right_hand.size,
            root_name='thumb',
            count=4
        )
        for index_name in ['pointer', 'middle', 'ring', 'pinky']:
            right_hand.create_part(
                'BipedFingerGuide',
                side=right_hand.side,
                size=right_hand.size,
                root_name='finger_%s' % index_name
            )

        spine.set_parent_joint(main.joints[-1])
        neck.set_parent_joint(spine.joints[-1])
        left_arm.set_parent_joint(spine.joints[-1])
        right_arm.set_parent_joint(spine.joints[-1])
        left_leg.set_parent_joint(spine.joints[0])
        right_leg.set_parent_joint(spine.joints[0])
        left_hand.set_parent_joint(left_arm.joints[-1])
        right_hand.set_parent_joint(right_arm.joints[-1])

        self.rig_data['space_switchers'] = copy.copy(pos.BIPED_HANDLE_SPACES)


class Biped(ContainerArray):

    mocap_joints = ObjectListProperty(
        name='mocap_joints'
    )
    character_node = ObjectProperty(
        name='character_node'
    )
    use_t_pose = DataProperty(
        name='use_t_pose',
        default_value=True
    )

    @classmethod
    def create(cls, **kwargs):
        kwargs['root_name'] = None
        return super(Biped, cls).create(**kwargs)

    def __init__(self, **kwargs):
        super(Biped, self).__init__(**kwargs)

    def finish_create(self, **kwargs):
        super(Biped, self).finish_create(**kwargs)
        if self.use_t_pose:
            self.setup_t_pose()

    def setup_t_pose(self):
        sdk_handles = WeakList()
        all_arms = self.find_parts(
                BipedArm,
                BipedArmBendy
        )
        if all_arms:
            for arm in all_arms:
                sdk_handles.extend(arm.fk_handles)
                sdk_handles.extend(
                    [
                        arm.wrist_handle,
                        arm.elbow_handle,
                        arm.clavicle_handle
                    ]
                )
                if arm.make_hand_roll:
                    sdk_handles.extend(
                        [
                            arm.finger_handle
                        ]
                    )

            sdk_handle_groups = [x.driven_group for x in sdk_handles if isinstance(x, GroupedHandle)]
            sdk_network = self.create_child(
                SDKNetwork,
                segment_name='TPose',
                lock_curves=False
            )
            sdk_network.initialize_driven_plugs(
                sdk_handle_groups,
                ['rx', 'ry', 'rz', 'tx', 'ty', 'tz']
            )
            t_pose_plug = self.settings_handle.create_plug(
                'TPose',
                at='double',
                dv=0.0,
                keyable=True,
                min=0.0,
                max=1.0
            )
            sdk_group = sdk_network.create_group(
                driver_plug=t_pose_plug,
            )
            sdk_group.create_keyframe_group(
                in_value=0.0
            )
            self.solve_t_pose()

            for x in sdk_handles:
                matrix = x.get_matrix()
                x.driven_group.set_matrix(matrix)
                x.set_matrix(matrix)
            sdk_group.create_keyframe_group(
                in_value=1.0
            )
            t_pose_plug.set_value(0.0)
            for arm in all_arms:
                arm.settings_handle.plugs['ikSwitch'].set_value(0.0)

    def finalize(self):
        super(Biped, self).finalize()
        if self.settings_handle.plugs.exists('TPose'):
            self.settings_handle.plugs['TPose'].set_locked(False)
            self.settings_handle.plugs['TPose'].set_value(1.0)

    def solve_t_pose(self):
        left_arms = self.find_parts(
                BipedArm,
                BipedArmBendy,
                side='left'
        )
        right_arms = self.find_parts(
                BipedArm,
                BipedArmBendy,
                side='right'
        )
        for left_arm in left_arms:
            for handle in left_arm.fk_handles:
                position = handle.get_translation()
                matrix = compose_matrix(
                    position,
                    position + Vector([20 * self.size, 0.0, 0.0]),
                    position + Vector([0.0, 0.0, -20 * self.size]),
                    rotation_order='xyz'
                )
                handle.set_matrix(matrix)
        for right_arm in right_arms:
            for handle in right_arm.fk_handles:
                position = handle.get_translation()
                matrix = compose_matrix(
                    position,
                    position + Vector([20 * self.size, 0.0, 0.0]),
                    position + Vector([0.0, 0.0, 20 * self.size]),
                    rotation_order='xyz'
                )
                handle.set_matrix(matrix)

        for arm in left_arms + right_arms:
            arm.match_to_ik()

    def get_toggle_blueprint(self):
        blueprint = super(Biped, self).get_toggle_blueprint()
        blueprint['use_t_pose'] = self.use_t_pose
        return blueprint


def compose_matrix(position, aim_position, up_position, rotation_order='xyz'):
    z_vector = up_position - position
    y_vector = aim_position - position
    x_vector = z_vector.cross_product(y_vector)
    z_vector = x_vector.cross_product(y_vector)
    matrix_list = []
    vector_dictionary = dict(
        x=x_vector,
        y=y_vector,
        z=z_vector
    )
    vector_list = [x for x in rotation_order]
    for i in range(3):
        matrix_list.extend(vector_dictionary[vector_list[i]].unit().data)
        matrix_list.append(0.0)
    matrix_list.extend(position.data)
    matrix_list.append(1.0)
    return Matrix(matrix_list)


