from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
import Snowman3.rigger.rig_factory.environment as env



class HandleGuide(PartGuide):

    mirror_function = DataProperty( name='mirror_function' )
    shape = DataProperty( name='shape' )
    create_gimbal = DataProperty( name='create_gimbal' )
    up_line = ObjectProperty( name='up_line' )
    aim_line = ObjectProperty( name='aim_line' )
    allowed_modes = DataProperty( name='allowed_modes', default_value=['translation', 'orientation'] )
    # allowed_modes = ['translation', 'orientation']
    poly_shape = DataProperty( name='poly_shape', default_value='polyCube' )
    default_settings = dict(
        root_name='Handle',
        size=1.0,
        side='center',
        shape='cube',
        create_gimbal=True,
        mirror_function='default',
        poly_shape='polyCube'
    )


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = Handle.__name__


    def set_guide_mode(self, mode):
        if mode in self.allowed_modes:
            if mode == 'orientation':
                if self.handles[1].parent != self:
                    pass
                else:
                    self.handles[1].plugs['visibility'].set_value(False)
                    self.handles[2].plugs['visibility'].set_value(False)
                    self.up_line.plugs['visibility'].set_value(False)
                    self.aim_line.plugs['visibility'].set_value(False)
                    self.handles[0].set_matrix(self.joints[0].get_matrix())
                    self.handles[1].set_parent(self.handles[0])
                    self.handles[2].set_parent(self.handles[0])
                    self.handles[0].plugs['drawStyle'].set_value(2)
                    self.controller.scene.select(cl=True)

            if mode == 'translation':
                if self.handles[1].parent == self:
                    pass
                else:
                    self.handles[1].set_parent(self)
                    self.handles[2].set_parent(self)
                    self.handles[0].plugs['drawStyle'].set_value(0)
                    self.handles[1].plugs['visibility'].set_value(True)
                    self.handles[2].plugs['visibility'].set_value(True)
                    self.up_line.plugs['visibility'].set_value(True)
                    self.aim_line.plugs['visibility'].set_value(True)

                    matrix = self.handles[0].get_matrix()

                    up_position = list(matrix.get_translation() + (matrix.y_vector().normalize() * self.size))
                    up_matrix = Matrix(matrix)
                    up_matrix.set_translation(up_position)
                    self.handles[1].set_matrix(up_matrix)

                    aim_position = list(matrix.get_translation() + (matrix.z_vector().normalize() * -self.size))
                    aim_matrix = Matrix(matrix)
                    aim_matrix.set_translation(aim_position)
                    self.handles[2].set_matrix(aim_matrix)

                    self.handles[0].plugs['rotate'].set_value([0, 0, 0])
                    self.handles[1].plugs['rotate'].set_value([0, 0, 0])
                    self.handles[2].plugs['rotate'].set_value([0, 0, 0])
                    self.handles[1].plugs['jointOrient'].set_value([0, 0, 0])
                    self.handles[2].plugs['jointOrient'].set_value([0, 0, 0])
                    self.controller.scene.select(cl=True)


    @classmethod
    def create(cls, **kwargs):
        """
        Use rig_objects.handle_guide.CubeHandleGuide
        """
        handle_positions = kwargs.get('handle_positions', dict())
        kwargs.setdefault('side', 'center')
        #kwargs.setdefault('poly_shape', 'cube')
        this = super().create(**kwargs)
        controller = this.controller
        side = this.side
        size = this.size

        # Create nodes

        joint = this.create_child(
            Joint
        )
        handle_1 = this.create_handle(
            segment_name='Base',
        )
        handle_2 = this.create_handle(
            segment_name='Base',
            functionality_name='AimVector'

        )
        up_handle = this.create_handle(
            segment_name='Base',
            functionality_name='UpVector'

        )
        locator_1 = handle_1.create_child(
            Locator
        )
        locator_2 = handle_2.create_child(
            Locator
        )
        up_locator = up_handle.create_child(
            Locator
        )
        up_line = this.create_child(
            Line,
            segment_name='Up'
        )
        aim_line = this.create_child(
            Line,
            segment_name='Aim'
        )
        default_position_1 = list(env.side_aim_vectors[side])
        default_position_1[1] *= size
        default_position_2 = list(env.side_up_vectors[side])
        default_position_2[2] *= size
        position_1 = handle_positions.get(handle_1.name, [0.0, 0.0, 0.0])
        position_2 = handle_positions.get(handle_2.name, default_position_1)
        up_position = handle_positions.get(up_handle.name, default_position_2)
        handle_1.plugs['translate'].set_value(position_1)
        handle_2.plugs['translate'].set_value(position_2)
        up_handle.plugs['translate'].set_value(up_position)
        cube_transform = this.create_child(
            Transform,
            segment_name='Cube'
        )
        cube_node = cube_transform.create_child(
            DependNode,
            node_type=this.poly_shape #'polyCube', #,
        )
        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
        )
        cube_mesh = cube_transform.create_child(
            Mesh
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='ItemSize'
        )

        cone_x = joint.create_child(
            Cone,
            segment_name='ConeX',
            size=size,
            axis=[1.0, 0.0, 0.0]
        )
        cone_y = joint.create_child(
            Cone,
            segment_name='ConeY',
            size=size,
            axis=[0.0, 1.0, 0.0]
        )
        cone_z = joint.create_child(
            Cone,
            segment_name='ConeZ',
            size=size,
            axis=[0.0, 0.0, 1.0]
        )

        # Constraints

        joint.zero_rotation()
        controller.create_aim_constraint(
            handle_2,
            joint,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=env.aim_vector,
            upVector=env.up_vector
        )

        controller.create_point_constraint(
            handle_1,
            joint
        )

        controller.create_point_constraint(
            handle_1,
            cube_transform
        )
        controller.create_aim_constraint(
            handle_2,
            cube_transform,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=env.aim_vector,
            upVector=env.up_vector
        )

        # Attributes

        size_plug = this.plugs['size']
        size_plug.connect_to(multiply.plugs['input1X'])
        multiply.plugs['input2X'].set_value(0.25)
        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        locator_1.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point2'])
        locator_1.plugs['worldPosition'].element(0).connect_to(up_line.curve.plugs['controlPoints'].element(0))
        up_locator.plugs['worldPosition'].element(0).connect_to(up_line.curve.plugs['controlPoints'].element(1))
        locator_1.plugs['worldPosition'].element(0).connect_to(aim_line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(aim_line.curve.plugs['controlPoints'].element(1))

        if this.poly_shape == 'polyCube':
            size_plug.connect_to(cube_node.plugs['height'])
            size_plug.connect_to(cube_node.plugs['depth'])
            size_plug.connect_to(cube_node.plugs['width'])
        elif this.poly_shape == 'polySphere':
            radius_md = this.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='SphereRadius'
            )
            radius_md.plugs['input2X'].set_value(0.5)
            size_plug.connect_to(radius_md.plugs['input1X'])
            radius_md.plugs['outputX'].connect_to(cube_node.plugs['radius'])

        multiply.plugs['outputX'].connect_to(handle_1.plugs['size'])
        multiply.plugs['outputX'].connect_to(handle_2.plugs['size'])
        multiply.plugs['outputX'].connect_to(up_handle.plugs['size'])

        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        up_locator.plugs['visibility'].set_value(False)
        cube_mesh.plugs['overrideEnabled'].set_value(True)
        cube_mesh.plugs['overrideDisplayType'].set_value(2)
        cube_transform.plugs['overrideEnabled'].set_value(True)
        cube_transform.plugs['overrideDisplayType'].set_value(2)
        joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=size*0.25
        )
        up_handle.plugs['radius'].set_value(size*0.25)
        handle_1.plugs['radius'].set_value(size*0.25)
        handle_2.plugs['radius'].set_value(size*0.25)

        size_plug.connect_to(cone_x.plugs['size'])
        size_plug.connect_to(cone_y.plugs['size'])
        size_plug.connect_to(cone_z.plugs['size'])
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
        # Shaders
        root = this.get_root()
        handle_1.mesh.assign_shading_group(root.shaders[side].shading_group)
        handle_2.mesh.assign_shading_group(root.shaders[side].shading_group)
        up_handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        cone_x.mesh.assign_shading_group(root.shaders['x'].shading_group)
        cone_y.mesh.assign_shading_group(root.shaders['y'].shading_group)
        cone_z.mesh.assign_shading_group(root.shaders['z'].shading_group)

        root = this.get_root()
        if root:
            root.add_plugs(
                [
                    handle_1.plugs['tx'],
                    handle_1.plugs['ty'],
                    handle_1.plugs['tz'],
                    handle_2.plugs['tx'],
                    handle_2.plugs['ty'],
                    handle_2.plugs['tz'],
                    up_handle.plugs['tx'],
                    up_handle.plugs['ty'],
                    up_handle.plugs['tz'],

                ]
            )
        this.up_line = up_line
        this.aim_line = aim_line
        this.base_handles = [handle_1]
        this.joints = [joint]
        return this


    def prepare_for_toggle(self):
        super().prepare_for_toggle()
        self.set_guide_mode('translation')
        self.controller.snap_handles_to_mesh_positions(self.get_root())



