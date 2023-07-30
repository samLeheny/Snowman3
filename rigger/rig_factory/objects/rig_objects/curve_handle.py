import copy

import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.node_objects.curve_construct import CurveConstruct
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty,\
    ObjectDictProperty
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.dictionaries.nurbsCurvePrefabs import ctrl_shapes as shape_data



'''handle_shapes_path = '{}/handle_shapes.json'.format( os.path.dirname(rig_factory.__file__.replace('\\', '/')) )
with open(handle_shapes_path, mode='r') as f:
    shape_data = json.loads(f.read())
z_shape_data = copy.deepcopy(shape_data)
x_shape_data = copy.deepcopy(shape_data)'''
z_shape_data = copy.deepcopy(shape_data)
x_shape_data = copy.deepcopy(shape_data)



for shape_name in shape_data:
    curves_data = shape_data[shape_name]
    for x in range(len(curves_data)):
        cv_data = curves_data[x]['cvs']
        for i in range(len(cv_data)):
            cvx, cvy, cvz = cv_data[i]
            z_shape_data[shape_name][x]['cvs'][i][0] = cvx
            z_shape_data[shape_name][x]['cvs'][i][1] = cvz
            z_shape_data[shape_name][x]['cvs'][i][2] = cvy
            x_shape_data[shape_name][x]['cvs'][i][0] = cvy
            x_shape_data[shape_name][x]['cvs'][i][1] = cvx
            x_shape_data[shape_name][x]['cvs'][i][2] = cvz


