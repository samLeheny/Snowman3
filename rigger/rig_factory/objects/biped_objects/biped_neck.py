import math
import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.utilities.positions as pos
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty


class BipedNeckGuide(SplineChainGuide):

    default_head_scale = 4

    head_cube = ObjectProperty( name='ik_neck' )
    head_matrix = DataProperty( name='head_matrix', default_value=list(Matrix()) )
    base_joints = ObjectListProperty( name='base_joints' )
    world_space_head = DataProperty( name='world_space_head', default_value=True )
    default_settings = dict(
        root_name='Neck',
        size=4.0,
        side='center',
        joint_count=9,
        count=5,
        degree=None,
        legacy_joints=False
    )

    degree = DataProperty( name='degree' )
    legacy_joints = DataProperty( name='legacy_joints', default_value=False )

    def __init__(self, **kwargs):
        super(BipedNeckGuide, self).__init__(**kwargs)
        self.toggle_class = BipedNeck.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedNeckGuide, cls).create(**kwargs)
        root = this.get_root()
        side = this.side
        size = this.size

        if this.head_matrix is None:
            head_scale = size*cls.default_head_scale
            head_matrix = Matrix([0.0, head_scale*.5, 0.0])
            head_matrix.set_scale([head_scale] * 3)

        cube_group_transform = this.joints[-1].create_child( Transform, segment_name='HeadTop' )
        cube_transform = cube_group_transform.create_child( Transform, segment_name='Head' )
        cube_node = cube_transform.create_child( DependNode, node_type='polyCube' )
        cube_mesh = cube_transform.create_child( Mesh )

        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        cube_transform.set_matrix(
            this.head_matrix,
            world_space=False
        )
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        root.add_plugs([
            cube_transform.plugs['tx'],
            cube_transform.plugs['ty'],
            cube_transform.plugs['tz'],
            cube_transform.plugs['rx'],
            cube_transform.plugs['ry'],
            cube_transform.plugs['rz'],
            cube_transform.plugs['sx'],
            cube_transform.plugs['sy'],
            cube_transform.plugs['sz']
        ])

        head_joint = this.joints[-1].create_child( Joint, segment_name='Head' )
        this.head_cube = cube_transform
        this.base_joints = list(this.joints)
        if not this.legacy_joints:
            this.joints = []
        this.joints.extend(this.spline_joints)
        this.joints.append(head_joint)
        this.set_handle_positions(pos.BIPED_POSITIONS)
        return this

    def get_blueprint(self):
        blueprint = super(BipedNeckGuide, self).get_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        blueprint['legacy_joints'] = self.legacy_joints
        blueprint['world_space_head'] = self.world_space_head

        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        blueprint['matrices'] = [list(x.get_matrix()) for x in self.base_joints]
        blueprint['legacy_joints'] = self.legacy_joints
        blueprint['world_space_head'] = self.world_space_head
        return blueprint


