from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from Snowman3.rigger.rig_factory.objects.part_objects.part import PartGuide, Part
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class BipedMainGuide(PartGuide):

    create_origin_joint = DataProperty(
        name='create_origin_joint',
        default_value=True
    )

    default_settings = dict(
        root_name='Main',
        size=10.0,
        create_origin_joint=True
    )

    def __init__(self, **kwargs):
        self.default_settings['root_name'] = 'Main'
        super(BipedMainGuide, self).__init__(**kwargs)
        self.toggle_class = BipedMain.__name__

    @classmethod
    def create(cls, **kwargs):
        side = kwargs.setdefault('side', 'center')
        this = super(BipedMainGuide, cls).create(**kwargs)
        controller = this.controller
        size = this.size
        size_plug = this.plugs['size']

        main_joint = this.create_child(Joint)

        ground_joint = this.create_child(
            Joint,
            parent=main_joint,
            segment_name='Ground'
        )

        handle = this.create_handle()

        cone_x = ground_joint.create_child(
            Cone,
            segment_name='X',
            size=size * 0.1,
            axis=[1.0, 0.0, 0.0]
        )
        cone_y = ground_joint.create_child(
            Cone,
            segment_name='Y',
            size=size * 0.099,
            axis=[0.0, 1.0, 0.0]
        )
        cone_z = ground_joint.create_child(
            Cone,
            segment_name='Z',
            size=size * 0.098,
            axis=[0.0, 0.0, 1.0]
        )

        controller.create_matrix_parent_constraint(
            handle,
            main_joint
        )
        for obj in (handle, cone_x, cone_y, cone_z):
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

        origin_joint = None
        if this.create_origin_joint:
            origin_joint = this.create_child(
                Joint,
                side=None,  # Keep name consistent with new Root part
                root_name=None, #  This makes it impossible to have more than one of these parts
                segment_name='Origin'
            )
            origin_joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                radius=0.0
            )

        root = this.get_root()
        handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        for obj, axis in zip((cone_x, cone_y, cone_z), ('x', 'y', 'z')):
            obj.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            obj.mesh.assign_shading_group(root.shaders[axis].shading_group)

        this.base_handles = [handle]
        this.joints = [main_joint, ground_joint]
        if origin_joint:
            this.joints.append(origin_joint)

        return this

    def get_blueprint(self):
        blueprint = super(BipedMainGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedMainGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedMain(Part):

    create_origin_joint = DataProperty(
        name='create_origin_joint',
        default_value=True
    )

    cog_joint = ObjectProperty(
        name='cog_joint'
    )

    def __init__(self, **kwargs):
        super(BipedMain, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedMain, cls).create(**kwargs)
        controller = this.controller
        size = this.size
        matrix = this.matrices[0]
        main_joint = this.create_child(
            Joint,
            parent=this.joint_group
        )
        ground_joint = this.create_child(
            Joint,
            segment_name='Ground',
            parent=main_joint
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
            size=size * 15,
            segment_name='Root',
            rotation_order='xzy',
            matrix=matrix,
        )
        ground_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='circle_c',
            line_width=2,
            size=size * 4,
            parent=main_handle.gimbal_handle,
            segment_name='Ground',
            rotation_order='xzy',
            matrix=matrix,
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
        for handle in [main_handle, ground_handle]:
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

        controller.create_matrix_parent_constraint(
            ground_handle.gimbal_handle,
            ground_joint
        )
        controller.create_matrix_parent_constraint(
            main_handle.gimbal_handle,
            main_joint
        )
        this.joints = [main_joint, ground_joint]
        if origin_joint:
            this.joints.append(origin_joint)
        this.cog_joint = ground_joint

        return this