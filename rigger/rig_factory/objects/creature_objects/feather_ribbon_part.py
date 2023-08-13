import Snowman3.rigger.rig_math.utilities as rmu
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.ribbon import Ribbon
from Snowman3.rigger.rig_factory.objects.deformer_objects.bend import Bend
from Snowman3.rigger.rig_factory.objects.deformer_objects.twist import Twist
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
import Snowman3.rigger.rig_factory.utilities.node_utilities.name_utilities as nmu
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.surface_point import SurfacePoint
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.deformer_parts.base_multi_deformer_part import BaseMultiDeformerPart


class FeatherRibbonPartGuide(ChainGuide):
    default_settings = dict(
        root_name='Feather',
        differentiation_name='Primary',
        size=1.0,
        side='center',
        ribbon_joint_count=10
    )
    create_gimbal = DataProperty( name='create_gimbal', default_value=False )
    ribbon_joint_count = DataProperty( name='ribbon_joint_count', default_value=10 )

    def __init__(self, **kwargs):
        super(FeatherRibbonPartGuide, self).__init__(**kwargs)
        self.toggle_class = FeatherRibbonPart.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 2
        this = super(FeatherRibbonPartGuide, cls).create(**kwargs)
        controller = this.controller
        # add ribbon joints
        ribbon_joints = []
        for i in range(this.ribbon_joint_count):
            # create joint
            ribbon_joint = this.create_child(
                Joint,
                parent=this,
                segment_name='{}_{}'.format(
                    this.differentiation_name,
                    'Ribbon_{}'.format(nmu.index_dictionary[i].upper()),
                ),
                differentiation_name=None
            )

            # place the joint between start and end
            wgt = 1.0 / (this.ribbon_joint_count - 1) * i
            controller.create_weight_constraint(
                this.joints[0],
                this.joints[1],
                ribbon_joint,
                type='pointConstraint',
                weights=[1.0 - wgt, wgt],
            )

            # make the joint un-selectable
            ribbon_joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )

            ribbon_joints.append(ribbon_joint)

        this.joints = [this.joints[0]] + ribbon_joints

        return this


