import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.rig_objects.capsule import Capsule
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
import Snowman3.rigger.rig_factory as rig_factory



class ChainGuide(PartGuide):

    capsules = ObjectListProperty( name='capsules' )
    locators = ObjectListProperty( name='locators' )
    up_handles = ObjectListProperty( name='up_handles' )
    up_locators = ObjectListProperty( name='up_locators' )
    segment_names = DataProperty( name='segment_names', default_value=[] )
    count = DataProperty( name='count' )
    up_vector_indices = DataProperty( name='up_vector_indices', default_value=[0] )
    default_settings = dict( count=4, root_name='Chain', )
    up_lines = ObjectListProperty( name='up_line' )
    temp_constraints = ObjectListProperty( name='temp_constraint' )
    allowed_modes = DataProperty( name='allowed_modes', default_value=[] )


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = Chain.__name__


    def set_guide_mode(self, mode):
        """
        This should do nothing if the mode is already what's being set.
        """
        if mode not in self.allowed_modes:
            return

        def set_orientation_guide_mode():
            if self.handles[1].parent != self:
                pass
            else:
                count = self.count

                base_handles_matrices = []
                for joint in self.joints:
                    base_handles_matrices.append(joint.get_matrix(world_space=False))

                self.base_handles[0].set_matrix(self.joints[0].get_matrix())

                i = 1
                while i != count:
                    self.base_handles[i].set_parent(self.base_handles[i - 1])
                    self.base_handles[i].set_matrix(base_handles_matrices[i], world_space=False)

                    self.base_handles[i].plugs['jointOrient'].set_value([0, 0, 0])
                    self.base_handles[i].set_matrix(base_handles_matrices[i], world_space=False)

                    i = i + 1

                for i, up_index in enumerate(self.up_vector_indices):
                    base_handle = self.base_handles[up_index]
                    up_handle = self.up_handles[i]
                    temp_const = self.controller.create_parent_constraint(
                        base_handle,
                        up_handle,
                        mo=True
                    )
                    self.temp_constraints.append(temp_const)
                    up_handle.plugs['visibility'].set_value(False)
                for line in self.up_lines:
                    line.plugs['visibility'].set_value(False)

                self.controller.scene.select(cl=True)

        def set_translation_guide_mode():
            if self.handles[1].parent == self:
                pass
            else:
                for handle in self.base_handles[1:]:
                    handle.set_parent(self)
                for handle in self.base_handles[1:]:
                    handle.plugs['rotate'].set_value([0, 0, 0])
                    handle.plugs['jointOrient'].set_value([0, 0, 0])
                for i, up_index in enumerate(self.up_vector_indices):
                    up_handle = self.up_handles[i]
                    up_handle.plugs['visibility'].set_value(True)
                for line in self.up_lines:
                    line.plugs['visibility'].set_value(True)
                if self.temp_constraints:
                    self.controller.schedule_objects_for_deletion(self.temp_constraints)
                    self.temp_constraints = []
                    self.controller.delete_scheduled_objects()
                self.base_handles[0].plugs['rotate'].set_value([0, 0, 0])

        if mode == 'orientation':
            set_orientation_guide_mode()
        if mode == 'translation':
            set_translation_guide_mode()


    @classmethod
    def create(cls, **kwargs):
        side = kwargs.setdefault('side', 'center')
        side_vectors = env.side_world_vectors[side]
        this = super().create(**kwargs)
        controller = this.controller
        part_segment_name = this.segment_name
        root = this.get_root()
        size = this.size
        spacing = size * 5.0
        size_plug = this.plugs['size']
        joint_parent = this
        aim_vector = env.aim_vector
        up_vector = env.up_vector
        handle_positions = kwargs.get('handle_positions', dict())
        if side == 'R':
            aim_vector = [x * -1.0 for x in env.aim_vector]
            up_vector = [x * -1.0 for x in env.up_vector]
        size_multiply = this.create_child( DependNode, node_type='multiplyDivide', functionality_name='Size' )
        size_plug.connect_to(size_multiply.plugs['input1X'])
        size_plug.connect_to(size_multiply.plugs['input1Y'])
        size_multiply.plugs['input2X'].set_value(0.5)
        size_multiply.plugs['input2Y'].set_value(0.25)

        joints = []
        handles = []
        locators = []
        up_handles = []
        base_handles = []
        segment_up_handles = []
        capsules = []
        up_handle_lines = dict()
        current_up_handle = None
        up_locators = []
        for i in range(this.count):
            if this.segment_names and i < len(this.segment_names):
                segment_name = this.segment_names[i]
            else:
                segment_name = rig_factory.index_dictionary[i].title()

            if i in this.up_vector_indices:
                up_handle = this.create_handle(
                    index=len(up_handles),
                    segment_name=segment_name,
                    functionality_name='UpVector'
                )
                position = handle_positions.get(up_handle.name, [
                    side_vectors[0] * (spacing * i),
                    side_vectors[1] * (spacing * i),
                    spacing * -5
                ])
                up_handle.plugs['translate'].set_value(position)
                up_handle.mesh.assign_shading_group(this.get_root().shaders[side].shading_group)
                size_multiply.plugs['outputY'].connect_to(up_handle.plugs['size'])
                root.add_plugs( [ up_handle.plugs['tx'],
                                  up_handle.plugs['ty'],
                                  up_handle.plugs['tz'] ] )
                up_handles.append(up_handle)
                current_up_handle = up_handle
            segment_up_handles.append(current_up_handle)
            joint = joint_parent.create_child( Joint, segment_name=segment_name )
            handle = this.create_handle( segment_name=segment_name )
            position = handle_positions.get(handle.name, [x * (spacing * i) for x in side_vectors])
            handle.plugs['translate'].set_value(position)
            root.add_plugs( [ handle.plugs['tx'],
                              handle.plugs['ty'],
                              handle.plugs['tz'] ] )
            cone_x = joint.create_child(
                Cone,
                segment_name=f'{segment_name}ConeX',
                index=i,
                size=size,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                segment_name=f'{segment_name}ConeY',
                index=i,
                size=size,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                segment_name=f'{segment_name}ConeZ',
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
                radius=0.0,
                overrideEnabled=True,
                overrideDisplayType=2,
                overrideRGBColors=True,
                overrideColorR=0.0,
                overrideColorG=0.0,
                overrideColorB=0.0
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
            locator.plugs.set_values( visibility=False )
            locator.plugs['visibility'].set_value(False)
            root = this.get_root()
            handle.mesh.assign_shading_group(root.shaders[side].shading_group)
            cone_x.mesh.assign_shading_group(root.shaders['x'].shading_group)
            cone_y.mesh.assign_shading_group(root.shaders['y'].shading_group)
            cone_z.mesh.assign_shading_group(root.shaders['z'].shading_group)
            joints.append(joint)
            locators.append(locator)
            handles.append(handle)
            base_handles.append(handle)
            joint_parent = joint
        for i in range(this.count):
            up_handle = segment_up_handles[i]
            if i < this.count - 1:
                if part_segment_name:
                    segment_name = '{}{}'.format(part_segment_name, rig_factory.index_dictionary[i].title()),
                else:
                    segment_name = rig_factory.index_dictionary[i]
                capsule = this.create_child(
                    Capsule,
                    index=i,
                    segment_name=f'f{segment_name}Segment',
                    parent=this
                )
                capsule.mesh.assign_shading_group(this.get_root().shaders[side].shading_group)
                size_plug.connect_to(capsule.plugs['size'])
                locator_1 = locators[i]
                locator_2 = locators[i + 1]
                joint_1 = joints[i]
                joint_2 = joints[i + 1]
                locator_1.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position1'])
                locator_2.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position2'])
                controller.create_point_constraint(joint_1, joint_2, capsule)
                controller.create_aim_constraint(
                    joint_2,
                    capsule,
                    aimVector=env.aim_vector
                )
                controller.create_aim_constraint(
                    handles[i + 1],
                    joints[i],
                    worldUpType='object',
                    worldUpObject=up_handle.get_selection_string(),
                    aimVector=aim_vector,
                    upVector=up_vector
                )
                capsules.append(capsule)
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
                line = this.create_child(
                    Line,
                    segment_name=rig_factory.index_dictionary[i].title()
                )
                locator_1 = locators[i]
                locator_2 = up_handle.create_child(Locator)
                locator_2.plugs.set_values(
                    visibility=False
                )
                locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
                locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
                up_handle_lines[up_handle] = line
                up_locators.append(locator_2)
                this.up_lines.append(line)

        handles.extend(up_handles)
        this.handles = handles
        this.locators = locators
        this.up_locators = up_locators

        this.capsules = capsules
        this.up_handles = up_handles
        this.joints = joints
        this.base_handles = base_handles
        return this


    def prepare_for_toggle(self):
        super().prepare_for_toggle()
        self.controller.snap_handles_to_mesh_positions(self.get_root())



class Chain(Part):
    """
    Added Part for consistency with other rig_factory objects
    Not intended for actual use
    """

    capsules = ObjectListProperty( name='capsules' )
    locators = ObjectListProperty( name='locators' )
    up_handles = ObjectListProperty( name='up_handles' )
    count = DataProperty( name='count' )

    default_settings = dict(count=4)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        controller = this.controller
        matrices = this.matrices
        size = this.size
        side = this.side
        handles = []
        joints = this.joints

        # Chain Handle
        joint_parent = this.joint_group
        handle_parent = this
        for x, matrix in enumerate(matrices):
            segment_name = rig_factory.index_dictionary[x].title()

            joint = this.create_child(
                Joint,
                segment_name=segment_name,
                index=x,
                matrix=matrix,
                parent=joint_parent
            )
            joint_parent = joint
            joint.zero_rotation()
            joint.plugs.set_values( overrideEnabled=1, overrideDisplayType=2 )
            joints.append(joint)
            if x != len(matrices) - 1:
                fk_handle = this.create_handle(
                    segment_name=segment_name,
                    index=x,
                    size=size * 2.5,
                    matrix=matrix,
                    side=side,
                    shape='cube',
                    parent=handle_parent
                )
                controller.create_parent_constraint(
                    fk_handle,
                    joint
                )
                fk_handle.plugs['scale'].connect_to(joint.plugs['scale'])
                fk_handle.plugs['rotateOrder'].connect_to(joint.plugs['rotateOrder'])
                fk_handle.stretch_shape(matrices[x + 1].get_translation())
                handle_parent = fk_handle
                handles.append(fk_handle)
        for fk_handle in handles:
            this.get_root().add_plugs([ fk_handle.plugs['rx'],
                                        fk_handle.plugs['ry'],
                                        fk_handle.plugs['rz'] ])
        joints[0].plugs['type'].set_value(1)
        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)

        return this