class BipedNeck(Part):

    spline_joints = ObjectListProperty( name='spline_joints' )
    head_handle = ObjectProperty( name='head_handle' )
    head_matrix = DataProperty( name='head_matrix', default_value=list(Matrix()) )
    settings_handle = ObjectProperty( name='settings_handle' )
    move_neck_A_pivot = DataProperty( name='move_neck_A_pivot' )
    degree = DataProperty( name='degree' )
    legacy_joints = DataProperty( name='legacy_joints', default_value=False )
    world_space_head = DataProperty( name='world_space_head', default_value=True )
    joint_matrices = []

    def __init__(self, **kwargs):
        super(BipedNeck, self).__init__(**kwargs)
        self.data_getters['broken_tangents'] = self.get_broken_tangents
        self.data_setters['broken_tangents'] = self.set_broken_tangents

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedNeck, cls).create(**kwargs)
        nodes = cls.build_nodes(
            parent_group=this,
            joint_group=this.joint_group,
            matrices=this.matrices,
            spline_matrices=this.joint_matrices,
            head_matrix=this.head_matrix,
            degree=this.degree,
            legacy_joints=this.legacy_joints,
            world_space_head=this.world_space_head
        )
        settings_handle = nodes['settings_handle']
        spline_joints = nodes['spline_joints']
        joints = nodes['joints']
        handles = nodes['handles']
        root = this.get_root()
        for handle in handles:
            root.add_plugs(
                [
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz'],
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz']
                ]
            )
        root.add_plugs(
            settings_handle.plugs['BreakStartTangent'],
            settings_handle.plugs['BreakEndTangent']
        )
        root.add_plugs(
            settings_handle.plugs['LockLength'],
            settings_handle.plugs['BaseCtrlVis'],
            settings_handle.plugs['TweakCtrlVis'],
            keyable=False
        )
        this.spline_joints = spline_joints
        this.joints = joints
        this.settings_handle = settings_handle
        this.set_handles(handles)
        return this

    @staticmethod
    def build_nodes(
            parent_group,
            joint_group,
            degree,
            matrices,
            head_matrix,
            spline_matrices,
            legacy_joints,
            world_space_head
    ):

        controller = parent_group.controller
        size = parent_group.size
        if degree is None:
            if len(matrices) < 3:
                degree = 1
            elif len(matrices) < 4:
                degree = 2
            else:
                degree = 3

        segment_names = []
        for x in range(len(matrices)):
            if x == 0:
                segment_names.append('Root')
            else:
                segment_names.append(rig_factory.index_dictionary[x - 1].title())

        root_name = parent_group.root_name
        matrix_count = len(matrices)
        handles = []
        tweak_handles = []
        localized_transforms = []
        curve_transforms = []
        base_joints = []
        handle_parent = parent_group
        joint_parent = joint_group
        for x in range(len(matrices)):
            localized_transform = parent_group.create_child(
                Transform,
                root_name=root_name,
                matrix=matrices[x],
                segment_name='Localized%s' % segment_names[x],
                parent=joint_group
            )
            curve_transform = parent_group.create_child(
                Transform,
                root_name=root_name,
                matrix=matrices[x],
                segment_name='Curve%s' % segment_names[x],
                parent=joint_group
            )
            base_joint = parent_group.create_child(
                Joint,
                root_name=root_name,
                matrix=matrices[x],
                segment_name=segment_names[x],
                parent=joint_parent
            )
            curve_transforms.append(curve_transform)
            localized_transforms.append(localized_transform)
            base_joints.append(base_joint)
            joint_parent = base_joint
            controller.create_parent_constraint(base_joint, localized_transform)
            controller.create_scale_constraint(base_joint, localized_transform)
            if x < matrix_count - 2:
                handle = parent_group.create_child(
                    LocalHandle,
                    size=size * 1.25 if x == 0 else 1.5,
                    matrix=matrices[x],
                    shape='crown' if x == 0 else 'circle',
                    parent=handle_parent,
                    segment_name=segment_names[x],
                    rotation_order='xzy'
                )
                handle_parent = handle.gimbal_handle
                handles.append(handle)
            tweak_handle = parent_group.create_child(
                LocalHandle,
                size=size * 1.25 if x == 0 else 1.5,
                matrix=matrices[x],
                shape='square',
                parent=handle_parent,
                segment_name=segment_names[x],
                rotation_order='xzy',
                create_gimbal=False,
                subsidiary_name='Tweak'
            )
            tweak_handles.append(tweak_handle)
            controller.create_parent_constraint(tweak_handle, base_joint)
            controller.create_scale_constraint(tweak_handle, base_joint)

            controller.root.add_plugs(
                [
                    tweak_handle.plugs['tx'],
                    tweak_handle.plugs['ty'],
                    tweak_handle.plugs['tz'],
                    tweak_handle.plugs['rx'],
                    tweak_handle.plugs['ry'],
                    tweak_handle.plugs['rz'],
                    tweak_handle.plugs['sx'],
                    tweak_handle.plugs['sy'],
                    tweak_handle.plugs['sz']
                ]
            )

        settings_handle = parent_group.create_child(
            GroupedHandle,
            segment_name='Settings',
            shape='gear_simple',
            size=size * 0.5,
            group_count=1,
            parent=handles[0]
        )
        settings_handle.groups[0].plugs.set_values(
            rz=-90,
            tz=-1.5 * size
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )
        start_tangent_plug = settings_handle.create_plug(
            'BreakStartTangent',
            at='double',
            k=True,
            dv=0.5,
            max=1.0,
            min=0.0
        )
        end_tangent_plug = settings_handle.create_plug(
            'BreakEndTangent',
            at='double',
            k=True,
            dv=0.5,
            max=1.0,
            min=0.0
        )
        lock_length_plug = settings_handle.create_plug(
            'LockLength',
            at='bool',
            k=True,
            dv=False
        )
        base_vis_plug = settings_handle.create_plug(
            'BaseCtrlVis',
            attributeType='bool',
            keyable=False,
            defaultValue=False,
        )
        controller.scene.setAttr(base_vis_plug.name, channelBox=True)
        for crv in handles[0].curves:
            base_vis_plug.connect_to(crv.plugs['v'])
        tweak_vis_plug = settings_handle.create_plug(
            'TweakCtrlVis',
            attributeType='bool',
            keyable=False,
            defaultValue=False,
        )
        controller.scene.setAttr(tweak_vis_plug.name, channelBox=True)
        for tweak_handle in tweak_handles:
            for crv in tweak_handle.curves:
                tweak_vis_plug.connect_to(crv.plugs['v'])

        # settings_handle.create_plug(
        #     'squash',
        #     attributeType='float',
        #     keyable=True,
        #     defaultValue=0.0,
        # )
        # settings_handle.create_plug(
        #     'squashMin',
        #     attributeType='float',
        #     keyable=True,
        #     defaultValue=-0.5,
        # )
        # settings_handle.create_plug(
        #     'squashMax',
        #     attributeType='float',
        #     keyable=True,
        #     defaultValue=1.0,
        # )

        connect_transforms(localized_transforms[0], curve_transforms[0])
        connect_transforms(localized_transforms[-1], curve_transforms[-1])
        for i in range(2, len(matrices) - 2):
            connect_transforms(localized_transforms[i], curve_transforms[i])
        blend_transforms(
            localized_transforms[1],
            localized_transforms[0],
            curve_transforms[1],
            start_tangent_plug
        )
        blend_transforms(
            localized_transforms[-2],
            localized_transforms[-1],
            curve_transforms[-2],
            end_tangent_plug
        )

        # Creates the "Head" handle.
        head_handle = parent_group.create_child(
            LocalHandle,
            segment_name='Head',
            size=size,
            matrix=Matrix(matrices[-1].get_translation()) if world_space_head else matrices[-1],
            shape='cube_head',
            parent=handles[-1].gimbal_handle,
            rotation_order='xzy'
        )
        head_handle.set_shape_matrix(Matrix(head_matrix))

        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            tweak_handles[-1].groups[0],
            mo=True
        )
        controller.create_scale_constraint(
            head_handle.gimbal_handle,
            tweak_handles[-1].groups[0]
        )
        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            tweak_handles[-2].groups[0],
            mo=True
        )
        controller.create_scale_constraint(
            head_handle.gimbal_handle,
            tweak_handles[-2].groups[0],
        )

        spline_node = parent_group.create_child(
            DependNode,
            node_type='rigSpline',
            root_name=root_name,
            segment_name='Spline',
        )

        spline_node.plugs.set_values(
            sourceUpVector=5,
            squashType=0,
            scaleType=2,
            matrixType=1,
            twistType=1,
            originalLength=controller.scene.get_predicted_curve_length(
                [x.get_translation() for x in matrices],
                degree,
                0
            )
        )
        lock_length_plug.connect_to(spline_node.plugs['distributionType'])

        for i in range(len(curve_transforms)):
            curve_transforms[i].plugs['matrix'].connect_to(spline_node.plugs['inMatrices'].element(i))

        if degree is not None:
            spline_node.plugs['degree'].set_value(degree)

        spline_joint_parent = joint_group
        spline_joints = []

        for i, matrix in enumerate(spline_matrices):
            segment_string = rig_factory.index_dictionary[i].title()

            spline_joint = spline_joint_parent.create_child(
                Joint,
                segment_name='Secondary%s' % segment_string,
                matrix=matrix
            )

            if spline_joints:
                spline_joints[-1].plugs['scale'].connect_to(
                    spline_joint.plugs['inverseScale'],
                )
            # spline_joint.zero_rotation()
            spline_joints.append(spline_joint)
            spline_joint_parent = spline_joint
            spline_node.plugs['outTranslate'].element(i).connect_to(spline_joint.plugs['translate'])
            spline_node.plugs['outRotate'].element(i).connect_to(spline_joint.plugs['rotate'])
            spline_node.plugs['outScale'].element(i).connect_to(spline_joint.plugs['scale'])
            parameter_plug = spline_joint.create_plug('SplineParameter', at='double')
            parameter_plug.set_value(1.0 / (len(spline_matrices) - 1) * i)
            parameter_plug.connect_to(spline_node.plugs['inParameters'][i])

        for i in range(len(spline_joints)):
            this_position = controller.scene.xform(spline_joints[i], q=True, ws=True, t=True)
            if i == len(spline_matrices) - 1:
                other_position = controller.scene.xform(spline_joints[i - 1], q=True, ws=True, t=True)
            else:
                other_position = controller.scene.xform(spline_joints[i + 1], q=True, ws=True, t=True)
            local_position = [this_position[x] - other_position[x] for x in range(3)]
            segment_length = math.sqrt(sum(x ** 2 for x in local_position))
            segment_length_plug = spline_joints[i].create_plug('SegmentLength', at='double')
            segment_length_plug.set_value(segment_length)
            segment_length_plug.set_value(segment_length)
            segment_length_plug.connect_to(spline_node.plugs['segmentLengths'][i])

        head_joint = joint_group.create_child(
            Joint,
            segment_name='Head',
            matrix=matrices[-1]
        )
        controller.create_orient_constraint(head_handle.gimbal_handle, head_joint, mo=False)
        controller.create_point_constraint(spline_joints[-1], head_joint, mo=False)
        controller.create_scale_constraint(head_handle.gimbal_handle, head_joint)

        if legacy_joints:
            all_joints = list(base_joints)
        else:
            all_joints = []
            for joint in base_joints:
                joint.plugs['drawStyle'].set_value(2)
        all_joints.extend(spline_joints)
        all_joints.append(head_joint)
        all_handles = list(handles)
        all_handles.extend(tweak_handles)
        all_handles.append(head_handle)
        all_handles.append(settings_handle)

        return dict(
            handles=all_handles,
            joints=all_joints,
            settings_handle=settings_handle,
            spline_joints=spline_joints
        )

    def get_broken_tangents(self):
        return [
            self.settings_handle.plugs['BreakStartTangent'].get_value(),
            self.settings_handle.plugs['BreakEndTangent'].get_value()
        ]

    def set_broken_tangents(self, tangents):
        self.settings_handle.plugs['BreakStartTangent'].set_value(tangents[0])
        self.settings_handle.plugs['BreakEndTangent'].set_value(tangents[1])

    def get_blueprint(self):
        blueprint = super(BipedNeck, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['head_matrix'] = self.head_matrix
        blueprint['legacy_joints'] = self.legacy_joints
        blueprint['world_space_head'] = self.world_space_head
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeck, self).get_toggle_blueprint()
        blueprint['world_space_head'] = self.world_space_head
        return blueprint


