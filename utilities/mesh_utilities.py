import maya.api.OpenMaya as om
from Snowman3.rigger.rig_factory.utilities import decorators as dec


@dec.m_object_arg
def get_vertex_count(mesh):
    return om.MItMeshVertex(mesh, om.MObject()).count()


@dec.m_object_arg
def get_closest_vertex_index(mesh, point):
    dag_path = om.MDagPath.getAPathTo(mesh)
    component = om.MObject()
    vertex_iterator = om.MItMeshVertex(dag_path, component)
    closest_distance = float('inf')
    closest_index = None
    while not vertex_iterator.isDone():
        d = vertex_iterator.position().distanceTo(point)
        if d < closest_distance:
            closest_distance = d
            closest_index = vertex_iterator.index()
        vertex_iterator.next()
    return closest_index


@dec.m_object_arg
def get_closest_vertex_uv(mesh, point):
    dag_path = om.MDagPath.getAPathTo(mesh)
    component = om.MObject()
    vertex_iterator = om.MItMeshVertex(dag_path, component)
    closest_distance = float('inf')
    closest_uv = [None, None]
    while not vertex_iterator.isDone():
        d = vertex_iterator.position().distanceTo(point)
        if d < closest_distance:
            closest_distance = d
            uv_util = om.MScriptUtil()
            uv_util.createFromList(closest_uv, 2)
            uvPoint = uv_util.asFloat2Ptr()
            vertex_iterator.getUV(uvPoint)
            closest_uv[1] = uv_util.getFloat2ArrayItem(uvPoint, 0, 1)
            closest_uv[0] = uv_util.getFloat2ArrayItem(uvPoint, 0, 0)
        vertex_iterator.next()
    return closest_uv
