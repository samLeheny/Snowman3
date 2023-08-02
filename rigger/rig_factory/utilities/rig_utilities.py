import logging

from Snowman3.rigger.rig_factory.objects.rig_objects.capsule import Capsule
from Snowman3.rigger.rig_factory.objects.rig_objects.space_switcher import SpaceSwitcher
from Snowman3.rigger.rig_factory.objects.part_objects.container import ContainerGuide
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.shader import Shader
from Snowman3.rigger.rig_factory.objects.deformer_objects.skin_cluster import SkinCluster
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.rig_objects.constraint import ParentConstraint, PointConstraint, \
    OrientConstraint, ScaleConstraint
import Snowman3.rigger.rig_factory.utilities.string_utilities as stu


def initialize_node(controller, node_name, **kwargs):
    """
    takes the name of an existing node and wraps it in the right Object instance
    :param node:
    :param parent:
    :return:
    """
    parent = kwargs.get('parent', None)
    if isinstance(node_name, str):
        m_object = controller.scene.get_m_object(node_name)
    else:
        m_object = node_name
    node_name = controller.scene.get_selection_string(m_object)
    object_type = controller.scene.get_m_object_type(m_object)

    if object_type == 'skinCluster':
        influences = [controller.initialize_node(x) for x in controller.scene.skinCluster(node_name, q=True,
                                                                                          influence=True)]
        geometry = controller.initialize_node(controller.scene.skinCluster(node_name, q=True, geometry=True)[0])
        node = SkinCluster(
            controller=controller,
            root_name=node_name
        )
        node.name = node_name
        node.m_object = controller.scene.get_m_object(node_name)
        node.geometry = geometry
        node.influences = influences

        if parent:
            controller.start_parent_signal.emit(node, parent)
            node.parent = parent
            parent.children.append(node)
            controller.end_parent_signal.emit(node, parent)

        return node


def create_rig_shaders(rig):
    for key in env.colors:
        side_color = env.colors[key]
        if key:
            shader = rig.create_child(
                Shader,
                node_type='lambert',
                segment_name=key.title(),
                side=None
            )
            shader.plugs['ambientColor'].set_value([0.75, 0.75, 0.75])
            shader.plugs['color'].set_value(side_color)
            shader.plugs['diffuse'].set_value(0.0)
            shader.plugs['transparency'].set_value([0.8, 0.8, 0.8])
            rig.shaders[key] = shader
    flat_colors = dict(
        x=[1.0, 0.1, 0.1],
        y=[0.1, 1.0, 0.1],
        z=[0.1, 0.1, 1.0],
        black=[0.1, 0.1, 0.1]
    )
    for key in flat_colors:
        color = flat_colors[key]
        shader = rig.create_child(
            Shader,
            node_type='lambert',
            segment_name=key.title(),
            side=None
        )
        shader.plugs['ambientColor'].set_value(color)
        shader.plugs['color'].set_value(color)
        shader.plugs['diffuse'].set_value(0.0)
        shader.plugs['transparency'].set_value([0.5, 0.5, 0.5])
        rig.shaders[key] = shader
    glass_shader = rig.create_child(
        Shader,
        node_type='blinn',
        segment_name='Glass',
        side=None
    )

    glass_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    glass_shader.plugs['transparency'].set_value([0.9, 0.9, 0.9])
    rig.shaders['glass'] = glass_shader

    blank_shader = rig.create_child(
        Shader,
        node_type='lambert',
        segment_name='Blank',
        side=None
    )
    glass_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    rig.shaders[None] = blank_shader

    origin_shader = rig.create_child(
        Shader,
        node_type='blinn',
        segment_name='Origin',
        side=None
    )
    origin_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    origin_shader.plugs['color'].set_value([0.8, 0.6, 0.6])

    realtime_shader = rig.create_child(
        Shader,
        node_type='blinn',
        segment_name='Realtime',
        side=None
    )
    realtime_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    realtime_shader.plugs['color'].set_value([0.6, 0.6, 0.8])

    rig.shaders['origin'] = origin_shader
    rig.shaders['realtime'] = realtime_shader

    for shader in rig.shaders.values():
        rig.plugs['nodeState'].connect_to(shader.plugs['nodeState'])  # stops maya from cleaning up this node


def bind_rig_geometry(self, rig, geometry):
    if isinstance(rig, ContainerGuide):
        geometry_name = str(geometry)
        bind_joints = rig.get_deform_joints()
        if geometry_name not in rig.geometry:
            raise Exception('the geometry "%s" is not a part of the rig "%s"' % (geometry, rig))
        if not bind_joints:
            bind_joints = rig.get_joints()
            logging.getLogger('rig_build').warning('"%s" does not have any bind joints...' % rig)

        skin_cluster = self.create_skin_cluster(
            geometry,
            bind_joints,
            root_name=geometry_name
        )
        rig.deformers.append(skin_cluster)
        geometry.deformers.append(skin_cluster)
        return skin_cluster
    else:
        raise Exception('Invalid type "%s" cannot bind_rig_geometry' % rig)


def create_parent_capsule(controller, part, parent_joint):

    if part.parent_capsule:
        controller.schedule_objects_for_deletion(part.parent_capsule)
        controller.delete_scheduled_objects()

    if parent_joint is not None and part.joints:
        kwargs = dict(
            side=part.side,
            size=1.0
        )
        this = part.create_child(
            Transform,
            segment_name='Parent',
            **kwargs
        )
        capsule = this.create_child(
            Capsule,
            segment_name='Parent',
            **kwargs
        )
        kwargs['index'] = 0
        kwargs['patemny'] = 0

        locator_transform_1 = this.create_child(
            Transform,
            segment_name='ParentStart',
            **kwargs
        )
        locator_1 = part.create_child(
            Locator,
            segment_name='ParentStart',
            parent=locator_transform_1,
            **kwargs
        )
        locator_transform_2 = this.create_child(
            Transform,
            segment_name='ParentEnd',
            **kwargs
        )
        locator_2 = part.create_child(
            Locator,
            segment_name='ParentEnd',
            parent=locator_transform_2,
            **kwargs
        )
        controller.create_point_constraint(
            part.joints[0], locator_transform_1
        )
        controller.create_point_constraint(
            parent_joint, locator_transform_2
        )
        controller.create_point_constraint(
            part.joints[0],
            parent_joint,
            capsule
        )
        controller.create_aim_constraint(
            parent_joint,
            capsule,
            aimVector=env.aim_vector
        )
        locator_1.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position2'])
        locator_transform_1.plugs['visibility'].set_value(False)
        locator_transform_2.plugs['visibility'].set_value(False)
        part.parent_capsule = this
        capsule.mesh.assign_shading_group(part.get_root().shaders['highlight'].shading_group)

        return this


def create_distance_between(handle_a, handle_b, root_name=None, index=None, parent=None):
    if not parent:
        parent = handle_a
    if not root_name:
        root_name = handle_a.root_name
    if root_name and index:
        root_name = '{0}{1:03d}'.format(
            root_name,
            index
        )
    distance_between_node = parent.create_child(
        DependNode,
        node_type='distanceBetween',
        root_name='%s_distanceBetween' % root_name
    )
    for handle, plug in zip((handle_a, handle_b), ('point1', 'point2')):
        pos = handle.create_child(
            Locator,
            root_name='%s_distancePosition%s' % (
                root_name,
                plug
            )
        )
        pos.plugs['visibility'].set_value(False)
        pos.plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs[plug])
    return distance_between_node
