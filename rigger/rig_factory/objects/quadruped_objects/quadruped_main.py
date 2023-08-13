from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from Snowman3.rigger.rig_factory.objects.part_objects.part import PartGuide, Part
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class QuadrupedMainGuide(PartGuide):

    create_origin_joint = DataProperty(
        name='create_origin_joint',
        default_value=True
    )

    default_settings = dict(
        root_name='Main',
        size=10.0,
        side='center',
        create_origin_joint=True
    )

    def __init__(self, **kwargs):
        self.default_settings['root_name'] = 'Main'
        super(QuadrupedMainGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedMain.__name__

    @classmethod
    def create(cls, **kwargs):
        side = kwargs.setdefault('side', 'center')
        this = super(QuadrupedMainGuide, cls).create(**kwargs)
        controller = this.controller
        size = this.size
        size_plug = this.plugs['size']
        main_joint = this.create_child(
            Joint,
            index=0,
            segment_name='Main'
        )
        ground_joint = this.create_child(
            Joint,
            parent=main_joint,
            segment_name='Ground'
        )
        cog_joint = this.create_child(
            Joint,
            parent=ground_joint,
            segment_name='Cog'
        )

        handle = this.create_handle()
        cog_handle = this.create_handle(
            segment_name='Cog'
        )

        cone_x = cog_joint.create_child(
            Cone,
            segment_name='X',
            size=size * 0.1,
            axis=[1.0, 0.0, 0.0]
        )
        cone_y = cog_joint.create_child(
            Cone,
            segment_name='Y',
            size=size * 0.099,
            axis=[0.0, 1.0, 0.0]
        )
        cone_z = cog_joint.create_child(
            Cone,
            segment_name='Z',
            size=size * 0.098,
            axis=[0.0, 0.0, 1.0]
        )

        controller.create_matrix_parent_constraint(
            handle,
            main_joint
        )
        controller.create_matrix_parent_constraint(
            cog_handle,
            cog_joint
        )

        for obj in (handle, cog_handle, cone_x, cone_y, cone_z):
            size_plug.connect_to(obj.plugs['size'])
            size_plug.connect_to(obj.plugs['size'])

        main_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        ground_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        cog_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )

        origin_joint = None
        if this.create_origin_joint:
            origin_joint = this.create_child(
                Joint,
                side=None,  # Keep name consistent with new Root part
                root_name=None,
                segment_name='Origin'
            )
            origin_joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                radius=0.0
            )

        root = this.get_root()
        handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        cog_handle.mesh.assign_shading_group(root.shaders[side].shading_group)

        for obj, axis in zip((cone_x, cone_y, cone_z), ('x', 'y', 'z')):
            obj.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            obj.mesh.assign_shading_group(root.shaders[axis].shading_group)
            obj.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            obj.mesh.assign_shading_group(root.shaders[axis].shading_group)

        this.base_handles = [handle]
        this.joints = [main_joint, ground_joint, cog_joint]
        if origin_joint:
            this.joints.append(origin_joint)

        return this

    def get_blueprint(self):
        blueprint = super(QuadrupedMainGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedMainGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedMain(Part):

    create_origin_joint = DataProperty(
        name='create_origin_joint',
        default_value=True
    )

    cog_joint = ObjectProperty(
        name='cog_joint'
    )

    def __init__(self, **kwargs):
        super(QuadrupedMain, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(QuadrupedMain, cls).create(**kwargs)
        controller = this.controller
        size = this.size
        root_name = this.root_name
        matrices = this.matrices
        main_joint = this.joint_group.create_child(
            Joint,
            matrix=matrices[0]
        )
        ground_joint = this.joint_group.create_child(
            Joint,
            root_name=root_name,
            segment_name='Ground',
            parent=main_joint,
            matrix=matrices[1]
        )
        cog_joint = this.joint_group.create_child(
            Joint,
            root_name=root_name,
            segment_name='Cog',
            parent=ground_joint,
            matrix=matrices[2]
        )

        main_joint.plugs.set_values(
            overrideEnabled=1,
            overrideDisplayType=2
        )

        ground_joint.plugs.set_values(
            overrideEnabled=1,
            overrideDisplayType=2
        )

        main_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='cog_arrow',
            line_width=2,
            size=size*12,
            root_name=root_name,
            segment_name='Root',
            rotation_order='xzy',
            matrix=matrices[0],
        )
        ground_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='circle_c',
            line_width=2,
            size=size*3,
            parent=main_handle.gimbal_handle,
            segment_name='Ground',
            root_name=root_name,
            rotation_order='xzy',
            matrix=matrices[1],
        )

        cog_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='cog_arrows',
            line_width=2,
            size=size*8,
            parent=ground_handle.gimbal_handle,
            segment_name='Cog',
            root_name=root_name,
            rotation_order='xzy',
            matrix=matrices[2],
        )

        # The top root needs to create an Origin_Jnt
        # which can be used to keep things at origin
        origin_joint = None
        if this.create_origin_joint:
            origin_joint = this.joint_group.create_child(
                Joint,
                side=None,  # Keep name consistent with new Root part
                root_name=None,
                segment_name='Origin'
            )
            origin_joint.plugs.set_values(
                drawStyle=2
            )

        scale_xyz_plug = main_handle.create_plug(
            'ScaleXYZ',
            at='double',
            k=True,
            dv=1.0,
        )

        scale_xyz_plug.connect_to(main_handle.plugs['sx'])
        scale_xyz_plug.connect_to(main_handle.plugs['sy'])
        scale_xyz_plug.connect_to(main_handle.plugs['sz'])

        main_handle.plugs['sx'].set_locked(True)
        main_handle.plugs['sy'].set_locked(True)
        main_handle.plugs['sz'].set_locked(True)

        root = this.get_root()
        for handle in [main_handle, ground_handle, cog_handle]:
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz']
                ]
            )
        root.add_plugs(scale_xyz_plug)

        ground_joint.plugs.set_values(
            type=1,
            drawStyle=2
        )
        main_joint.plugs.set_values(
            type=1,
            drawStyle=2
        )
        cog_joint.plugs.set_values(
            drawStyle=2
        )

        controller.create_matrix_parent_constraint(
            ground_handle.gimbal_handle,
            ground_joint
        )
        controller.create_matrix_parent_constraint(
            main_handle.gimbal_handle,
            main_joint
        )
        controller.create_matrix_parent_constraint(
            cog_handle.gimbal_handle,
            cog_joint
        )

        this.joints = [main_joint, ground_joint, cog_joint]
        if origin_joint:
            this.joints.append(origin_joint)
        this.cog_joint = cog_joint

        return this