class CurveHandle(CurveConstruct):

    curves = ObjectListProperty( name='curves' )
    base_curves = ObjectListProperty( name='base_curves' )
    shape_matrix = DataProperty( name='shape_matrix' )
    shape = DataProperty( name='shape' )
    axis = DataProperty( name='axis', default_value='y' )
    mirror_plugs = DataProperty( name='mirror_plugs' )
    vertices = ObjectListProperty( name='vertices' )
    color = DataProperty( name='color', default_value=[] )
    default_color = DataProperty( name='default_color', default_value=[] )
    offset_Vec = DataProperty( name='offset_Vec', default_value=[] )
    scale_offset = DataProperty( name='scale_offset', default_value= 0 )
    maintain_offset = DataProperty( name='maintain_offset', default_value = [0] )
    owner = ObjectProperty( name='owner' )
    utility_nodes = ObjectDictProperty( name='utility_nodes' )
    line_width = DataProperty( name='line_width', default_value=-1 )
    handle_metadata = DataProperty( name='handle_metadata', default_value=dict() )
    default_limits = DataProperty( name='default_limits', default_value=dict() )
    cached_curve_visibility_connections = DataProperty( name='cached_curve_visibility_connections',
                                                        default_value=dict() )
    # Used mostly for control shapes that have multiple shape nodes...
    curve_segment_name = DataProperty( name='curve_segment_name' )

    suffix = 'Ctrl'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        shape = kwargs.setdefault('shape', None)
        if shape not in shape_data:
            raise Exception(f"Shape type '{shape}' not supported.")
        this.create_plug('shapeMatrix', at='matrix')
        this.shape = None
        this.set_shape(shape)
        this.plugs['overrideEnabled'].set_value(True)
        this.set_color(env.colors[this.side])
        return this


    def set_color(self, color):
        index_color = env.index_colors[self.side]
        self.plugs['overrideColor'].set_value(index_color)


    def snap_to_vertices(self, vertices, mo=False, differ_vec=None, scale=0):
        self.controller.snap_handle_to_vertices(self, vertices, mo=mo, differ_vec=differ_vec, scale=scale)


    def update_assign_vertices(self, handle):
        self.controller.update_assign_vertices(self, handle)


    def set_shape(self, new_shape, delete_current=True):
        if new_shape == self.shape:
            return None

        if self.curves or self.base_curves:
            if self.curves:
                self.controller.schedule_objects_for_deletion(self.curves)
            if self.base_curves:
                self.controller.schedule_objects_for_deletion(self.base_curves)
            self.controller.delete_scheduled_objects()

        curves = []
        base_curves = []
        if self.axis == 'x':
            curve_data = x_shape_data[new_shape]
        elif self.axis == 'z':
            curve_data = z_shape_data[new_shape]
        else:
            curve_data = shape_data[new_shape]
        size = self.size

        for i, curve_data in enumerate(curve_data):
            curve_segment_name = rig_factory.index_dictionary[i].title()
            if self.subsidiary_name:
                base_subsidiary_name = f'{self.subsidiary_name}Base'
            else:
                base_subsidiary_name = 'Base'
            base_curve = self.create_child(
                NurbsCurve,
                subsidiary_name=base_subsidiary_name,
                curve_segment_name=curve_segment_name,
                degree=curve_data['degree'],
                positions=curve_data['cvs']
            )

            curve = self.create_child(
                NurbsCurve,
                curve_segment_name=curve_segment_name
            )
            curve.plugs['isHistoricallyInteresting'].set_value(False)

            transform_geometry = curve.create_child(
                DependNode,
                curve_segment_name=curve_segment_name,
                node_type='transformGeometry'
            )
            transform_geometry.plugs['isHistoricallyInteresting'].set_value(False)

            self.set_line_width(self.line_width)

            base_curve.plugs['intermediateObject'].set_value(True)

            base_curve.plugs['worldSpace'].element(0).connect_to(
                transform_geometry.plugs['inputGeometry'],
            )
            transform_geometry.plugs['outputGeometry'].connect_to(
                curve.plugs['create'],
            )
            self.plugs['shapeMatrix'].connect_to(
                transform_geometry.plugs['transform'],
            )

            self.plugs['shapeMatrix'].set_value([
                size, 0.0, 0.0, 0.0,
                0.0, size, 0.0, 0.0,
                0.0, 0.0, size, 0.0,
                0.0, 0.0, 0.0, 1.0
            ])

            curves.append(curve)
            base_curves.append(base_curve)

        # connect vis if this handle is a gimbal
        if '_Gimbal_Ctrl' in self.name:
            for crv in curves:
                if not crv.plugs['visibility'].is_connected():
                    if self.parent.plugs.exists('gimbalVisibility'):
                        self.parent.plugs['gimbalVisibility'].connect_to(crv.plugs['visibility'])

        self.shape = new_shape
        self.curves = curves
        self.base_curves = base_curves

        return self.curves

    def set_line_width(self, line_width):
        self.line_width = line_width
        condition = (
                line_width is not None
                and float(self.controller.scene.maya_version) > 2018.0
        )
        if condition:
            for curve in self.curves:
                self.controller.scene.setAttr(
                    curve.plugs['lineWidth'],
                    line_width
                )

    def stretch_shape(self, end_position):
        if isinstance(end_position, Matrix):
            end_position = end_position.get_translation()
        if isinstance(end_position, Transform):
            end_position = end_position.get_translation()

        handle_length = (end_position - self.get_matrix().get_translation()).magnitude()
        size = self.size
        side = self.side
        aim_vector = env.aim_vector
        if side == 'right':
            aim_vector = [x*-1.0 for x in env.aim_vector]

        shape_matrix = Matrix(0.0, 0.0, 0.0)
        shape_matrix.set_translation([
            handle_length * 0.5 * aim_vector[0],
            handle_length * 0.5 * aim_vector[1],
            handle_length * 0.5 * aim_vector[2]
        ])
        shape_matrix.set_scale([
            size if not aim_vector[0] else handle_length,
            size if not aim_vector[1] else handle_length,
            size if not aim_vector[2] else handle_length
        ])
        self.plugs['shapeMatrix'].set_value(list(shape_matrix))

    def get_shape(self):
        shapes = []
        for curve in self.curves:
            matrix_list = self.plugs['shapeMatrix'].get_value(Matrix().data)
            shapes_data = dict(
                matrix=matrix_list,
                curve_data=curve.data
            )
            shapes.append(shapes_data)
        return

    def set_shape_matrix(self, matrix):
        self.plugs['shapeMatrix'].set_value(list(matrix))

    def get_shape_matrix(self):
        return Matrix(self.plugs['shapeMatrix'].get_value(list(Matrix())))

    def multiply_shape_matrix(self, matrix):
        value = self.plugs['shapeMatrix'].get_value(Matrix().data)
        self.plugs['shapeMatrix'].set_value(
            list(Matrix(value) * matrix)
        )

    def add_standard_plugs(self):
        pass

    def set_handle_color(self, color, hover):
        self.controller.scene.select(cl=True)
        self.controller.set_handle_color(self, color, hover)

    def set_gimbal_handle_color(self, color, hover):
        self.controller.scene.select(cl=True)
        self.controller.set_gimbal_handle_color(self, color, hover)

    def set_default_color(self, gimb, main):
        self.controller.scene.select(cl=True)
        self.controller.set_default_color(self, gimb, main)

    def assign_selected_vertices(self, mo=False):
        self.controller.assign_selected_vertices_to_handle(self, mo=mo)

    def remove_offset_from_snap(self):
        self.controller.remove_offset_from_snap(self)

    def get_transform_limits(self):
        limits = dict()
        for key in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            limits[key] = dict(
                enabled=self.controller.scene.transformLimits(
                    self.name,
                    **{'q': True, f'e{key}': True}
                ),
                value=self.controller.scene.transformLimits(
                    self.name,
                    **{'q': True, key: True}
                )
            )
        return limits

    def set_transform_limits(self, limits):
        for key in limits:
            if self.name:
                kwargs = {
                        str(f'e{key}'): tuple(limits[key]['enabled'])
                    }
                self.controller.scene.transformLimits(
                    self.name,
                    **kwargs
                )
                kwargs = {
                        str(key): tuple(limits[key]['value'])
                    }
                self.controller.scene.transformLimits(
                    self.name,
                    **kwargs
                )


    def reset_transform_limits(self):
        self.set_transform_limits(self.default_limits)

def test(controller):

    right_handle = controller.create_object(
        'CurveHandle',
        root_name='Handle',
        shape='cube',
        side='right'
    )

    right_handle.plugs['tx'].set_value(1.2)

    left_handle = controller.create_object(
        'CurveHandle',
        root_name='Handle',
        shape='cube',
        side='left'
    )

    left_handle.plugs['tx'].set_value(-1.2)

    center_handle = controller.create_object(
        'CurveHandle',
        root_name='Handle',
        shape='pyramid',
        side='center'
    )

    puppy_handle = controller.create_object(
        'CurveHandle',
        root_name='Handle',
        shape='puppy',
        side='center',
        color=[0.0, 1.0, 0.0]
    )

    puppy_handle.plugs['ty'].set_value(2.0)


if __name__ == '__main__':
    test()