class Handle(Part):

    deformers = ObjectListProperty( name='deformers' )
    geometry = ObjectListProperty( name='geometry' )
    shape = DataProperty( name='shape' )
    create_gimbal = DataProperty( name='create_gimbal' )
    mirror_function = DataProperty( name='mirror_function' )


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        controller = this.controller
        size = this.size
        mirror_function = this.mirror_function
        handle_matrix = this.matrices[0]
        handle_matrix = Matrix(handle_matrix)
        joint = this.create_child(
            Joint,
            index=0,
            matrix=handle_matrix,
            parent=this.joint_group
        )
        if mirror_function == 'behaviour' and this.side == 'right':
            default_mat = handle_matrix
            trans_values = default_mat.get_translation()
            # behaviour mirror along X axis
            mirror_x = Matrix()
            mirror_x.data = (
                    (1.0, 0.0, 0.0, 0.0),
                    (0.0, -1.0, 0.0, 0.0),
                    (0.0, 0.0, -1.0, 0.0),
                    (0.0, 0.0, 0.0, 1.0)
                )
            default_mat = default_mat * mirror_x

            default_mat.set_translation(trans_values)
            handle_matrix = [default_mat]

        elif mirror_function == 'orientation' and this.side == 'right':

            default_mat = handle_matrix
            trans_values = default_mat.get_translation()

            default_mat.mirror_matrix()
            default_mat.set_translation(trans_values)

            default_mat.flip_x()
            handle_matrix = [default_mat]

        elif mirror_function == 'reverseX' and this.side == 'right':
            default_mat = handle_matrix
            default_mat.flip_x()

            handle_matrix = [default_mat]

        handle = this.create_handle(
            handle_type=GroupedHandle,
            shape=this.shape if this.shape else 'cube',
            size=size,
            matrix=handle_matrix,
            create_gimbal=this.create_gimbal
        )

        handle.mirror_plugs = ['translateX', 'rotateY', 'rotateZ']

        joint.zero_rotation()
        joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )

        if handle.gimbal_handle:
            controller.create_parent_constraint(
                handle.gimbal_handle,
                joint
            )
            controller.create_scale_constraint(
                handle.gimbal_handle,
                joint, mo=1
            )
        else:
            controller.create_parent_constraint(
                handle,
                joint
            )
            controller.create_scale_constraint(
                handle,
                joint, mo=1
            )

        root = this.get_root()
        if root:
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz']
                ]
            )

        this.joints = [joint]
        return this

