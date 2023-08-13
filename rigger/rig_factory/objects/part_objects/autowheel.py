from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_math.matrix import Matrix


class AutowheelGuide(PartGuide):
    """ A class for creating the auto wheel guides in guide state """
    default_settings = dict(
        root_name='Autowheel',
        size=5.0,
        wheel_amount=2,
        shape='cube',
        create_gimbal=False
    )
    shape = DataProperty( name='shape' )
    create_gimbal = DataProperty( name='create_gimbal' )
    wheel_handles = ObjectListProperty( name='wheel_handles' )
    placement_offsets = DataProperty( name='placement_offsets', default_value=[0.0, 0.0] )

    def __init__(self, **kwargs):
        super(AutowheelGuide, self).__init__(**kwargs)
        self.toggle_class = Autowheel.__name__

    @classmethod
    def create(cls, **kwargs):
        handle_positions = kwargs.get('handle_positions', dict())
        kwargs.setdefault('side', 'center')
        this = super(AutowheelGuide, cls).create(**kwargs)
        controller = this.controller
        side = this.side
        size = this.size
        wheel_amount = kwargs.get('wheel_amount', cls.default_settings['wheel_amount'])

        if wheel_amount == 1:
            pass

        elif wheel_amount == 2:
            pass

        else:
            print ("uh oh spaghettios you messed up it only takes 1 or 2 babyyyy")

        # Create nodes
        # Create wheels

        wheel_left_jnt = this.create_child(
            Joint,
            side='left'
        )

        wheel_right_jnt = this.create_child(
            Joint,
            side='right'
        )

        wheel_left_spin_jnt = wheel_left_jnt.create_child(
            Joint,
            segment_name='Spin',
            side='left'
        )

        wheel_right_spin_jnt = wheel_right_jnt.create_child(
            Joint,
            segment_name='Spin',
            side='right'
        )

        settings_jnt = this.create_child(
            Joint,
            segment_name='Settings',
            side='center'
        )

        wheel_left_guide = this.create_handle(
            segment_name='Wheel',
            side='left'
        )
        wheel_left_guide.create_plug(
            'placement_offset',
            at='float',
            keyable=True,
            dv=this.placement_offsets[0]
        )
        this.wheel_handles.append(wheel_left_guide)

        wheel_right_guide = this.create_handle(
            segment_name='Wheel',
            side='right'
        )
        wheel_right_guide.create_plug(
            'placement_offset',
            at='float',
            keyable=True,
            dv=this.placement_offsets[1]
        )
        this.wheel_handles.append(wheel_right_guide)

        settings_guide = this.create_handle(
            segment_name='Settings',
            side='center'
        )

        wheel_left_pos = handle_positions.get(wheel_left_guide.name, [20.0, 0.0, 0.0])
        wheel_left_guide.plugs['translate'].set_value(wheel_left_pos)

        wheel_right_pos = handle_positions.get(wheel_right_guide.name, [-20.0, 0.0, 0.0])
        wheel_right_guide.plugs['translate'].set_value(wheel_right_pos)

        settings_pos = handle_positions.get(settings_guide.name, [0.0, 0.0, 10.0])
        settings_guide.plugs['translate'].set_value(settings_pos)

        # create everything else

        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
        )

        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='ItemSize'
        )

        # Constraints

        controller.create_point_constraint(
            wheel_left_guide,
            wheel_left_jnt
        )

        controller.create_point_constraint(
            wheel_right_guide,
            wheel_right_jnt
        )

        controller.create_point_constraint(
            settings_guide,
            settings_jnt
        )

        # Attributes

        size_plug = this.plugs['size']
        size_plug.connect_to(multiply.plugs['input1X'])
        multiply.plugs['input2X'].set_value(1)

        multiply.plugs['outputX'].connect_to(wheel_left_guide.plugs['size'])
        multiply.plugs['outputX'].connect_to(wheel_right_guide.plugs['size'])
        multiply.plugs['outputX'].connect_to(settings_guide.plugs['size'])

        for joint in [wheel_left_jnt, wheel_right_jnt, settings_jnt]:
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                radius=size * 1.5
            )

        wheel_left_guide.plugs['radius'].set_value(size * 0.5)
        wheel_right_guide.plugs['radius'].set_value(size * 0.5)
        settings_guide.plugs['radius'].set_value(size * 0.5)

        # Shaders
        root = this.get_root()
        wheel_left_guide.mesh.assign_shading_group(root.shaders['left'].shading_group)
        wheel_right_guide.mesh.assign_shading_group(root.shaders['right'].shading_group)
        settings_guide.mesh.assign_shading_group(root.shaders['center'].shading_group)

        root = this.get_root()
        if root:
            root.add_plugs(
                [
                    wheel_left_guide.plugs['tx'],
                    wheel_left_guide.plugs['ty'],
                    wheel_left_guide.plugs['tz'],
                    wheel_right_guide.plugs['tx'],
                    wheel_right_guide.plugs['ty'],
                    wheel_right_guide.plugs['tz'],
                    settings_guide.plugs['tx'],
                    settings_guide.plugs['ty'],
                    settings_guide.plugs['tz']
                ]
            )
        this.base_handles = [wheel_left_guide,
                             wheel_right_guide,
                             settings_guide
                             ]
        this.joints = [wheel_left_jnt,
                       wheel_right_jnt,
                       wheel_left_spin_jnt,
                       wheel_right_spin_jnt,
                       settings_jnt,
                       ]
        return this

    def get_toggle_blueprint(self):
        blueprint = super(AutowheelGuide, self).get_toggle_blueprint()
        self.placement_offsets = [x.plugs['placement_offset'].get_value() for x in self.wheel_handles]
        blueprint['placement_offsets'] = self.placement_offsets

        return blueprint