class FeatherRibbonPart(BaseMultiDeformerPart):
    create_gimbal = DataProperty(
        name='create_gimbal',
        default_value=False
    )
    deform_slide_group = ObjectProperty(
        name='deform_slide_group'
    )

    ribbon_joint_count = DataProperty(
        name='ribbon_joint_count',
        default_value=10
    )

    ribbon = None

    def __init__(self, **kwargs):
        super(FeatherRibbonPart, self).__init__(**kwargs)
        self.data_getters['slide_value'] = self.get_slide_value
        self.data_setters['slide_value'] = self.set_slide_value

    def get_slide_value(self):
        return self.handles[0].plugs['Slide'].get_value()

    def set_slide_value(self, value):
        return self.handles[0].plugs['Slide'].set_value(value)

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(FeatherRibbonPart, cls).create(*args, **kwargs)
        joint_1 = this.create_child(
            Joint,
            segment_name='Base',
            matrix=this.matrices[0],
            parent=this.joint_group
        )

        joint_1.zero_rotation()

        handle = this.create_handle(
            segment_name='Settings',
            shape='marker',
            axis='z',
            matrix=this.matrices[0]
        )

        length = (this.matrices[0].get_translation() - this.matrices[-1].get_translation()).mag()
        handle.set_shape_matrix(Matrix([0.0, (length * -1.1) if this.side == 'right' else (length * 1.1), 0.0]))
        if this.side == 'right':
            handle.multiply_shape_matrix(Matrix(scale=[1.0, -1.0, 1.0]))
        this.controller.create_parent_constraint(handle, joint_1)

        # make ribbon joints
        ribbon_joints = []
        parent = joint_1
        for i in range(this.ribbon_joint_count):
            # create joint
            ribbon_joint = this.create_child(
                Joint,
                parent=parent,
                segment_name='{}_{}'.format(
                    this.differentiation_name,
                    'Ribbon_{}'.format(nmu.index_dictionary[i].upper()),
                ),
                differentiation_name=None,
            )
            ribbon_joints.append(ribbon_joint)
            parent = ribbon_joint

            # place the joint between start and end
            wgt = 1.0 / (this.ribbon_joint_count - 1) * i
            mtx = rmu.calculate_in_between_matrix(
                this.matrices[0],
                this.matrices[-1],
                weight=wgt
            )
            ribbon_joint.set_matrix(mtx)

        this.joints = [joint_1] + ribbon_joints
        ribbon_width = length / this.ribbon_joint_count * 0.5
        this.ribbon = this.create_child(
            Ribbon,
            [x.get_translation() for x in ribbon_joints],
            segment_name='Ribbon',
            vector=list(joint_1.get_matrix().x_vector() * ribbon_width),
            # vector=joint_1.get_matrix().x_vector(),
            extrude=True,
            degree=2,
            suffix='Srf',
        )

        this.ribbon.plugs['inheritsTransform'].set_value(False)
        this.ribbon.plugs['v'].set_value(0)

        # as surfaces are not rebuilt, their v parameter can be higher than one
        # in order to calculate the correct v value for follicle we need this
        surface_v_range = this.ribbon.nurbs_surface.plugs['minMaxRangeV'].get_value()[1]

        # attach ribbon joints to ribbon surface
        for i, ribbon_joint in enumerate(ribbon_joints):
            follicle = this.create_child(
                SurfacePoint,
                segment_name='{}_{}'.format(
                    this.differentiation_name,
                    'Follicle_{}'.format(nmu.index_dictionary[i].title())
                ),
                differentiation_name=None,
                surface=this.ribbon.nurbs_surface,
                use_plugin=False
            )

            # Turn off inheritsTransform for SurfacePoint, otherwise joints will double transform
            # This needs to inheritTransform untill we update to plugin follicle
            # follicle.plugs['inheritsTransform'].set_value(0.0)

            u, v = this.controller.scene.get_closest_surface_uv(
                this.ribbon.nurbs_surface.m_object,
                ribbon_joint.get_translation(),
            )
            follicle.follicle.plugs.set_values(
                parameterU=u,
                parameterV=v / surface_v_range,
            )
            this.controller.create_parent_constraint(
                follicle,
                ribbon_joint,
                mo=True,
            )

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
            dv=0.0
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
        super(FeatherRibbonPart, self).post_create(**kwargs)

        # deform ribbon surface using 2 bends + 1 twist + skincluser to base joint
        self.create_deformers([self.ribbon.nurbs_surface])
        self.controller.scene.skinCluster(
            self.ribbon.nurbs_surface,
            self.joints[0],
            bindMethod=0,
            tsb=True
        )

    def add_geometry(self, geometry):
        """ feather_ribbon doesn't support deformers on geos. they must get skinned to ribbon joints """
        return

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

        # keep the twist deformer and end of feather in sync
        # to avoid twisting only half of feather, when user slides the start of twist
        scale_pma = deform_slide_group.create_child(
            DependNode,
            node_type='plusMinusAverage',
            segment_name='SlideScale'
        )
        scale_pma.plugs['operation'].set_value(2)
        scale_pma.plugs['input1D'].child(0).set_value(1)
        self.handles[0].plugs['Slide'].connect_to(scale_pma.plugs['input1D'].child(1))
        scale_pma.plugs['output1D'].connect_to(twist.handle_transform.plugs['sy'])

        # position deformers
        position = [
            0.0,
            length * -0.25 if self.side == 'right' else length * 0.25,
            0.0
        ]
        scale = [
            length * 0.75,
            length * 0.75,
            length * 0.75
        ]
        bend_matrix = Matrix(position, scale=scale)
        twist_matrix = Matrix(position, scale=scale)
        bend_x.set_matrix(bend_matrix, world_space=False)
        bend_z.set_matrix(bend_matrix, world_space=False)
        twist.set_matrix(twist_matrix, world_space=False)

        # connect feather settings control to deformer attributes
        twist.handle_shape.plugs['handleWidth'].set_value(1.0)
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
            null_twist_multiply.plugs['input2X'].set_value(-1.0)
            null_twist_multiply.plugs['input2Y'].set_value(-1.0)
            r_bend_x_offset = null_twist_multiply.plugs['outputX']
            r_bend_z_offset = null_twist_multiply.plugs['outputY']
            r_bend_x_offset.connect_to(bend_x.settings_node.plugs['curvature'])
            r_bend_z_offset.connect_to(bend_z.settings_node.plugs['curvature'])
            bend_x.settings_node.plugs['highBound'].set_value(0.0)
            bend_z.settings_node.plugs['highBound'].set_value(0.0)
            twist.settings_node.plugs['highBound'].set_value(0.0)
            base_twist_offset.connect_to(twist.settings_node.plugs['endAngle'])
            twist_offset.connect_to(twist.settings_node.plugs['startAngle'])

        else:
            bend_x_offset.connect_to(bend_x.settings_node.plugs['curvature'])
            bend_z_offset.connect_to(bend_z.settings_node.plugs['curvature'])
            twist.settings_node.plugs['lowBound'].set_value(0.0)
            bend_x.settings_node.plugs['lowBound'].set_value(0.0)
            bend_z.settings_node.plugs['lowBound'].set_value(0.0)
            base_twist_offset.connect_to(twist.settings_node.plugs['startAngle'])
            twist_offset.connect_to(twist.settings_node.plugs['endAngle'])

        twist.plugs['v'].set_value(False)
        bend_x.plugs['v'].set_value(False)
        bend_z.plugs['v'].set_value(False)
        self.deformers = [twist, bend_x, bend_z]
        self.deformer_utility_nodes = [deform_slide_group]
