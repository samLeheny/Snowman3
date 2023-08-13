import logging
import traceback
import copy
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.deformer_parts.base_deformer_part import BaseDeformerPart
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.deformer_objects.lattice import Lattice
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
import Snowman3.rigger.rig_factory.utilities.legacy_data_utilities as ldu
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory as rig_factory


class NewLatticeSquishGuide(PartGuide):

    default_settings = {
        'root_name': 'Squish',
        'bend_multiplier': 1.0,
        'root_bend_multiplier': 0.5,
        'side':'center'
    }
    start_joint = ObjectProperty( name='start_joint' )
    center_joint = ObjectProperty( name='center_joint' )
    end_joint = ObjectProperty( name='end_joint' )
    root_bend_multiplier = DataProperty( name='root_bend_multiplier', default_value=0.5 )
    bend_multiplier = DataProperty( name='bend_multiplier', default_value=1.0 )
    split_deformers = DataProperty( name='split_deformers' )

    @classmethod
    def create(cls, **kwargs):
        handle_positions = kwargs.get('handle_positions', dict())
        kwargs.setdefault('side', 'center')
        this = super(NewLatticeSquishGuide, cls).create(**kwargs)
        controller = this.controller
        side = this.side
        size = this.size
        root_bend_multiplier = this.root_bend_multiplier
        bend_multiplier = this.bend_multiplier

        joint_1 = this.create_child(
            Joint,
            segment_name='A',
        )
        joint_2 = joint_1.create_child(
            Joint,
            segment_name='B',
        )

        center_joint = this.create_child(
            Joint,
            segment_name='Center',
        )

        handle_1 = this.create_handle(
            segment_name='A',
        )
        handle_2 = this.create_handle(
            segment_name='B',
        )
        up_handle = this.create_handle(
            index=0,
            segment_name='A',
            functionality_name='UpVector'
        )
        locator_1 = joint_1.create_child(
            Locator
        )
        locator_2 = joint_2.create_child(
            Locator
        )
        up_locator = up_handle.create_child(
            Locator
        )

        line = this.create_child(
            Line
        )
        position_1 = handle_positions.get(handle_1.name, [0.0, 0.0, 0.0])
        position_2 = handle_positions.get(
            handle_2.name,
            [x * size * 3 for x in env.side_world_vectors[side]],
        )
        up_position = handle_positions.get(up_handle.name, [0.0, 0.0, size * -3])
        handle_1.plugs['translate'].set_value(position_1)
        handle_2.plugs['translate'].set_value(position_2)
        up_handle.plugs['translate'].set_value(up_position)
        cube_transform = this.create_child(
            Transform,
            segment_name='Cube'
        )
        cube_node = cube_transform.create_child(
            DependNode,
            node_type='polyCube',
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
        )

        # Constraints

        joint_1.zero_rotation()
        joint_2.zero_rotation()
        controller.create_aim_constraint(
            handle_2,
            joint_1,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=env.aim_vector,
            upVector=env.up_vector
        )
        controller.create_aim_constraint(
            handle_1,
            joint_2,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=[x*-1 for x in env.aim_vector],
            upVector=env.up_vector
        )
        controller.create_point_constraint(
            handle_1,
            joint_1
        )
        controller.create_point_constraint(
            handle_2,
            joint_2
        )
        controller.create_point_constraint(
            joint_1,
            joint_2,
            cube_transform
        )
        controller.create_parent_constraint(
            joint_1,
            joint_2,
            center_joint
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
        multiply.plugs['input2X'].set_value(4.0)
        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        locator_1.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point2'])
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        up_locator.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
        distance_node.plugs['distance'].connect_to(cube_node.plugs['height'])
        size_plug.connect_to(handle_1.plugs['size'])
        size_plug.connect_to(handle_2.plugs['size'])
        size_plug.connect_to(up_handle.plugs['size'])
        multiply.plugs['outputX'].connect_to(cube_node.plugs['depth'])
        multiply.plugs['outputX'].connect_to(cube_node.plugs['width'])
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        up_locator.plugs['visibility'].set_value(False)
        cube_mesh.plugs['overrideEnabled'].set_value(True)
        cube_mesh.plugs['overrideDisplayType'].set_value(2)
        cube_transform.plugs['overrideEnabled'].set_value(True)
        cube_transform.plugs['overrideDisplayType'].set_value(2)
        joint_1.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        joint_2.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        center_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )

        # Multiplier plug
        root_bend_multiplier_plug = this.create_plug(
            'root_bend_multiplier',
            at='float',
            min=0.0,
            max=1.0,
            dv=root_bend_multiplier,
            keyable=True
        )

        bend_multiplier_plug = this.create_plug(
            'bend_multiplier',
            at='float',
            min=0.0,
            dv=bend_multiplier,
            keyable=True
        )

        root = this.get_root()
        handle_1.mesh.assign_shading_group(root.shaders[side].shading_group)
        handle_2.mesh.assign_shading_group(root.shaders[side].shading_group)
        up_handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        this.start_joint = joint_1
        this.center_joint = center_joint
        this.end_joint = joint_2
        return this

    def __init__(self, **kwargs):
        super(NewLatticeSquishGuide, self).__init__(**kwargs)
        self.toggle_class = NewLatticeSquish.__name__

    def get_toggle_blueprint(self):
        blueprint = super(NewLatticeSquishGuide, self).get_toggle_blueprint()
        blueprint['matrices'] = [list(self.start_joint.get_matrix()), list(self.end_joint.get_matrix())]
        blueprint['root_bend_multiplier'] = self.plugs['root_bend_multiplier'].get_value()
        blueprint['bend_multiplier'] = self.plugs['bend_multiplier'].get_value()
        blueprint['split_deformers'] = self.split_deformers
        return blueprint

    def get_blueprint(self):
        blueprint = super(NewLatticeSquishGuide, self).get_blueprint()
        blueprint['root_bend_multiplier'] = self.plugs['root_bend_multiplier'].get_value()
        blueprint['bend_multiplier'] = self.plugs['bend_multiplier'].get_value()
        blueprint['split_deformers'] = self.split_deformers
        return blueprint


