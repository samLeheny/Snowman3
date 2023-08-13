from Snowman3.rigger.rig_factory.objects.deformer_objects.bend import Bend
from Snowman3.rigger.rig_factory.objects.deformer_objects.twist import Twist
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.deformer_parts.base_multi_deformer_part import BaseMultiDeformerPart
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.utilities.legacy_data_utilities as ldu


class FeatherPartGuide(ChainGuide):
    default_settings = dict(
        root_name='Feather',
        differentiation_name='Primary',
        size=1.0,
        side='center',
    )

    create_gimbal = DataProperty(
        name='create_gimbal',
        default_value=False
    )

    def __init__(self, **kwargs):
        super(FeatherPartGuide, self).__init__(**kwargs)
        self.toggle_class = FeatherPart.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 2
        this = super(FeatherPartGuide, cls).create(**kwargs)
        return this


class FeatherPart(BaseMultiDeformerPart):
    create_gimbal = DataProperty(
        name='create_gimbal',
        default_value=False
    )
    deform_slide_group = ObjectProperty(
        name='deform_slide_group'
    )
    slide_value = DataProperty(
        name='slide_value',
        default_value=0.0
    )

    def __init__(self, **kwargs):
        super(FeatherPart, self).__init__(**kwargs)
        self.data_getters['slide_value'] = self.get_slide_value
        self.data_setters['slide_value'] = self.set_slide_value

    def get_slide_value(self):
        return self.handles[0].plugs['Slide'].get_value()

    def set_slide_value(self, value):
        return self.handles[0].plugs['Slide'].set_value(value)

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(FeatherPart, cls).create(*args, **kwargs)
        joint_1 = this.create_child(
            Joint,
            segment_name='Base',
            matrix=this.matrices[0],
            parent=this.joint_group
        )
        joint_2 = joint_1.create_child(
            Joint,
            segment_name='Tip',
            matrix=this.matrices[1]
        )

        joint_1.zero_rotation()
        joint_2.zero_rotation()

        handle = this.create_handle(
            segment_name='Settings',
            shape='marker',
            axis='z',
            matrix=this.matrices[0],
        )

        length = (joint_2.get_translation() - joint_1.get_translation()).mag()
        handle.set_shape_matrix(
            Matrix(
                translation=[
                    0.0,
                    (length * -1.1) if this.side == 'right' else (length * 1.1),
                    0.0
                ],
                scale=[
                    this.size * 0.5,
                    this.size * 0.5,
                    this.size * 0.5,
                ]
            )
        )
        if this.side == 'right':
            handle.multiply_shape_matrix(Matrix(scale=[1.0, -1.0, 1.0]))
        this.controller.create_parent_constraint(handle, joint_1)
        this.joints = [joint_1, joint_2]

        # create an empty transform at the tip of feather, as helper
        # it will be used to aim feathers to the feather beside them
        this.create_child(
            'Transform',
            segment_name='{}_Tip'.format(this.differentiation_name),
            differentiation_name=None,
            matrix=this.joints[-1].get_matrix(),
            suffix='Loc',
            parent=handle.groups[0],
        )

        # create attributes
        bend_x_plug = handle.create_plug(
            'BendX',
            at='double',
            keyable=True
        )
        bend_z_plug = handle.create_plug(
            'BendZ',
            at='double',
            keyable=True
        )
        twist_plug = handle.create_plug(
            'Twist',
            at='double',
            keyable=True
        )
        base_twist_plug = handle.create_plug(
            'BaseTwist',
            at='double',
            keyable=True
        )
        handle.create_plug(
            'BendXInput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'BendZInput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'TwistInput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'BendXOutput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'BendZOutput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'TwistOutput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'BaseTwistInput',
            at='double',
            keyable=False
        )
        handle.create_plug(
            'BaseTwistOutput',
            at='double',
            keyable=False
        )
        bend_x_add = this.create_child(
            DependNode,
            node_type='addDoubleLinear',
            segment_name='BendX'
        )
        bend_z_add = this.create_child(
            DependNode,
            node_type='addDoubleLinear',
            segment_name='BendZ'
        )
        twist_add = this.create_child(
            DependNode,
            node_type='addDoubleLinear',
            segment_name='Twist'
        )
        base_twist_add = this.create_child(
            DependNode,
            node_type='addDoubleLinear',
            segment_name='BaseTwist'
        )
        slide_plug = handle.create_plug(
            'Slide',
            at='double',
            keyable=True,
            min=-1.0,
            max=1.0,
            dv=this.slide_value
        )

        # Adding 3 extra attributes to the driver null: twist, bend x , bend z
        drv_null = handle.drv
        drv_bendx_plug = drv_null.create_plug(
            'BendX',
            at='double',
            keyable=True,
            dv=0
        )
        drv_bendz_plug = drv_null.create_plug(
            'BendZ',
            at='double',
            keyable=True,
            dv=0
        )
        drv_twist_plug = drv_null.create_plug(
            'Twist',
            at='double',
            keyable=True,
            dv=0
        )
        root = this.get_root()

        root.add_plugs(
            drv_bendx_plug,
            drv_bendz_plug,
            drv_twist_plug
        )
        handle.plugs['BendX'].connect_to(bend_x_add.plugs['input1'])
        handle.plugs['BendXInput'].connect_to(bend_x_add.plugs['input2'])
        bend_x_add.plugs['output'].connect_to(handle.plugs['BendXOutput'])

        handle.plugs['BendZ'].connect_to(bend_z_add.plugs['input1'])
        handle.plugs['BendZInput'].connect_to(bend_z_add.plugs['input2'])
        bend_z_add.plugs['output'].connect_to(handle.plugs['BendZOutput'])

        handle.plugs['Twist'].connect_to(twist_add.plugs['input1'])
        handle.plugs['TwistInput'].connect_to(twist_add.plugs['input2'])
        twist_add.plugs['output'].connect_to(handle.plugs['TwistOutput'])

        handle.plugs['BaseTwist'].connect_to(base_twist_add.plugs['input1'])
        handle.plugs['BaseTwistInput'].connect_to(base_twist_add.plugs['input2'])
        base_twist_add.plugs['output'].connect_to(handle.plugs['BaseTwistOutput'])

        root = this.get_root()

        root.add_plugs(
            slide_plug,
            bend_x_plug,
            bend_z_plug,
            twist_plug,
            base_twist_plug,
            handle.plugs['rx'],
            handle.plugs['ry'],
            handle.plugs['rz'],
        )
        return this

    def post_create(self, **kwargs):
        ldu.process_legacy_feather_rig_data(self, kwargs)  # Delete this when legacy data is gone
        super(FeatherPart, self).post_create(**kwargs)

    def add_geometry(self, geometry):
        super(FeatherPart, self).add_geometry(geometry)

        geometry = [
            geo for geo in geometry
            if geo in self.controller.named_objects
        ]

        for g in geometry:
            if not self.controller.scene.find_skin_cluster(g):
                self.controller.scene.skinCluster(
                    g,
                    self.joints[0],
                    bindMethod=0,
                    tsb=True
                )

    def create_deformers(self, geometries):

        deform_slide_parent = self.create_child(
            Transform,
            segment_name='DeformSlideParent',
            matrix=self.joints[0].get_matrix()
        )
        deform_slide_parent.plugs['inheritsTransform'].set_value(False)
        deform_slide_group = deform_slide_parent.create_child(
            Transform,
            segment_name='DeformSlide'
        )
        slide_divide = deform_slide_group.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='Slide'
        )
        length = (self.matrices[-1].get_translation() - self.matrices[0].get_translation()).mag()

        self.handles[0].plugs['Slide'].connect_to(slide_divide.plugs['input1X'])
        slide_divide.plugs['input2X'].set_value(length * -1.0 if self.side == 'right' else length)
        slide_divide.plugs['outputX'].connect_to(deform_slide_group.plugs['ty'])

        # create 2 bend and one twist deformers
        twist = deform_slide_group.create_child(
            Twist,
            geometry=geometries,
            segment_name='Twist'
        )
        bend_x = deform_slide_group.create_child(
            Bend,
            geometry=geometries,
            segment_name='BendX'
        )
        bend_z = deform_slide_group.create_child(
            Bend,
            geometry=geometries,
            segment_name='BendZ'
        )
        bend_position = [
            0.0,
            length * -0.25 if self.side == 'right' else length * 0.25,
            0.0
        ]
        twist_position = [
            0.0,
            length * -0.75 if self.side == 'right' else length * 0.75,
            0.0
        ]

        bend_scale = [length * 0.75, length * 0.75, length * 0.75]
        twist_scale = [length * 0.25, length * 0.25, length * 0.25]
        bend_matrix = Matrix(bend_position, scale=bend_scale)
        twist_matrix = Matrix(twist_position, scale=twist_scale)
        twist.handle_shape.plugs['handleWidth'].set_value(1.0)
        bend_x.set_matrix(bend_matrix, world_space=False)
        bend_z.set_matrix(bend_matrix, world_space=False)
        twist.set_matrix(twist_matrix, world_space=False)
        bend_z.plugs['ry'].set_value(90.0)
        if self.side == 'right':
            bend_twist_multiply = self.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='BendTwist'
            )
            self.handles[0].plugs['BendXOutput'].connect_to(bend_twist_multiply.plugs['input1X'])
            self.handles[0].plugs['BendZOutput'].connect_to(bend_twist_multiply.plugs['input1Y'])
            self.handles[0].plugs['TwistOutput'].connect_to(bend_twist_multiply.plugs['input1Z'])
            bend_twist_multiply.plugs['input2X'].set_value(-1.0)
            bend_twist_multiply.plugs['input2Y'].set_value(-1.0)
            bend_twist_multiply.plugs['input2Z'].set_value(1.0)

        # adding the bend offset nulls with the bends from the handle:
        drv_null = self.handles[0].drv
        bend_x_drv_plug = drv_null.plugs['BendX']
        bend_z_drv_plug = drv_null.plugs['BendZ']
        bend_x_offset = bend_x_drv_plug.add(self.handles[0].plugs['BendXOutput'])
        bend_z_offset = bend_z_drv_plug.add(self.handles[0].plugs['BendZOutput'])
        twist_offset = drv_null.plugs['Twist'].add(self.handles[0].plugs['TwistOutput'])
        base_twist_offset = drv_null.plugs['Twist'].add(self.handles[0].plugs['BaseTwistOutput'])

        if self.side == 'right':
            null_twist_multiply = self.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='BendTwistNull'
            )
            bend_x_offset.connect_to(null_twist_multiply.plugs['input1X'])
            bend_z_offset.connect_to(null_twist_multiply.plugs['input1Y'])
            twist_offset.connect_to(null_twist_multiply.plugs['input1Z'])
            null_twist_multiply.plugs['input2X'].set_value(-1.0)
            null_twist_multiply.plugs['input2Y'].set_value(-1.0)
            null_twist_multiply.plugs['input2Z'].set_value(1.0)
            r_bend_x_offset = null_twist_multiply.plugs['outputX']
            r_bend_z_offset = null_twist_multiply.plugs['outputY']
            r_twist_offset = null_twist_multiply.plugs['outputZ']
            r_bend_x_offset.connect_to(bend_x.settings_node.plugs['curvature'])
            r_bend_z_offset.connect_to(bend_z.settings_node.plugs['curvature'])
            bend_x.settings_node.plugs['highBound'].set_value(0.0)
            bend_z.settings_node.plugs['highBound'].set_value(0.0)
            r_twist_offset.connect_to(twist.settings_node.plugs['startAngle'])
            base_twist_offset.connect_to(twist.settings_node.plugs['endAngle'])

        else:
            bend_x_offset.connect_to(bend_x.settings_node.plugs['curvature'])
            bend_z_offset.connect_to(bend_z.settings_node.plugs['curvature'])
            bend_x.settings_node.plugs['lowBound'].set_value(0.0)
            bend_z.settings_node.plugs['lowBound'].set_value(0.0)
            base_twist_offset.connect_to(twist.settings_node.plugs['startAngle'])
            twist_offset.connect_to(twist.settings_node.plugs['endAngle'])

        twist.plugs['v'].set_value(False)
        bend_x.plugs['v'].set_value(False)
        bend_z.plugs['v'].set_value(False)
        self.deformers = [twist, bend_x, bend_z]
        self.deformer_utility_nodes = [deform_slide_group]

    def get_blueprint(self):
        blueprint = super(FeatherPart, self).get_blueprint()
        return blueprint
