from dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject



def flatten_integers(*args):
    integers = []
    for arg in args:
        if isinstance(arg, int):
            integers.append(arg)
        elif isinstance(arg, (list, tuple, set)):
            integers.extend(flatten_integers(*arg))
    return integers



class Mesh(DagNode):

    deformers = ObjectListProperty( name='deformers' )
    node_type = DataProperty( name='node_type', default_value='mesh' )

    suffix = 'Msh'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def vertex_count(self):
        return self.controller.scene.get_vertex_count(self.m_object)


    def get_closest_vertex_index(self, point):
        return self.controller.scene.get_closest_vertex_index(self.m_object, point)


    def get_closest_vertex_uv(self, point):
        return self.controller.scene.get_closest_vertex_uv(self.m_object, point)


    def get_vertices(self, *indices):
        return [self.get_vertex(x) for x in flatten_integers(indices)]


    def get_vertex(self, index):
        if not isinstance(index, int):
            raise Exception(f"Cannot get vertex with index of type '{type(index)}'")
        vertex_name = f"{self.name}.vtx[{index}]"
        if vertex_name in self.controller.named_objects:
            return self.controller.named_objects[vertex_name]
        else:
            return self.create_child( MeshVertex, index=index, name=vertex_name, mesh=self )


    def get_face(self, index):
        if not isinstance(index, int):
            raise Exception(f"Cannot get face with index of type '{type(index)}'")
        face_name = f"{self.name}.f[{index}]"
        if face_name in self.controller.named_objects:
            return self.controller.named_objects[face_name]
        else:
            return self.create_child( MeshFace, index=index, name=face_name, mesh=self )


    def redraw(self):
        self.controller.scene.update_mesh(self.m_object)


    def unlock_normals(self):
        self.controller.scene.polyNormalPerVertex(
            self.get_selection_string(),
            ufn=True
        )


    def smooth_normals(self, angle=180):
        self.controller.scene.polySoftEdge(
            self.get_selection_string(),
            angle=angle,
            ch=False
        )



class MeshVertex(BaseObject):

    mesh = ObjectProperty( name='mesh' )
    index = DataProperty( name='index' )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def get_translation(self):
        return self.controller.xform(self.get_selection_string(), q=True, ws=True, t=True)

    def get_selection_string(self):
        return '{}.vtx[{}]'.format(self.mesh.get_selection_string(), self.index)



class MeshFace(BaseObject):

    mesh = ObjectProperty( name='mesh' )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def get_translation(self):
        return self.controller.xform(self.get_selection_string(), q=True, ws=True, t=True)

    def get_selection_string(self):
        return '{}.f[{}]'.format(self.mesh.get_selection_string(), self.index)