class NewLatticeSquish(BaseDeformerPart):

    main_handle = ObjectProperty(
        name='main_handle'
    )

    root_bend_multiplier = DataProperty(
        name='root_bend_multiplier',
        default_value=0.5
    )

    bend_multiplier = DataProperty(
        name='bend_multiplier',
        default_value=1.0
    )

    def __init__(self, **kwargs):
        super(NewLatticeSquish, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(NewLatticeSquish, cls).create(**kwargs)
        controller = this.controller
        root = this.get_root()
        size = this.size
        root_bend_multiplier = this.root_bend_multiplier
        bend_multiplier = this.bend_multiplier

        # Extract data from matrices
        matrices = copy.deepcopy(this.matrices)
        main_handle_matrix = Matrix(matrices[-1])
        start_position = matrices[0].get_translation()
        end_position = matrices[1].get_translation()
        main_handle_matrix.set_translation(end_position)
        end_position = matrices[1].get_translation()
        joint_distance = (end_position - start_position).mag()

        # Generate a middle position half way between start and end
        middle_matrix = Matrix(matrices[0])
        middle_position = (start_position * 0.5) + (end_position * 0.5)
        middle_matrix.set_translation(middle_position)
        matrices.insert(1, middle_matrix)

        joint_driver_parent = this
        handle_parent = this
        joints = []
        fk_handles = []

        main_handle = this.create_handle(
            shape='arrow_vertical',
            size=size,
            matrix=main_handle_matrix,
            segment_name='Main',
            create_gimbal=False
        )

        this.main_handle = main_handle

        # Multiplier plug
        root_bend_multiplier_plug = main_handle.create_plug(
            'root_bend_multiplier',
            at='float',
            min=0.0,
            max=1.0,
            dv=root_bend_multiplier,
            keyable=True
        )

        bend_multiplier_plug = main_handle.create_plug(
            'bend_multiplier',
            at='float',
            min=0.0,
            dv=bend_multiplier,
            keyable=True
        )

        fk_handle_vis_plug = main_handle.create_plug(
            'FkHandlesVis',
            at='long',
            keyable=True,
            min=0,
            max=1,
            dv=0
        )
        ik_handle_vis_plug = main_handle.create_plug(
            'IkHandlesVis',
            at='long',
            keyable=True,
            min=0,
            max=1,
            dv=0
        )

        root.add_plugs(
            root_bend_multiplier_plug,
            bend_multiplier_plug,
            main_handle.plugs['tx'],
            main_handle.plugs['ty'],
            main_handle.plugs['tz'],
            fk_handle_vis_plug,
            ik_handle_vis_plug,
        )
        for i in range(len(matrices)):
            index_character = rig_factory.index_dictionary[i].upper()
            fk_handle = this.create_handle(
                shape='circle',
                matrix=matrices[i],
                segment_name=index_character,
                parent=handle_parent,
                size=size*4.0,
                create_gimbal=False
            )
            ik_handle = this.create_handle(
                shape='ring',
                matrix=matrices[i],
                segment_name='{0}Ik'.format(index_character),
                parent=fk_handle,
                size=size * 4.0,
                create_gimbal=False
            )
            # Scale controls down in y-axis a bit
            shape_matrix = Matrix()
            shape_matrix.set_scale([
                size * 4.0,
                size,
                size * 4.0,
            ])
            ik_handle.plugs['shapeMatrix'].set_value(list(shape_matrix))
            joint = this.create_child(
                Joint,
                parent=this.joint_group,
                segment_name=index_character,
                matrix=matrices[i]
            )
            joint.plugs['v'].set_value(False)
            joint_driver = this.create_child(
                Transform,
                segment_name='Driver{0}'.format(index_character),
                matrix=matrices[i]
            )
            controller.create_parent_constraint(
                ik_handle,
                joint_driver,
                mo=False
            )
            controller.create_scale_constraint(
                ik_handle,
                joint_driver,
                mo=False
            )
            # USe direct connection to fix double transforms
            joint_driver.plugs['translate'].connect_to(joint.plugs['translate'])
            joint_driver.plugs['rotate'].connect_to(joint.plugs['rotate'])
            joint_driver.plugs['scale'].connect_to(joint.plugs['scale'])
            # If mid section, create two separate joints for more control on lattice shearing shape
            if index_character == 'B':
                front_left_sub_joint = this.create_child(
                    Joint,
                    parent=joint,
                    segment_name='{0}FrontLeftSub'.format(index_character),
                    matrix=matrices[i]
                )
                front_right_sub_joint = this.create_child(
                    Joint,
                    parent=joint,
                    segment_name='{0}FrontRightSub'.format(index_character),
                    matrix=matrices[i]
                )
                back_left_sub_joint = this.create_child(
                    Joint,
                    parent=joint,
                    segment_name='{0}BackLeftSub'.format(index_character),
                    matrix=matrices[i]
                )
                back_right_sub_joint = this.create_child(
                    Joint,
                    parent=joint,
                    segment_name='{0}BackRightSub'.format(index_character),
                    matrix=matrices[i]
                )
            root.add_plugs(
                fk_handle.plugs['tx'],
                fk_handle.plugs['ty'],
                fk_handle.plugs['tz'],
                fk_handle.plugs['rx'],
                fk_handle.plugs['ry'],
                fk_handle.plugs['rz'],
                fk_handle.plugs['sx'],
                fk_handle.plugs['sy'],
                fk_handle.plugs['sz'],
                ik_handle.plugs['tx'],
                ik_handle.plugs['ty'],
                ik_handle.plugs['tz'],
                ik_handle.plugs['rx'],
                ik_handle.plugs['ry'],
                ik_handle.plugs['rz'],
                ik_handle.plugs['sx'],
                ik_handle.plugs['sy'],
                ik_handle.plugs['sz']
            )
            handle_parent = fk_handle
            fk_handles.append(fk_handle)
            joints.append(joint)

            # Connect fk handles to visibility plug
            fk_handle_curves = fk_handle.curves
            for curve in fk_handle_curves:
                fk_handle_vis_plug.connect_to(curve.plugs['v'])

            # Connect ik handles to visibility plug
            ik_handle_curves = ik_handle.curves
            for curve in ik_handle_curves:
                ik_handle_vis_plug.connect_to(curve.plugs['v'])

            # Turn off inherit transform on joint group to fix double transforms when parented
            this.joint_group.plugs['inheritsTransform'].set_value(0.0)

            if index_character == 'B':
                joints.append(front_left_sub_joint)
                joints.append(front_right_sub_joint)
                joints.append(back_left_sub_joint)
                joints.append(back_right_sub_joint)

        lattice_matrix = Matrix(matrices[0])
        lattice_matrix.set_translation(middle_position)
        this.deformer = this.create_child(
            Lattice,
            segment_name='Volume',
            matrix=lattice_matrix
        )
        root.geometry[this.deformer.lattice_shape.name] = this.deformer.lattice_shape
        length = (end_position - start_position).mag()
        this.deformer.plugs['sy'].set_value(length)
        this.deformer.plugs['sx'].set_value(size*4.0)
        this.deformer.plugs['sz'].set_value(size*4.0)
        this.deformer.lattice_shape.plugs['tDivisions'].set_value(3)
        this.deformer.lattice_shape.plugs['sDivisions'].set_value(2)
        this.deformer.lattice_shape.plugs['uDivisions'].set_value(2)

        # Scaling for squash
        for i in range(len(fk_handles)):
            squash_scale_total_pma = this.create_child(
                DependNode,
                node_type='plusMinusAverage',
                segment_name='SquashTotal{0}'.format(rig_factory.index_dictionary[i].title())
            )
            squash_scale_total_pma.plugs['input3D'].element(3).child(1).set_value(1.0)  # Y Axis

            if i == 0:
                squash_scale_values = [(0, -0.04), (0, -0.04),
                                       (0.5, 0.55),  # At Zero
                                       (0.625, 1.125), (0.75, 1.95), (0.875, 3.35), (1.0, 6)]  # Squashed down
                squash_scale_total_pma.plugs['input3D'].element(3).child(0).set_value(0.450)
                squash_scale_total_pma.plugs['input3D'].element(3).child(2).set_value(0.450)
            elif i == 1:
                squash_scale_values = [(0, 0.45), (0.5, 0.55), (0.75, 0.50), (1, 0.375)]
                squash_scale_total_pma.plugs['input3D'].element(3).child(0).set_value(0.450)
                squash_scale_total_pma.plugs['input3D'].element(3).child(2).set_value(0.450)
            elif i == 2:
                squash_scale_values = [(0, 1.30), (0.5, 0.55), (0.75, 0.04), (1, -0.15)]
                squash_scale_total_pma.plugs['input3D'].element(3).child(0).set_value(0.450)
                squash_scale_total_pma.plugs['input3D'].element(3).child(2).set_value(0.450)
            squash_scale_plug = main_handle.plugs['translateY'].remap(*squash_scale_values)
            squash_scale_remap = squash_scale_plug.get_node()

            squash_scale_remap.plugs['outputMin'].set_value(0.0001)
            squash_scale_remap.plugs['inputMin'].set_value(joint_distance * 2.0)
            squash_scale_remap.plugs['inputMax'].set_value(-joint_distance * 2.0)

            for value_index in range(len(squash_scale_values)):
                squash_scale_remap.plugs['value'].element(value_index).child(2).set_value(1)

            squash_scale_remap.plugs['outValue'].connect_to(squash_scale_total_pma.plugs['input3D'].element(i).child(0))

            squash_scale_remap.plugs['outValue'].connect_to(squash_scale_total_pma.plugs['input3D'].element(i).child(2))

            squash_scale_total_pma.plugs['output3D'].connect_to(fk_handles[i].ofs.plugs['scale'])

        # Translation for squash
        squash_translate_total_pma = this.create_child(
            DependNode,
            node_type='plusMinusAverage',
            segment_name='SquashTranslate'
        )
        for direction in ['Up', 'Down']:
            squash_translate_clamp = this.create_child(
                DependNode,
                node_type='clamp',
                segment_name='SquashTranslate{0}Normalize'.format(direction)
            )
            squash_translate_input_max_mdl = this.create_child(
                DependNode,
                node_type='multDoubleLinear',
                segment_name='SquashTranslate{0}InputMax'.format(direction)
            )
            squash_translate_output_max_mdl = this.create_child(
                DependNode,
                node_type='multDoubleLinear',
                segment_name='SquashTranslate{0}OutputMax'.format(direction)
            )
            squash_translate_mdl = this.create_child(
                DependNode,
                node_type='multDoubleLinear',
                segment_name='SquashTranslate{0}'.format(direction)
            )
            main_handle.plugs['translateY'].connect_to(squash_translate_clamp.plugs['inputR'])
            squash_translate_mdl.plugs['input2'].set_value(0.5)

            squash_translate_clamp.plugs['outputR'].connect_to(squash_translate_input_max_mdl.plugs['input1'])
            squash_translate_input_max_mdl.plugs['input2'].set_value(0.5)
            squash_translate_clamp.plugs['outputR'].connect_to(squash_translate_output_max_mdl.plugs['input1'])
            squash_translate_output_max_mdl.plugs['input2'].set_value(0.5)

            if direction == 'Up':
                squash_translate_values = [(0, 1.0)]
                squash_translate_clamp.plugs['maxR'].set_value(99999)

                squash_translate_plug = main_handle.plugs['translateY'].remap(*squash_translate_values)
                squash_translate_remap = squash_translate_plug.get_node()
                squash_translate_remap.plugs['inputMin'].set_value(0.0)
                squash_translate_remap.plugs['inputMax'].set_value(joint_distance * 2.0)
                squash_translate_remap.plugs['outputMin'].set_value(0.0)
                squash_translate_output_max_mdl.plugs['output'].connect_to(squash_translate_remap.plugs['outputMax'])
                squash_translate_remap.plugs['outValue'].connect_to(
                    squash_translate_total_pma.plugs['input1D'].element(0)
                )
            else:
                squash_translate_values = [(0, 0.67), (0.5, 0.50), (0.75, 0.35), (1, 0.1)]
                squash_translate_clamp.plugs['minR'].set_value(-99999)

                squash_translate_plug = main_handle.plugs['translateY'].remap(*squash_translate_values)
                squash_translate_remap = squash_translate_plug.get_node()
                squash_translate_remap.plugs['inputMin'].set_value(-joint_distance * 2.0)
                squash_translate_remap.plugs['inputMax'].set_value(0.0)
                squash_translate_output_max_mdl.plugs['output'].connect_to(squash_translate_remap.plugs['outputMin'])
                squash_translate_remap.plugs['outputMax'].set_value(0.0)
                squash_translate_remap.plugs['outValue'].connect_to(
                    squash_translate_total_pma.plugs['input1D'].element(1)
                )

        bend_adls = []
        for i, sub_jnt_name in enumerate([
            'FrontLeftSubJnt',
            'FrontRightSubJnt',
            'BackLeftSubJnt',
            'BackRightSubJnt'
        ]):
            adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='{0}Bend'.format(sub_jnt_name)
            )
            bend_adls.append(adl)

            adl.plugs['output'].connect_to(
                joints[i + 2].plugs['translateY']
            )  # Find the sub joints by adding index

        for axis in 'XZ':
            bend_rotation_values = [(0, 0.0), (1, 1.0)]
            remap_bend_rotation_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                bend_multiplier_plug
            ).remap(
                *bend_rotation_values
            )
            remap_bend_rotation_node = remap_bend_rotation_plug.get_node()
            remap_bend_rotation_node.plugs['inputMin'].set_value(-size * 8.0)
            remap_bend_rotation_node.plugs['inputMax'].set_value(size * 8.0)

            bend_translation_values = [
                (0.0, 0.8),
                (0.25, 0.6),
                (0.5, 0.5),
                (0.75, 0.6),
                (1.0, 0.8)
            ]
            remap_bend_translation_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                bend_multiplier_plug
            ).remap(
                *bend_translation_values
            )
            remap_bend_translation_node = remap_bend_translation_plug.get_node()
            remap_bend_translation_node.plugs['inputMin'].set_value(-size * 8.0)
            remap_bend_translation_node.plugs['inputMax'].set_value(size * 8.0)
            remap_bend_translation_node.plugs['outputMin'].set_value(-joint_distance / size)
            remap_bend_translation_node.plugs['outputMax'].set_value(joint_distance / size)

            if axis == 'X':
                remap_bend_rotation_node.plugs['outValue'].connect_to(
                    this.handles[3].ofs.plugs['rotateZ']
                )  # Middle fk handle
                remap_bend_rotation_node.plugs['outValue'].multiply(root_bend_multiplier_plug).connect_to(
                    this.handles[1].ofs.plugs['rotateZ']
                )  # Root fk handle
                remap_bend_translation_node.plugs['outValue'].connect_to(
                    squash_translate_total_pma.plugs['input1D'].element(2)
                )
            elif axis == 'Z':
                remap_bend_rotation_node.plugs['outValue'].connect_to(
                    this.handles[3].ofs.plugs['rotateX']
                )  # Middle fk handle
                remap_bend_rotation_node.plugs['outValue'].multiply(root_bend_multiplier_plug).connect_to(
                    this.handles[1].ofs.plugs['rotateX']
                )  # Root fk handle
                remap_bend_translation_node.plugs['outValue'].connect_to(
                    squash_translate_total_pma.plugs['input1D'].element(3)
                )

            if axis == 'X':
                remap_bend_rotation_node.plugs['outputMin'].set_value(90)
                remap_bend_rotation_node.plugs['outputMax'].set_value(-90)

                positive_remap_bend_sub_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                    bend_multiplier_plug
                ).remap(
                    *bend_rotation_values
                )
                positive_remap_bend_sub_node = positive_remap_bend_sub_plug.get_node()
                positive_remap_bend_sub_node.plugs['inputMin'].set_value(-size * 8.0)
                positive_remap_bend_sub_node.plugs['inputMax'].set_value(size * 8.0)
                positive_remap_bend_sub_node.plugs['outputMin'].set_value(-joint_distance / size * 2.0)
                positive_remap_bend_sub_node.plugs['outputMax'].set_value(joint_distance / size * 2.0)

                negative_remap_bend_sub_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                    bend_multiplier_plug
                ).remap(
                    *bend_rotation_values
                )
                negative_remap_bend_sub_node = negative_remap_bend_sub_plug.get_node()
                negative_remap_bend_sub_node.plugs['inputMin'].set_value(-size * 8.0)
                negative_remap_bend_sub_node.plugs['inputMax'].set_value(size * 8.0)
                negative_remap_bend_sub_node.plugs['outputMin'].set_value(joint_distance / size * 2.0)
                negative_remap_bend_sub_node.plugs['outputMax'].set_value(-joint_distance / size * 2.0)

                positive_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[0].plugs['input1'])  # Front Left
                positive_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[2].plugs['input1'])  # Back Left
                negative_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[1].plugs['input1'])  # Front Right
                negative_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[3].plugs['input1'])  # Back Right

                # Adding offset for when both squash and bend are activated
                remap_translate_offset_values = [(0, 0.0), (1, 1.0)]
                remap_translate_offset_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                    bend_multiplier_plug
                ).remap(
                    *remap_translate_offset_values
                )
                remap_translate_offset_node = remap_translate_offset_plug.get_node()
                remap_translate_offset_node.plugs['inputMin'].set_value(-joint_distance * 2.0)
                remap_translate_offset_node.plugs['inputMax'].set_value(joint_distance * 2.0)
                remap_translate_offset_node.plugs['outputMin'].set_value(-1.0)

                remap_translate_offset_mdl = this.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}BendOffsetTranslate'.format(axis)
                )
                main_handle.plugs['translateY'].connect_to(remap_translate_offset_mdl.plugs['input1'])
                remap_translate_offset_node.plugs['outValue'].connect_to(remap_translate_offset_mdl.plugs['input2'])

                remap_translate_half_mdl = this.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}BendOffsetTranslateHalf'.format(axis)
                )
                remap_translate_offset_mdl.plugs['output'].connect_to(remap_translate_half_mdl.plugs['input1'])
                remap_translate_half_mdl.plugs['input2'].set_value(0.5)

                remap_translate_half_mdl.plugs['output'].connect_to(
                    fk_handles[1].ofs.plugs['translate{0}'.format(axis)]
                )
                remap_translate_offset_mdl.plugs['output'].connect_to(
                    fk_handles[2].ofs.plugs['translate{0}'.format(axis)]
                )

            else:
                remap_bend_rotation_node.plugs['outputMin'].set_value(-90)
                remap_bend_rotation_node.plugs['outputMax'].set_value(90)

                negative_remap_bend_sub_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                    bend_multiplier_plug
                ).remap(
                    *bend_rotation_values
                )
                negative_remap_bend_sub_node = negative_remap_bend_sub_plug.get_node()
                negative_remap_bend_sub_node.plugs['inputMin'].set_value(-size * 8.0)
                negative_remap_bend_sub_node.plugs['inputMax'].set_value(size * 8.0)
                negative_remap_bend_sub_node.plugs['outputMin'].set_value(-joint_distance / size * 2.0)
                negative_remap_bend_sub_node.plugs['outputMax'].set_value(joint_distance / size * 2.0)

                positive_remap_bend_sub_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                    bend_multiplier_plug
                ).remap(
                    *bend_rotation_values
                )
                positive_remap_bend_sub_node = positive_remap_bend_sub_plug.get_node()
                positive_remap_bend_sub_node.plugs['inputMin'].set_value(-size * 8.0)
                positive_remap_bend_sub_node.plugs['inputMax'].set_value(size * 8.0)
                positive_remap_bend_sub_node.plugs['outputMin'].set_value(joint_distance / size * 2.0)
                positive_remap_bend_sub_node.plugs['outputMax'].set_value(-joint_distance / size * 2.0)

                negative_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[0].plugs['input2'])  # Front Left
                negative_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[1].plugs['input2'])  # Front Right
                positive_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[2].plugs['input2'])  # Back Left
                positive_remap_bend_sub_node.plugs['outValue'].connect_to(bend_adls[3].plugs['input2'])  # Back Right

                # Adding offset for when both squash and bend are activated
                remap_translate_offset_values = [(0, 0.0), (1, 1.0)]
                remap_translate_offset_plug = main_handle.plugs['translate{0}'.format(axis)].multiply(
                    bend_multiplier_plug
                ).remap(
                    *remap_translate_offset_values
                )
                remap_translate_offset_node = remap_translate_offset_plug.get_node()
                remap_translate_offset_node.plugs['inputMin'].set_value(joint_distance * 2.0)
                remap_translate_offset_node.plugs['inputMax'].set_value(-joint_distance * 2.0)
                remap_translate_offset_node.plugs['outputMin'].set_value(-1.0)

                remap_translate_offset_mdl = this.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}BendOffsetTranslate'.format(axis)
                )
                main_handle.plugs['translateY'].multiply(-1.0).connect_to(remap_translate_offset_mdl.plugs['input1'])
                remap_translate_offset_node.plugs['outValue'].connect_to(remap_translate_offset_mdl.plugs['input2'])

                remap_translate_half_mdl = this.create_child(
                    DependNode,
                    node_type='multDoubleLinear',
                    segment_name='{0}BendOffsetTranslateHalf'.format(axis)
                )
                remap_translate_offset_mdl.plugs['output'].connect_to(remap_translate_half_mdl.plugs['input1'])
                remap_translate_half_mdl.plugs['input2'].set_value(0.5)

                remap_translate_half_mdl.plugs['output'].connect_to(
                    fk_handles[1].ofs.plugs['translate{0}'.format(axis)]
                )
                remap_translate_offset_mdl.plugs['output'].connect_to(
                    fk_handles[2].ofs.plugs['translate{0}'.format(axis)]
                )

        squash_translate_total_pma.plugs['output1D'].connect_to(
            fk_handles[1].ofs.plugs['translateY'])
        squash_translate_total_pma.plugs['output1D'].connect_to(
            fk_handles[2].ofs.plugs['translateY'])

        skincluster = this.controller.scene.skinCluster(
            joints,
            this.deformer.lattice_shape,
            tsb=True
        )[0]

        # Set weights on lattice
        bottom_pts = '[0:1][0][0:1]'
        front_left_mid_pts = '[1][1][1]'
        front_right_mid_pts = '[0][1][1]'
        back_left_mid_pts = '[1][1][0]'
        back_right_mid_pts = '[0][1][0]'
        top_pts = '[0:1][2][0:1]'
        lattices_pts = [
            bottom_pts,
            front_left_mid_pts,
            front_right_mid_pts,
            back_left_mid_pts,
            back_right_mid_pts,
            top_pts
        ]

        bind_joints = joints
        bind_joints.pop(1)  # Pop main middle joint

        for lattice_pt, bind_jnt in zip(lattices_pts, bind_joints):
            this.controller.scene.skinPercent(
                skincluster,
                '{0}.pt{1}'.format(this.deformer.lattice_transform, lattice_pt),
                transformValue=[bind_jnt, 1.0]
            )

        this.deformer.lattice_transform.set_matrix(this.deformer.get_matrix())

        color = env.colors['newlatticeSquish']
        this.plugs['overrideRGBColors'].set_value(True)
        this.plugs['overrideColorR'].set_value(color[0])
        this.plugs['overrideColorG'].set_value(color[1])
        this.plugs['overrideColorB'].set_value(color[2])

        return this

    def post_create(self, **kwargs):
        ldu.process_legacy_lattice_squish_rig_data(self, kwargs)  # handle legacy part data: Delete when possible
        super(NewLatticeSquish, self).post_create(**kwargs)

    def finalize(self):
        super(NewLatticeSquish, self).finalize()

    def create_split_deformers(self):
        members = self.get_members()
        s_divisions = self.deformer.lattice_shape.plugs['sDivisions'].get_value()
        t_divisions = self.deformer.lattice_shape.plugs['tDivisions'].get_value()
        u_divisions = self.deformer.lattice_shape.plugs['uDivisions'].get_value()
        if self.split_deformers and members:
            for i, geometry_name in enumerate(members.keys()):
                logging.getLogger('rig_build').info('Removing %s from %s' % (geometry_name, self.deformer.ffd.name))
                segment_name = 'Volume%s' % rig_factory.index_dictionary[i].upper()
                lattice = self.create_child(
                    Lattice,
                    legacy_segment_names=False,
                    segment_name=segment_name,
                    s_divisions=s_divisions,
                    t_divisions=t_divisions,
                    u_divisions=u_divisions
                )
                # Copy attrs, or link from source if driven by the rig
                # (avoiding making the old lattice show in the inputs of the member)
                dup_attrs = [
                    (self.deformer.ffd, lattice.ffd, [
                        'local',
                        'localInfluenceS',
                        'localInfluenceT',
                        'localInfluenceU',
                        'outsideLattice',
                        'outsideFalloffDist',
                        'usePartialResolution',
                        'partialResolution',
                        'freezeGeometry',
                        'envelope'
                    ]
                     ),
                    (self.deformer, lattice, [
                        'translate',
                        'rotate',
                        'scale',
                        'inheritsTransform'
                    ]
                     ),
                    (self.deformer.lattice_transform, lattice.lattice_transform, [
                        'translate',
                        'rotate',
                        'scale',
                        'inheritsTransform'
                    ]
                     ),
                    (self.deformer.lattice_base_transform, lattice.lattice_base_transform, [
                        'translate',
                        'rotate',
                        'scale',
                        'inheritsTransform'
                    ]
                     )
                ]
                for src_obj, dst_obj, attrs in dup_attrs:
                    for attr in attrs:
                        src_plug = src_obj.plugs[attr]
                        dst_plug = dst_obj.plugs[attr]
                        in_cons = self.controller.scene.listConnections(src_plug.name, p=1, s=True, d=False)
                        if in_cons:
                            self.controller.scene.connectAttr(in_cons[0], dst_plug.name)
                        else:
                            dst_plug.set_value(src_plug.get_value())

                self.deformer.lattice_shape.plugs['latticeOutput'].connect_to(
                    lattice.lattice_shape.plugs['latticeInput']
                )

                logging.getLogger('rig_build').info('Adding %s to %s' % (geometry_name, lattice.ffd.name))
                lattice.ffd.set_members({geometry_name: members[geometry_name]})
                lattice.set_mesh_weights(geometry_name, self.deformer.get_mesh_weights(geometry_name))
                lattice.plugs['visibility'].set_value(False)
                try:
                    self.controller.scene.reorderDeformers(
                        self.deformer.ffd.name,
                        lattice.ffd.name,
                        geometry_name
                    )
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
            self.deformer.remove_geometry(members.keys())