def connect_transforms(driver, driven):
    for attribute in ['translate', 'rotate', 'scale']:
        driver.plugs[attribute].connect_to(driven.plugs[attribute])


def blend_transforms(driver_1, driver_2, driven, weight_plug):
    pair_blend = driven.create_child(
        DependNode,
        node_type='pairBlend',
        segment_name='%sBaseJointPairBlend' % driven.segment_name
    )
    blend_colors = driven.create_child(
        DependNode,
        node_type='blendColors',
        segment_name='%sBaseJointScaleBlend' % driven.segment_name
    )
    pair_blend.plugs['rotInterpolation'].set_value(1)
    driver_1.plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
    driver_2.plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
    pair_blend.plugs['outTranslate'].connect_to(driven.plugs['translate'])
    driver_1.plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
    driver_2.plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
    pair_blend.plugs['outRotate'].connect_to(driven.plugs['rotate'])
    driver_1.plugs['scale'].connect_to(blend_colors.plugs['color1'])
    driver_2.plugs['scale'].connect_to(blend_colors.plugs['color2'])
    blend_colors.plugs['output'].connect_to(driven.plugs['scale'])
    weight_plug.connect_to(blend_colors.plugs['blender'])
    weight_plug.connect_to(pair_blend.plugs['weight'])