class Autowheel(Part):
    """ A class for creating the autowheel part """
    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    shape = DataProperty(
        name='shape'
    )

    create_gimbal = DataProperty(
        name='create_gimbal'
    )

    wheel_handles = ObjectListProperty(
        name='wheel_handles'
    )

    placement_offsets = DataProperty(
        name='placement_offsets',
        default_value=[0.0, 0.0]
    )

    left_wheel_placement_node = ObjectProperty(
        name='left_wheel_placement_node'
    )

    right_wheel_placement_node = ObjectProperty(
        name='right_wheel_placement_node'
    )

    def __init__(self, **kwargs):
        super(Autowheel, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(Autowheel, cls).create(**kwargs)
        controller = this.controller
        size = this.size
        matrices = this.matrices

        top_transform = this.create_child(
            Transform,
            side='center',
            segment_name='Master'
        )
        this.plugs.set_values(
            overrideEnabled=False
        )

        wheel_left_spin_handle_jnt = this.create_child(
            Joint,
            segment_name='Spin',
            index=0,
            side='left',
            matrix=matrices[0],
            parent=this.joint_group
        )

        wheel_left_handle = this.create_handle(
            handle_type=GroupedHandle,
            shape='cube',
            side='left',
            size=size,
            matrix=matrices[0],
            create_gimbal=this.create_gimbal,
            parent=top_transform
        )
        wheel_left_spin_handle_jnt.zero_rotation()
        wheel_left_spin_handle_jnt.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )

        wheel_left_handle_jnt = this.create_child(
            Joint,
            index=0,
            side='left',
            matrix=matrices[0],
            parent=this.joint_group
        )
        if wheel_left_handle.gimbal_handle:
            parent_node = wheel_left_handle.gimbal_handle
        else:
            parent_node = wheel_left_handle

        wheel_left_spin_handle = this.create_handle(
            handle_type=GroupedHandle,
            shape='circle_c',
            side='left',
            segment_name='Spin',
            size=size,
            matrix=matrices[0],
            create_gimbal=this.create_gimbal,
            parent=parent_node
        )

        wheel_left_handle_jnt.zero_rotation()
        wheel_left_handle_jnt.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=1,
            overrideColorRGB=env.colors['left']
        )
        if wheel_left_spin_handle.gimbal_handle:
            wheel_left_loc = wheel_left_spin_handle.gimbal_handle.create_child(
                Transform,
                suffix='Loc',
                side='left',
                matrix=matrices[0],
            )
        else:
            wheel_left_loc = wheel_left_spin_handle.create_child(
                Transform,
                suffix='Loc',
                side='left',
                matrix=matrices[0],
            )

        wheel_left_loc_shape = wheel_left_loc.create_child(
            Locator,
            suffix='Shape'
        )

        left_wheel_offset = list(matrices[0].get_translation())
        left_wheel_radius = abs(left_wheel_offset[1])

        left_wheel_offset[0] += left_wheel_offset[1] * 0.25
        left_wheel_offset[1] = -1
        left_wheel_placement_matrix = Matrix(left_wheel_offset)

        left_wheel_placeoff = wheel_left_handle_jnt.create_child(
            Transform,
            segment_name='LeftWheelPlacement_Offset',
            matrix=left_wheel_placement_matrix
        )

        left_wheel_placement = left_wheel_placeoff.create_child(
            Transform,
            segment_name='LeftWheelPlacement',
        )

        left_wheel_placement_mesh = left_wheel_placement.create_child(
            DagNode,
            node_type='mesh',
            segment_name='LeftWheelPlacement'
        )
        left_wheel_placement_mesh.plugs['hideOnPlayback'].set_value(True)

        left_wheel_offset_plug = wheel_left_handle.create_plug(
            'placement_offset',
            at='float',
            keyable=True,
            dv=this.placement_offsets[0]
        )
        left_wheel_offset_plug.connect_to(
            left_wheel_placement.plugs['tx']
        )
        this.wheel_handles.append(wheel_left_handle)

        left_wheel_placement_poly_cube = this.create_child(
            DependNode,
            node_type='polyCube',
            segment_name='LeftWheelPlacement'
        )
        left_wheel_placement_poly_cube.plugs['output'].connect_to(
            left_wheel_placement_mesh.plugs['inMesh'],
        )

        left_wheel_placement_poly_cube.plugs.set_values(
            width=left_wheel_radius * 0.75,
            height=2,
            depth=left_wheel_radius * 2,
        )

        left_wheel_placement.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )

        wheel_left_handle.zro.plugs['visibility'].connect_to(left_wheel_placeoff.plugs['visibility'])

        this.left_wheel_placement_node = left_wheel_placement

        #########################################################################################

        wheel_right_spin_handle_jnt = this.create_child(
            Joint,
            segment_name='Spin',
            index=0,
            side='right',
            matrix=matrices[1],
            parent=this.joint_group
        )
        wheel_right_handle = this.create_handle(
            handle_type=GroupedHandle,
            shape='cube',
            side='right',
            size=size,
            matrix=matrices[1],
            create_gimbal=this.create_gimbal,
            parent=top_transform
        )
        wheel_right_spin_handle_jnt.zero_rotation()
        wheel_right_spin_handle_jnt.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )

        wheel_right_handle_jnt = this.create_child(
            Joint,
            index=0,
            side='right',
            matrix=matrices[1],
            parent=this.joint_group
        )
        if wheel_right_handle.gimbal_handle:
            parent_node = wheel_right_handle.gimbal_handle
        else:
            parent_node = wheel_right_handle

        wheel_right_spin_handle = this.create_handle(
            handle_type=GroupedHandle,
            shape='circle_c',
            side='right',
            segment_name='Spin',
            size=size,
            matrix=matrices[1],
            create_gimbal=this.create_gimbal,
            parent=parent_node
        )

        wheel_right_handle_jnt.zero_rotation()
        wheel_right_handle_jnt.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=1,
            overrideColorRGB=env.colors['right']
        )
        if wheel_right_spin_handle.gimbal_handle:
            wheel_right_loc = wheel_right_spin_handle.gimbal_handle.create_child(
                Transform,
                suffix='Loc',
                side='right',
                matrix=matrices[1],
            )
        else:
            wheel_right_loc = wheel_right_spin_handle.create_child(
                Transform,
                suffix='Loc',
                side='right',
                matrix=matrices[1],
            )

        wheel_right_loc_shape = wheel_right_loc.create_child(
            Locator,
            suffix='Shape'
        )

        right_wheel_offset = list(matrices[1].get_translation())
        right_wheel_radius = abs(right_wheel_offset[1])

        right_wheel_offset[0] -= right_wheel_offset[1] * 0.25
        right_wheel_offset[1] = -0.5
        right_wheel_placement_matrix = Matrix(right_wheel_offset)

        right_wheel_placeoff = wheel_right_handle_jnt.create_child(
            Transform,
            segment_name='RightWheelPlacement_Offset',
            matrix=right_wheel_placement_matrix
        )
        right_wheel_placeoff.plugs.set_values(
            scaleX=-1
        )

        right_wheel_placement = right_wheel_placeoff.create_child(
            Transform,
            segment_name='RightWheelPlacement'
        )

        right_wheel_placement_mesh = right_wheel_placement.create_child(
            DagNode,
            node_type='mesh',
            segment_name='RightWheelPlacement'
        )
        right_wheel_placement_mesh.plugs['hideOnPlayback'].set_value(True)

        right_wheel_offset_plug = wheel_right_handle.create_plug(
            'placement_offset',
            at='float',
            keyable=True,
            dv=this.placement_offsets[1]
        )
        right_wheel_offset_plug.connect_to(
            right_wheel_placement.plugs['tx']
        )
        this.wheel_handles.append(wheel_right_handle)

        right_wheel_placement_poly_cube = this.create_child(
            DependNode,
            node_type='polyCube',
            segment_name='RightWheelPlacement'
        )
        right_wheel_placement_poly_cube.plugs['output'].connect_to(
            right_wheel_placement_mesh.plugs['inMesh'],
        )
        right_wheel_placement_poly_cube.plugs.set_values(
            width=right_wheel_radius * 0.75,
            height=2,
            depth=right_wheel_radius * 2,
        )

        right_wheel_placement.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )

        wheel_right_handle.zro.plugs['visibility'].connect_to(right_wheel_placeoff.plugs['visibility'])

        this.right_wheel_placement_node = right_wheel_placement

        #########################################################################################

        axle_name = ["One", "One_Facing", "Two", "Displace_Aim", "Orient_Parent", "Orient_Up"]
        axle_parts = []
        average_axle_pos = (wheel_left_spin_handle_jnt.get_translation() + wheel_right_spin_handle_jnt.get_translation()) / 2

        for each in axle_name:
            axle_pieces = this.create_child(
                Transform,
                segment_name=each,
                suffix='Loc',
                side='center',
                matrix=average_axle_pos,
                parent=this.utility_group
            )

            axle_pieces.create_child(
                Locator,
                suffix='Shape'

            )
            axle_parts.append(axle_pieces)

        displace_loc = this.create_child(
            Transform,
            segment_name='Displace',
            suffix='Loc',
            side='center',
            matrix=average_axle_pos,
            parent=axle_parts[3]
        )

        displace_loc.create_child(
            Locator,
            suffix='Shape'

        )

        orient_loc = this.create_child(
            Transform,
            segment_name='Orient',
            suffix='Loc',
            side='center',
            matrix=average_axle_pos,
            parent=axle_parts[4]
        )

        orient_loc.create_child(
            Locator,
            suffix='Shape'

        )

        axle_part_1_value = axle_parts[5].plugs['ty'].get_value()
        axle_part_2_value = axle_parts[1].plugs['tz'].get_value()

        axle_parts[5].plugs['ty'].set_value(axle_part_1_value + 10.0)
        axle_parts[1].plugs['tz'].set_value(axle_part_2_value + 1.0)
        #########################################################################################

        wheel_turn_handle = this.create_handle(
            handle_type=GroupedHandle,
            shape='circle_line',
            side='center',
            segment_name='Wheel_Turn',
            size=size * 3,
            matrix=average_axle_pos,
            parent=top_transform
        )

        #########################################################################################

        settings_handle = this.create_handle(
            shape='gear_simple',
            segment_name='Settings',
            matrix=matrices[4]
        )

        settings_handle_joint = this.create_child(
            Joint,
            index=0,
            side='center',
            matrix=matrices[4],
            parent=this.joint_group
        )

        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )

        auto_plug = settings_handle.create_plug(
            'AutoWheel',
            at='double',
            keyable=True,
            min=0,
            max=1,
            dv=0
        )

        spin_plug = settings_handle.create_plug(
            'SpinAllWheels',
            at='double',
            keyable=True,
            dv=0
        )

        #########################################################################################
        # create nodes

        axle_reverse_md = this.create_child(
            DependNode,
            segment_name='Axle_Rev',
            node_type='multiplyDivide',
        )
        axle_reverse_cnd = this.create_child(
            DependNode,
            segment_name='Axle_Rev',
            node_type='condition',
            suffix='Cnd'
        )

        linear_rotate = this.create_child(
            DependNode,
            segment_name='Linear_Rotate',
            node_type='multiplyDivide',
        )

        spin_wheels = this.create_child(
            DependNode,
            segment_name='Spin_All',
            node_type='multiplyDivide',
        )

        ###############################################
        # create left side nodes
        axle_rotate_left_01 = this.create_child(
            DependNode,
            segment_name='Axle_Rotation_01',
            side='left',
            node_type='multiplyDivide'
        )

        axle_rotate_left_02 = this.create_child(
            DependNode,
            segment_name='Axle_Rotation_02',
            side='left',
            node_type='multiplyDivide'
        )

        axle_rotate_left_rev = this.create_child(
            DependNode,
            segment_name='Axle_Rotation_Rev_01',
            side='left',
            node_type='multiplyDivide'
        )

        axle_total_left_rotate = this.create_child(
            DependNode,
            segment_name='Total_Rotate',
            side='left',
            node_type='plusMinusAverage'
        )

        axle_left_switch = this.create_child(
            DependNode,
            segment_name='Switch',
            side='left',
            node_type='multiplyDivide'
        )

        axle_left_conversion = this.create_child(
            DependNode,
            segment_name='Axle_Conversion',
            side='left',
            node_type='unitConversion'
        )

        orient_left_conversion = this.create_child(
            DependNode,
            segment_name='Ori_Conversion',
            side='left',
            node_type='unitConversion'
        )

        ###############################################
        # create right side nodes
        axle_rotate_right_01 = this.create_child(
            DependNode,
            segment_name='Axle_Rotation_01',
            side='right',
            node_type='multiplyDivide'
        )

        axle_rotate_right_02 = this.create_child(
            DependNode,
            segment_name='Axle_Rotation_02',
            side='right',
            node_type='multiplyDivide'
        )

        axle_total_right_rotate = this.create_child(
            DependNode,
            segment_name='Total_Rotate',
            side='right',
            node_type='plusMinusAverage'
        )

        axle_right_switch = this.create_child(
            DependNode,
            segment_name='Switch',
            side='right',
            node_type='multiplyDivide'
        )

        axle_right_conversion = this.create_child(
            DependNode,
            segment_name='Axle_Conversion',
            side='right',
            node_type='unitConversion'
        )

        orient_right_conversion = this.create_child(
            DependNode,
            segment_name='Ori_Conversion',
            side='right',
            node_type='unitConversion'
        )

        #########################################################################################
        # create expression
        expression_node = this.create_child(
            DependNode,
            segment_name='AutoWheel',
            node_type='expression',
            suffix='Exp'
        )

        lines = []
        lines.append(
            '''if (%s.AutoWheel>0)
            {
                //front wheel distance measure placement
                if(dot(unit($v2),unit($v1))<0.999)
                {
                    float $directionFr=-1;
                       float $magnitudeFr=mag($p1-$p2);
                    if(dot(unit($v2),unit($v1))<0)
                    {
                        $directionFr=1;
                    }
                    vector $newPositionFr=unit($v1)*$magnitudeFr*$directionFr;
                    %s.translateX =($newPositionFr.x+$p1.x);
                    %s.translateY =($newPositionFr.y+$p1.y);
                    %s.translateZ =($newPositionFr.z+$p1.z);
                }

            }''' % (settings_handle, axle_parts[2], axle_parts[2], axle_parts[2])
        )

        lines.append('''
            else
            {
                %s.translateX=%s.translateX;
                %s.translateY=%s.translateY;
                %s.translateZ=%s.translateZ;

            }''' % (axle_parts[2], axle_parts[0], axle_parts[2],
                    axle_parts[0], axle_parts[2], axle_parts[0])
                     )

        expression_line = ' '.join(lines)

        expression_code = ("""//front wheel variables
        float $loc1x={0}.translateX;
        float $loc1y={0}.translateY;
        float $loc1z={0}.translateZ;

        float $loc2x={2}.translateX;
        float $loc2y={2}.translateY;
        float $loc2z={2}.translateZ;

        float $loc1Facingx={1}.translateX;
        float $loc1Facingy={1}.translateY;
        float $loc1Facingz={1}.translateZ;

        vector $p1=<<$loc1x, $loc1y, $loc1z>>;
        vector $p2=<<$loc2x, $loc2y, $loc2z>>;
        vector $v1=<<$loc1Facingx-$loc1x, $loc1Facingy-$loc1y, $loc1Facingz-$loc1z>>;
        vector $v2=$p1-$p2;

        {4}

        {3}.firstTerm=dot($v2, $v1);

        """.format(axle_parts[0], axle_parts[1], axle_parts[2], axle_reverse_cnd, expression_line)

                           )

        expression_node.plugs['expression'].set_value(expression_code)

        #########################################################################################
        # connect nodes

        axle_radius = wheel_left_spin_handle_jnt.plugs['tx'].get_value()
        axle_radius = axle_radius * 2

        settings_handle.plugs['SpinAllWheels'].connect_to(spin_wheels.plugs['input1X'])
        settings_handle_joint.plugs['visibility'].set_value(0)

        axle_reverse_md.plugs['input2Z'].set_value(-1)
        spin_wheels.plugs['input2X'].set_value(360)
        linear_rotate.plugs['operation'].set_value(2)
        linear_rotate.plugs['input2X'].set_value(axle_part_1_value)
        axle_reverse_md.plugs['outputZ'].connect_to(axle_reverse_cnd.plugs['colorIfTrueR'])
        axle_reverse_cnd.plugs['outColorR'].connect_to(linear_rotate.plugs['input1X'])
        axle_reverse_cnd.plugs['operation'].set_value(4)
        displace_loc.plugs['translateZ'].connect_to(axle_reverse_md.plugs['input1Z'])
        displace_loc.plugs['translateZ'].connect_to(axle_reverse_cnd.plugs['colorIfFalseR'])

        axle_rotate_left_01.plugs['outputY'].connect_to(axle_rotate_left_rev.plugs['input1Y'])
        axle_rotate_left_rev.plugs['input2Y'].set_value(-1)
        axle_rotate_left_rev.plugs['outputY'].connect_to(axle_rotate_left_02.plugs['input1Y'])
        axle_rotate_left_02.plugs['outputY'].connect_to(axle_total_left_rotate.plugs['input1D'].element(1))
        axle_rotate_left_02.plugs['input2Y'].set_value(axle_part_1_value)
        axle_rotate_left_02.plugs['operation'].set_value(2)
        axle_total_left_rotate.plugs['output1D'].connect_to(axle_left_switch.plugs['input1X'])
        axle_left_switch.plugs['outputX'].connect_to(axle_left_conversion.plugs['input'])
        axle_left_conversion.plugs['output'].connect_to(wheel_left_loc.plugs['rotateX'])
        orient_loc.plugs['rotateY'].connect_to(orient_left_conversion.plugs['input'])
        orient_left_conversion.plugs['output'].connect_to(axle_rotate_left_01.plugs['input1Y'])
        linear_rotate.plugs['outputX'].connect_to(axle_total_left_rotate.plugs['input1D'].element(0))
        axle_rotate_left_01.plugs['input2Y'].set_value(axle_radius)
        settings_handle.plugs['AutoWheel'].connect_to(axle_left_switch.plugs['input2X'])
        spin_wheels.plugs['outputX'].connect_to(wheel_left_spin_handle.ofs.plugs['rotateX'])
        wheel_turn_handle.plugs['rotateY'].connect_to(wheel_left_handle.drv.plugs['rotateY'])
        wheel_left_loc.plugs['visibility'].set_value(0)

        axle_rotate_right_01.plugs['outputY'].connect_to(axle_rotate_right_02.plugs['input1Y'])
        axle_rotate_right_02.plugs['outputY'].connect_to(axle_total_right_rotate.plugs['input1D'].element(1))
        axle_rotate_right_02.plugs['input2Y'].set_value(axle_part_1_value)
        axle_rotate_right_02.plugs['operation'].set_value(2)
        axle_total_right_rotate.plugs['output1D'].connect_to(axle_right_switch.plugs['input1X'])
        axle_right_switch.plugs['outputX'].connect_to(axle_right_conversion.plugs['input'])
        axle_right_conversion.plugs['output'].connect_to(wheel_right_loc.plugs['rotateX'])
        orient_loc.plugs['rotateY'].connect_to(orient_right_conversion.plugs['input'])
        orient_right_conversion.plugs['output'].connect_to(axle_rotate_right_01.plugs['input1Y'])
        linear_rotate.plugs['outputX'].connect_to(axle_total_right_rotate.plugs['input1D'].element(0))
        axle_rotate_right_01.plugs['input2Y'].set_value(axle_radius)
        axle_right_switch.plugs['outputX'].connect_to(axle_right_conversion.plugs['input'])
        axle_right_conversion.plugs['output'].connect_to(wheel_right_loc.plugs['rotateX'])
        settings_handle.plugs['AutoWheel'].connect_to(axle_right_switch.plugs['input2X'])
        spin_wheels.plugs['outputX'].connect_to(wheel_right_spin_handle.ofs.plugs['rotateX'])
        wheel_turn_handle.plugs['rotateY'].connect_to(wheel_right_handle.drv.plugs['rotateY'])
        wheel_right_loc.plugs['visibility'].set_value(0)

        #########################################################################################
        # create constraints

        controller.create_parent_constraint(
            top_transform,
            axle_parts[0],
            maintainOffset=True
        )

        controller.create_parent_constraint(
            top_transform,
            axle_parts[1],
            maintainOffset=True
        )

        controller.create_parent_constraint(
            top_transform,
            axle_parts[5],
            maintainOffset=True
        )

        controller.create_point_constraint(
            axle_parts[2],
            axle_parts[3],
            maintainOffset=True
        )

        controller.create_point_constraint(
            axle_parts[0],
            displace_loc,
            maintainOffset=True
        )

        controller.create_point_constraint(
            settings_handle,
            settings_handle_joint,
            maintainOffset=True
        )

        controller.create_point_constraint(
            axle_parts[0],
            axle_parts[4],
            maintainOffset=True
        )

        controller.create_aim_constraint(
            axle_parts[0],
            axle_parts[3],
            aimVector=(0, 0, 1),
            upVector=(0, 1, 0),
            maintainOffset=True
        )

        controller.create_aim_constraint(
            axle_parts[5],
            axle_parts[4],
            aimVector=(0, 1, 0),
            upVector=(0, 1, 0),
            maintainOffset=True
        )

        controller.create_aim_constraint(
            axle_parts[1],
            orient_loc,
            worldUpType=2,
            worldUpObject=axle_parts[1],
            aimVector=(0, 0, 1),
            upVector=(0, 1, 0),
            maintainOffset=True
        )

        controller.create_parent_constraint(
            wheel_left_handle,
            wheel_left_handle_jnt
        )
        controller.create_scale_constraint(
            wheel_left_handle,
            wheel_left_handle_jnt
        )
        controller.create_parent_constraint(
            wheel_right_handle,
            wheel_right_handle_jnt
        )
        controller.create_scale_constraint(
            wheel_right_handle,
            wheel_right_handle_jnt
        )

        controller.create_parent_constraint(
            wheel_left_loc,
            wheel_left_spin_handle_jnt
        )
        controller.create_scale_constraint(
            wheel_left_loc,
            wheel_left_spin_handle_jnt
        )
        controller.create_parent_constraint(
            wheel_right_loc,
            wheel_right_spin_handle_jnt
        )
        controller.create_scale_constraint(
            wheel_right_loc,
            wheel_right_spin_handle_jnt
        )

        controller.create_parent_constraint(
            settings_handle,
            top_transform,
            maintainOffset=True
        )

        controller.create_scale_constraint(
            settings_handle,
            top_transform,
            maintainOffset=True
        )

        #########################################################################################
        root = this.get_root()
        if root:
            root.add_plugs(
                [
                    wheel_left_handle.plugs['tx'],
                    wheel_left_handle.plugs['ty'],
                    wheel_left_handle.plugs['tz'],
                    wheel_left_handle.plugs['rx'],
                    wheel_left_handle.plugs['ry'],
                    wheel_left_handle.plugs['rz'],
                    wheel_left_handle.plugs['sx'],
                    wheel_left_handle.plugs['sy'],
                    wheel_left_handle.plugs['sz'],
                    wheel_left_spin_handle.plugs['rx'],
                    wheel_right_handle.plugs['tx'],
                    wheel_right_handle.plugs['ty'],
                    wheel_right_handle.plugs['tz'],
                    wheel_right_handle.plugs['rx'],
                    wheel_right_handle.plugs['ry'],
                    wheel_right_handle.plugs['rz'],
                    wheel_right_handle.plugs['sx'],
                    wheel_right_handle.plugs['sy'],
                    wheel_right_handle.plugs['sz'],
                    wheel_right_spin_handle.plugs['rx'],
                    wheel_turn_handle.plugs['ry'],
                    settings_handle.plugs['AutoWheel'],
                    settings_handle.plugs['SpinAllWheels']
                ]
            )
        this.joints = [wheel_left_handle_jnt,
                       wheel_right_handle_jnt,
                       wheel_left_spin_handle_jnt,
                       wheel_right_spin_handle_jnt,
                       settings_handle_joint
                       ]
        return this

    def get_toggle_blueprint(self):
        blueprint = self.guide_blueprint
        blueprint['placement_offsets'] = self.placement_offsets

        # get offsets attribute values
        offset_values = [x.plugs['placement_offset'].get_value() for x in self.wheel_handles]
        blueprint['placement_offsets'] = offset_values

        return blueprint
