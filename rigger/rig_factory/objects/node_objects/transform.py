from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty



def process_matrix(func):
    def new_func(*args, **kwargs):
        if kwargs.get('matrix', None):
            kwargs['matrix'] = Matrix(kwargs['matrix'])
        elif isinstance(kwargs.get('parent', None), Transform):
            kwargs['matrix'] = kwargs['parent'].get_matrix()
        return func(*args, **kwargs)
    return new_func


class Transform(DagNode):

    pretty_name = DataProperty( name='pretty_name' )
    suffix = 'Grp'

    @process_matrix
    def __init__(self, **kwargs):
        kwargs.setdefault('node_type', 'transform')
        super().__init__(**kwargs)


    @classmethod
    @process_matrix
    def create(cls, **kwargs):
        kwargs.setdefault('root_name', 'Body')
        this = super().create(**kwargs)
        if 'matrix' in kwargs:
            this.set_matrix(kwargs['matrix'])
        return this


    def set_matrix(self, matrix, world_space=True):
        self.controller.set_matrix(self, matrix, world_space=world_space)


    def get_matrix(self, world_space=True):
        return self.controller.get_matrix(self, world_space=world_space)


    def get_translation(self):
        return self.get_matrix().get_translation()


    def set_translation(self, translation, world_space=True):
        self.controller.xform(self.get_selection_string(), worldSpace=world_space, t=translation)


    def xform(self, **kwargs):
        return self.controller.xform(self, **kwargs)


    def create_in_scene(self):
        super().create_in_scene()


    def set_rotate_order(self, rotate_order):
        self.plugs['rotateOrder'].set_value(rotate_order)


    def get_children(self, *types, **properties):
        if types:
            children = [x for x in self.children if isinstance(x, types)]
        else:
            children = list(self.children)
        if properties:
            filtered_children = []
            for child in children:
                for key in properties:
                    if hasattr(child, key) and getattr(child, key) == properties[key]:
                        filtered_children.append(child)
            return filtered_children
        else:
            return children
