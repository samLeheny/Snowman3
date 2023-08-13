#import rig_factory
#import rig_factory.objects as obs
from Snowman3.rigger.rig_factory.objects.rig_objects.curve_handle import CurveHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import StandardHandle
from Snowman3.rigger.rig_factory.objects.part_objects.container import ContainerGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part_group import PartGroupGuide
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import StandardHandle, GroupedHandle
#from rig_factory.objects.part_objects.base_part import BasePart
#from rig_factory.objects.part_objects.base_container import BaseContainer
#from rig_factory.objects.node_objects.transform import Transform
#from rig_factory.objects.node_objects.dag_node import DagNode

from Snowman3.rigger.rig_factory.objects.rig_objects.guide_handle import GuideHandle
#from Snowman3.utilities.rig_math.matrix import Matrix
#from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
#from rig_factory.objects.base_objects.weak_list import WeakList
import logging
#from rig_factory.objects.part_objects.rig_spline_part import RigSplinePart
#import rig_api.general as pgen

import maya.api.OpenMaya as om


# ----------------------------------------------------------------------------------------------------------------------
def create_part_handle(part, handle_type, **kwargs):
    this = part.create_child(handle_type, **kwargs)
    this.owner = part
    part.handles.append(this)
    return this


# ----------------------------------------------------------------------------------------------------------------------
def create_standard_handle(part, **kwargs):
    kwargs.setdefault('segment_name', 'Main')
    handle_type = kwargs.pop('handle_type', StandardHandle)
    return create_part_handle(part, handle_type, **kwargs)


# ----------------------------------------------------------------------------------------------------------------------
def create_guide_handle(part, **kwargs):
    kwargs.setdefault('segment_name', 'Main')
    handle_type = kwargs.pop('handle_type', GuideHandle)
    return create_part_handle(part, handle_type, **kwargs)


# ----------------------------------------------------------------------------------------------------------------------
def remove_offset_from_snap(controller, handle):
    logger = logging.getLogger('rig_build')

    if isinstance(handle, (GuideHandle, CurveHandle)):
        if handle.maintain_offset == [1]:
            handle.maintain_offset = [0]
            vert_pos = controller.scene.get_bounding_box_center([x.name for x in handle.vertices])

            controller.xform(handle, ws=True, t=vert_pos)

            handle.maintain_offset = [0]
            handle.offset_Vec = []
            handle.scale_offset = 0
        else:
            raise Exception(f"There is not offset on the  '{type(handle)}' data")
    else:
        raise Exception(f"Invalid handle type '{type(handle)}' for snap_handle_to_selected_verts")


# ----------------------------------------------------------------------------------------------------------------------
def assign_selected_vertices(controller, handle, mo=False):
    logger = logging.getLogger('rig_build')
    if isinstance(handle, (GuideHandle, CurveHandle)):
        controller.scene.convert_selection(toVertex=True)
        selected_vertices = controller.scene.list_selected_vertices()
        if not selected_vertices:
            raise Exception('No mesh components selected.')
        mesh_names = controller.scene.get_selected_mesh_names()
        if len(mesh_names) != 1:
            raise Exception('Select one mesh')
        vertex_indices = controller.scene.get_selected_vertex_indices()
        owner = handle.owner
        body = owner.get_root()
        vertices = []
        for i in range(len(mesh_names)):
            mesh_name = mesh_names[i]
            if mesh_name not in body.geometry:
                logger.info(f"Warning: The mesh name '{mesh_name}' is not part of the rig")
            else:
                mesh = body.geometry[mesh_name]
                vertices.extend([mesh.get_vertex(x) for x in vertex_indices[i]])
        if vertices:
            handle.vertices = vertices

        final_vec = controller.scene.get_bounding_box_center(*selected_vertices)
        if mo:
            vert_vec = om.MVector(controller.scene.get_bounding_box_center(*selected_vertices))
            handle_vec = om.MVector(controller.xform(handle, q=True, ws=True, t=True))
            differ_vec = handle_vec - vert_vec
            handle.offset_Vec = [differ_vec[0], differ_vec[1], differ_vec[2]]
            differ_vec = differ_vec
            final_vec = vert_vec + differ_vec
            handle.maintain_offset = [1]
            handle.scale_offset = 0

        else:
            handle.maintain_offset = [0]

        if selected_vertices:
            controller.xform(handle, ws=True, t=final_vec)

    else:
        raise Exception(f"Invalid handle type '{type(handle)}' for snap_handle_to_selected_verts")


# ----------------------------------------------------------------------------------------------------------------------
def assign_vertices(controller, handle, vertices, mo=False, differ_vec=None, scale=0):
    if isinstance(handle, (GuideHandle, CurveHandle)):
        if vertices:
            handle.vertices = vertices
            position = controller.scene.get_bounding_box_center([x.name for x in vertices])
            final_vec = position
            if mo and differ_vec:
                vert_vec = om.MVector(position)
                differ_vec = om.MVector(differ_vec[0], differ_vec[1], differ_vec[2])

                handle.offset_Vec = [differ_vec[0], differ_vec[1], differ_vec[2]]
                if scale:
                    differ_vec = differ_vec.normal() * scale
                final_vec = vert_vec + differ_vec
                handle.maintain_offset = [1]

            controller.xform(handle, ws=True, t=final_vec)
    else:
        raise Exception('Invalid handle type "%s" for snap_handle_to_selected_verts' % type(handle))


# ----------------------------------------------------------------------------------------------------------------------
def update_assign_vertices(controller, handle):
    position = controller.scene.get_bounding_box_center([x.name for x in handle.vertices])
    vert_vec = om.MVector(position)
    differ_vec = handle.offset_Vec
    differ_vec = om.MVector(differ_vec[0], differ_vec[1], differ_vec[2])
    if handle.scale_offset:
        differ_vec = differ_vec.normal() * handle.scale_offset

    final_vec = vert_vec + differ_vec
    controller.xform(handle, ws=True, t=final_vec)


def snap_handles_to_mesh_positions(rig):
    if isinstance(rig, (ContainerGuide, PartGroupGuide)):
        for handle in rig.get_handles():
            snap_handle_to_mesh_positions(handle)
    else:
        raise Exception(f"Invalid handle type '{type(rig)}' for snap_handles_to_mesh_positions")


# ----------------------------------------------------------------------------------------------------------------------
def snap_handle_to_mesh_positions(handle):
    if isinstance(handle, (GuideHandle, CurveHandle)):
        controller = handle.controller
        vertices = handle.vertices
        if vertices:
            position = controller.scene.get_bounding_box_center([x.name for x in vertices])
            final_pose = position
            if handle.maintain_offset == [1]:
                scale = handle.scale_offset
                offset_list = handle.offset_Vec
                differ_vec = om.MVector(offset_list[0], offset_list[1], offset_list[2])
                if scale:
                    differ_vec = differ_vec.normal() * scale
                final_pose = om.MVector(position) + differ_vec

            controller.xform(handle, ws=True, t=final_pose)

    else:
        raise Exception(f"Invalid handle type '{type(handle)}' for snap_handle_to_selected_verts")


# ----------------------------------------------------------------------------------------------------------------------
def set_handle_shape(
       handle,
       handle_data,
       normalize_gimbal=True
):
    if not isinstance(handle, CurveHandle):
        return dict(
            status='warning',
            warning=f'Invalid type: "{handle}" is not a subclass of CurveHandle'
        )
    if len(handle_data) == 2:
        shape, matrix = handle_data
        handle.set_shape(shape)
        handle.plugs['shapeMatrix'].set_value(matrix)
        info = f'Set handle matrix and shape: {shape}'

    else:
        handle.plugs['shapeMatrix'].set_value(handle_data)
        info = 'Set handle matrix.'

    if normalize_gimbal and isinstance(handle, GroupedHandle):
        handle.normalize_gimbal_shape()
    return dict( info=info )


# ----------------------------------------------------------------------------------------------------------------------
def set_handle_color(handle, color, hover):
    if color:
        handle.plugs['overrideEnabled'].set_value(True)
        handle.plugs['overrideRGBColors'].set_value(True)
        handle.plugs['overrideColorR'].set_value(color[0])
        handle.plugs['overrideColorG'].set_value(color[1])
        handle.plugs['overrideColorB'].set_value(color[2])
        if not hover:
            handle.color = color



'''
import rig_factory
import rig_factory.objects as obs
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.part_objects.container import ContainerGuide
from rig_factory.objects.part_objects.part_group import PartGroupGuide
from rig_factory.objects.part_objects.base_part import BasePart
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.dag_node import DagNode

import rig_factory.environment as env
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from Snowman3.utilities.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.base_objects.weak_list import WeakList
import logging
from rig_factory.objects.part_objects.rig_spline_part import RigSplinePart
import rig_api.general as pgen

import maya.api.OpenMaya as om


def create_part_handle(part, handle_type, **kwargs):
   this = part.create_child(
       handle_type,
       **kwargs
   )
   this.owner = part
   part.handles.append(this)
   # if isinstance(this, GroupedHandle) and this.gimbal_handle:
   #     this.gimbal_handle.owner = part
   return this


def create_standard_handle(part, **kwargs):
   kwargs.setdefault('segment_name', 'Main')
   handle_type = kwargs.pop(
       'handle_type',
       StandardHandle
   )
   return create_part_handle(part, handle_type, **kwargs)


def create_guide_handle(part, **kwargs):
   kwargs.setdefault('segment_name', 'Main')
   handle_type = kwargs.pop(
       'handle_type',
       GuideHandle
   )
   return create_part_handle(part, handle_type, **kwargs)


def expand_handle_shapes(controller, rig):
   top_group = controller.create_object(
       Transform,
       parent=rig,
       segment_name='ExpandedHandles'
   )
   rig.expanded_handles_group = top_group
   expanded_handles = []
   for handle in rig.get_handles(include_gimbal_handles=False):
       namespace = None
       if ':' in handle.name:
           namespace = handle.name.split(':')[0]
       handle.plugs['overrideEnabled'].set_value(1)
       handle.plugs['overrideVisibility'].set_value(False)
       shape_matrix_plug = handle.plugs['shapeMatrix']
       if handle.functionality_name:
           functionality_name = '%sExpanded' % handle.functionality_name
       else:
           functionality_name = 'Expanded'
       controller.current_layer = controller.add_layer(handle.layer)
       if namespace:
           controller.namespace = namespace
           if not controller.scene.namespace(exists=':%s' % namespace):
               controller.scene.namespace(add=':%s' % namespace)
           controller.scene.namespace(set=':%s' % namespace)
       expanded_group = handle.create_child(
           Transform,
           parent=top_group,
           functionality_name=functionality_name,
           matrix=list(handle.get_matrix())
       )
       expanded_handle = expanded_group.create_child(
           CurveHandle,
           shape=handle.shape,
           axis=handle.axis,
           owner=handle,
           matrix=handle.get_matrix() * Matrix(shape_matrix_plug.get_value(Matrix().data)),
           size=handle.size
       )
       expanded_handle.plugs['shapeMatrix'].set_value(list(Matrix()))
       expanded_handles.append(expanded_handle)
       expanded_handle.plugs['overrideEnabled'].set_value(True)
       expanded_handle.plugs['overrideRGBColors'].set_value(1)
       expanded_handle.plugs['overrideColorRGB'].set_value([0.6, 0.2, 0.9])
       expanded_handle.plugs['matrix'].connect_to(shape_matrix_plug)
       controller.scene.namespace(set=':')
       controller.namespace = None
       controller.current_layer = None

   controller.root.expanded_handles = expanded_handles


def collapse_handle_shapes(controller, rig):
   for handle in rig.get_handles(include_gimbal_handles=False):
       handle.plugs['overrideEnabled'].set_value(1)
       handle.plugs['overrideVisibility'].set_value(True)
       if isinstance(handle, GroupedHandle):
           handle.normalize_gimbal_shape()

   if rig.expanded_handles_group:
       controller.schedule_objects_for_deletion(rig.expanded_handles_group)
       controller.delete_scheduled_objects()



def assign_closest_vertices(part, mesh_name):
   if mesh_name in part.get_root().geometry:
       mesh = part.get_root().geometry[mesh_name]
       for handle in part.get_handles():
           try:
               index = part.controller.get_closest_vertex_index(
                   mesh,
                   handle.get_matrix().get_translation()
               )
               handle.snap_to_vertices([mesh.get_vertex(index)])
               del handle
           except Exception as e:
               del handle
               raise e
   else:
       raise Exception('Invalid mesh: %s ' % mesh_name)


def set_handle_mesh_positions(controller, part, positions):
   missing_handles = []
   missing_meshs = []
   handle_map = dict((handle.name, handle) for handle in part.get_handles())
   for handle_name in positions:
       if handle_name in handle_map:
           vertices = []
           data = positions[handle_name]
           if data:
               if [1] in data or [0] in data:
                   mo = data[-3]
                   differ_vec = data[-2]
                   scale_offst = data[-1]
                   data = data[:-3]
               else:
                   scale_offst = 0
                   mo = [0]
                   differ_vec = []
               for mesh_name, vertex_index in data:
                   if mesh_name in part.get_root().geometry:
                       mesh = part.get_root().geometry[mesh_name]
                       vertices.append(mesh.get_vertex(vertex_index))
                   else:
                       missing_meshs.append(mesh_name)
               controller.snap_handle_to_vertices(
                   handle_map[handle_name],
                   vertices,
                   mo=mo[0],
                   differ_vec=differ_vec,
                   scale=scale_offst
               )
       else:
           missing_handles.append(handle_name)

   if missing_handles:
       missing_strings = [missing_handles[x] for x in range(len(missing_handles)) if x < 10]
       if len(missing_handles) > 10:
           missing_strings.append('...')
       controller.raise_warning(
           'Unable to set some mesh positions due to missing handles: \n\n %s ' % '\n'.join(missing_strings)
       )

   missing_meshs = list(set(missing_meshs))

   if missing_meshs:
       missing_mesh_strings = [missing_meshs[x] for x in range(len(missing_meshs)) if x < 10]
       if len(missing_meshs) > 10:
           missing_mesh_strings.append('...')
       controller.raise_warning(
           'Unable to set some mesh positions due to missing Mesh\'s: \n\n %s ' % '\n'.join(missing_mesh_strings)
       )


def get_joints(item):
   if isinstance(item, BaseContainer):
       joints = WeakList(item.joints)
       for sub_part in item.get_parts(recursive=False):
           joints.extend(get_joints(sub_part))
       return joints
   elif isinstance(item, BasePart):
       return item.joints
   else:
       raise Exception('Invalid type "%s" for get_joints' % type(item))


def get_deform_joints(item):
   if isinstance(item, BaseContainer):
       joints = WeakList(item.deform_joints)

       for sub_part in item.get_parts(recursive=False):
           joints.extend(get_deform_joints(sub_part))
       return joints
   elif isinstance(item, BasePart):
       return item.deform_joints
   else:
       raise Exception('Invalid type "%s" for get_joints' % type(item))


def get_handle_mesh_positions(controller, rig):
   mesh_positions = dict()
   for handle in rig.get_handles():
       if hasattr(handle, 'vertices') and handle.vertices:
           mesh_positions[handle.name] = [(x.mesh.get_selection_string(), x.index) for x in handle.vertices] + \
                                         [handle.maintain_offset] + [handle.offset_Vec] + [handle.scale_offset]

   return mesh_positions


def get_handle_data(rig):
   data = []
   for handle in rig.get_handles():
       handle_data = dict(
           vertices=[str(x) for x in handle.vertices],
           root_name=handle.root_name,
           side=handle.side,
           index=handle.index,
           size=handle.size,
           selection_string=handle.get_selection_string()
       )
       data.append(handle_data)
   return data


def mirror_all(rigs, side='left'):
   # handle vertices go first so it doesn't overwrite the handle positions
   mirror_handle_vertices(rigs, side)
   mirror_handle_positions(rigs, side)
   mirror_handle_attributes(rigs, side)


def mirror_handle_positions(rigs, side='left', origin_point=None):

   for rig in rigs:
       controller = rig.controller
       all_handles = dict((x.name, x) for x in controller.root.get_handles())

       if not isinstance(rig, (BaseContainer, BasePart)):
           raise Exception('Invalid type "%s"' % type(rig))
       if side not in env.side_mirror_dictionary:
           raise Exception('Invalid side "%s"' % side)

       for handle in rig.get_handles():
           if handle.side != side:
               # Skip handles from other side or center
               continue
           mirror_handle_name = handle.name.replace(
               '%s_' % rig_factory.settings_data['side_prefixes'][handle.side],
               '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[handle.side]],
               1
           )

           if mirror_handle_name in all_handles:
               mirror_handle = all_handles[mirror_handle_name]
               matrix = handle.get_matrix()
               is_blink_slider = False
               if hasattr(handle, 'guide_mirror_function') and handle.guide_mirror_function == 'reverseX':
                   matrix.mirror_matrix()
               else:
                   translate = list(matrix.get_translation())
                   if isinstance(handle.owner, obs.BaseSliderGuide):  # check if it's a panel slider part
                       if controller.root.find_parts(obs.FacePanelGuide):  # check if the face panel exists
                           for panel_container in controller.root.find_parts(obs.FacePanelGuide):
                               mouth_part = panel_container.find_first_part(
                                   obs.MouthSliderGuide,
                                   side='center'
                               )
                               if mouth_part:
                                   mouth_pos = mouth_part.handles[0].plugs['translate'].get_value()
                                   eye_part = panel_container.find_first_part(
                                       obs.OpenEyeRegionsSliderGuide,
                                       side=env.side_mirror_dictionary[handle.side]
                                   )
                                   if mirror_handle_name == eye_part.handles[1].name:  # skip the blink slider
                                       is_blink_slider = True
                                   else:
                                       # logic: the mouth position plus the space between the mouth and the handle
                                       translate[0] = mouth_pos[0] + (mouth_pos[0] - translate[0])
                   else:
                       translate[0] = translate[0] * -1
                   matrix.set_translation(translate)
               if not is_blink_slider:  # skip the blink slider
                   mirror_handle.set_matrix(matrix)


def mirror_handle_vertices(rigs, side='left'):
   controller = rigs[0].controller
   all_handles = dict((x.name, x) for x in controller.root.get_handles())
   for rig in rigs:
       if not isinstance(rig, (BaseContainer, BasePart)):
           raise Exception('Invalid type "%s"' % type(rig))
       if side not in env.side_mirror_dictionary:
           raise Exception('Invalid side "%s"' % side)
   if side not in env.side_mirror_dictionary:
       raise Exception('Invalid side "%s"' % side)
   all_selected_handles = []
   for rig in rigs:
       all_selected_handles.extend(rig.get_handles())
   for handle in list(set(all_selected_handles)):
       if handle.side == side:
           mirror_handle_name = handle.name.replace(
               '%s_' % rig_factory.settings_data['side_prefixes'][side],
               '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[side]],
               1
           )
           if mirror_handle_name in all_handles:
               differ_vec = []
               mo = False
               scale = 0
               mirror_handle = all_handles[mirror_handle_name]
               mirror_vertices = []
               for vertex in handle.vertices:
                   mesh_name = vertex.mesh.name
                   mirror_mesh_name = vertex.mesh.name.replace(
                       '%s_' % rig_factory.settings_data['side_prefixes'][side],
                       '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[side]],
                       1
                   )
                   if mirror_mesh_name in controller.named_objects:
                       mesh_name = mirror_mesh_name
                   mesh = controller.named_objects[mesh_name]
                   position = controller.xform(vertex.name, ws=True, t=True, q=True)

                   if handle.offset_Vec:
                       differ_vec = [-1 * handle.offset_Vec[0], handle.offset_Vec[1], handle.offset_Vec[2]]
                       mo = True
                       scale = handle.scale_offset

                   position[0] = position[0] * -1
                   mirror_index = controller.get_closest_vertex_index(
                       mesh,
                       position,
                   )
                   mirror_vertex = mesh.get_vertex(mirror_index)
                   mirror_vertices.append(mirror_vertex)
               assign_vertices(
                   controller,
                   mirror_handle,
                   mirror_vertices,
                   mo=mo,
                   differ_vec=differ_vec,
                   scale=scale

               )


def mirror_handle_attributes(rigs, side='left'):
   controller = rigs[0].controller
   for rig in rigs:
       all_handles = dict((x.name, x) for x in rig.controller.root.get_handles())

       if not isinstance(rig, (BaseContainer, BasePart)):
           raise Exception('Invalid type "%s"' % type(rig))
       if side not in env.side_mirror_dictionary:
           raise Exception('Invalid side "%s"' % side)

       if isinstance(rig, BaseContainer):
           part_list = rig.get_parts(recursive=False)  # get all parts inside the container
       else:
           part_list = [rig]  # gets the part

       for part in part_list:
           if part.name.startswith(rig_factory.settings_data['side_prefixes'][side]):
               mirror_part = part.name.replace(
                   '%s_' % rig_factory.settings_data['side_prefixes'][side],
                   '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[side]],
                   1
               )
               if 'size' in controller.scene.listAttr(part.name, keyable=True):
                   controller.scene.setAttr('%s.size' % mirror_part, controller.scene.getAttr('%s.size' % part.name))

       for handle in rig.get_handles():
           if handle.side != side:
               # Skip handles from other side or center
               continue
           mirror_handle_name = handle.name.replace(
               '%s_' % rig_factory.settings_data['side_prefixes'][handle.side],
               '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[handle.side]],
               1
           )
           list_attr = controller.scene.listAttr(handle.name, keyable=True)

           for remove_attr in ['translate', 'rotate', 'scale', 'size']:
               list_attr = [a for a in list_attr if remove_attr not in a]
           if mirror_handle_name in all_handles:
               for attr in list_attr:
                   controller.scene.setAttr('%s.%s' % (mirror_handle_name, attr),
                                            controller.scene.getAttr('%s.%s' % (handle.name, attr)))


def transfer_handle_vertices(rig, mesh, side='left'):
   controller = rig.controller
   for handle in rig.get_handles():
       new_vertices = []
       for vertex in handle.vertices:
           position = controller.xform(vertex, ws=True, t=True, q=True)
           mirror_index = controller.get_closest_vertex_index(
               mesh,
               position,
           )
           mirror_vertex = mesh.get_vertex(mirror_index)
           new_vertices.append(mirror_vertex)
       assign_vertices(controller, handle, new_vertices)


def get_handle_shapes(rig, local=True):
   controller = rig.controller
   handle_shapes = dict()
   if local:
       for handle in rig.get_handles():
           if controller.current_layer == handle.layer:
               handle_shapes[handle.name] = [
                   handle.shape,
                   handle.plugs['shapeMatrix'].get_value(Matrix().data)
               ]
   else:
       for handle in rig.get_handles():
           handle_shapes[handle.name] = [
               handle.shape,
               handle.plugs['shapeMatrix'].get_value(Matrix().data)
           ]
   return handle_shapes


def get_handle_colors(rig):
   handle_color_dict = dict((h.name, [round(x, 5) for x in h.color]) for h in rig.get_handles())
   return handle_color_dict


def get_handle_default_colors(rig):
   handle_color_dict = {}
   for handle in rig.get_handles():
       override = handle.plugs['overrideEnabled'].get_value()
       if override:
           handle.plugs['overrideRGBColors'].get_value()
           r_value = handle.plugs['overrideColorR'].get_value()
           g_value = handle.plugs['overrideColorG'].get_value()
           b_value = handle.plugs['overrideColorB'].get_value()
           colors = [r_value, g_value, b_value]
           colors = [round(x, 5) for x in colors]
           if handle.default_color:
               handle_color_dict[handle.name] = handle.default_color
           else:
               handle_color_dict[handle.name] = colors
               handle.default_color = colors

   return handle_color_dict


def set_gimbal_handle_color(handle, color, hover):
   if color:
       handle.gimbal_handle.plugs['overrideEnabled'].set_value(True)
       handle.gimbal_handle.plugs['overrideRGBColors'].set_value(True)
       handle.gimbal_handle.plugs['overrideColorR'].set_value(color[0])
       handle.gimbal_handle.plugs['overrideColorG'].set_value(color[1])
       handle.gimbal_handle.plugs['overrideColorB'].set_value(color[2])
       if not hover:
           handle.gimbal_handle.color = color


def set_default_color(handle, gimb, main):
   if main:
       if handle.default_color:
           set_handle_color(handle, handle.default_color, False)
       else:
           handle.plugs['overrideEnabled'].set_value(False)
           handle.color = []
   if gimb:
       if handle.gimbal_handle:
           if handle.gimbal_handle.default_color:
               set_gimbal_handle_color(handle, handle.gimbal_handle.default_color, False)
           else:
               handle.gimbal_handle.plugs['overrideEnabled'].set_value(False)
               handle.gimbal_handle.color = []


def get_input_transforms(rig):
   controller = rig.controller
   input_transforms = dict()
   parts = controller.root.find_parts(RigSplinePart)
   for part in parts:
       if part.handles:
           for handle in part.handles:
               input_transform = handle.relationships.get('input_transform')
               if input_transform:
                   input_transforms[handle.name] = input_transform.name
   return input_transforms


def set_input_transforms(self, input_transforms):
   controller = self.controller
   if input_transforms:
       for key, value in input_transforms.items():
           target_converted = controller.named_objects[key]
           pgen.create_input_transform(self, source_handle_name=value, target=target_converted)


def set_handle_shapes(
       rig,
       shapes,
       namespace=None,
       normalize_gimbal=True
):
   logger = logging.getLogger('rig_build')
   updated_handles = []
   if shapes:
       handle_map = {handle.name: handle for handle in rig.get_handles()}
       for handle_name, handle_data in shapes.items():
           full_handle_name = handle_name
           if namespace:
               full_handle_name = '%s:%s' % (namespace, full_handle_name)
           if full_handle_name in handle_map:
               handle = handle_map[full_handle_name]
               # skin gimbals as we're going to set them using normalize_gimbal_shape later
               if '_Gimbal_' in handle_name and normalize_gimbal:
                   continue
               updated_handles.append(handle_name)
               result = set_handle_shape(
                   handle,
                   handle_data,
                   normalize_gimbal=normalize_gimbal
               )
               warning = result.get('warning')
               if warning:
                   logging.getLogger('rig_build').warning(warning)
           else:
               logger.info('WARNING: Handle not found "%s"' % handle_name)
   rig.custom_handles = True


def strs_to_handles_list(controller, str_sel_list):
   """
   Convert maya strings list to framework node_objects
   :param controller: Rigging framework controller obj
   :param str_sel_list: list(str) List of string names to convert.
   :return: list() List of framework node_objects.
   """
   handles = []
   for obj_str in str_sel_list:
       if obj_str in controller.named_objects.keys():
           handles.append(controller.named_objects[obj_str])
   return handles


def get_mirror_handles(handles):
   """
   Get the mirrored side's object. Objects which were not able to find its symmetrical object will be filtered and
   not be returned.
   :param handles: list(), list of framework node_objects
   :return: 2 list(), Lists of the handles and their existing symmetrical handles. These two lists are
   parallel to each other.
   """
   rev_handles = []
   org_handles = []
   all_handles = dict((x.name, x) for x in handles[0].controller.root.expanded_handles)
   for handle in handles:
       if handle.side != 'center':
           mirror_handle_name = handle.name.replace(
               '%s_' % rig_factory.settings_data['side_prefixes'][handle.side],
               '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[handle.side]],
               1
           )
           if mirror_handle_name in all_handles.keys():
               rev_handles.append(all_handles[mirror_handle_name])
               org_handles.append(handle)
   return org_handles, rev_handles


def symmetry_constrain_handle_shapes(org_handles, obj_handles):
   """
   Apply symmetryConstraint on handles to its symmetrical side. The two arguments should work in parallel of each
   other, use the get_mirror_handles function. Joints will be created, as the symmetryConstraint has a 'joint orient'
   attr that is required for it to work properly with rotations, and then node_objects will be then constrained to the
   joint.
   :param org_handles: The parents of the list of handles.
   :param obj_handles: The children of the list of handles.
   :return: 2 lists(), The parent joints which were generated, and the symmetrical joints that were generated.
   """
   org_jnts = []
   rev_jnts = []
   for org, rev in zip(org_handles, obj_handles):
       org_jnt, rev_jnt = symmetry_constrain_handle_shape(org, rev)
       org_jnts.append(org_jnt)
       rev_jnts.append(rev_jnt)
   return org_jnts, rev_jnts


def symmetry_constrain_handle_shape(org, rev):
   """
   symmetryConstraint on handles to its symmetrical side. The two arguments should work in parallel of each
   other, use the get_mirror_handles function. Joints will be created, as the symmetryConstraint has a 'joint orient'
   attr that is required for it to work properly with rotations, and then node_objects will be then constrained to the
   joint.
   :param org: The parent handle.
   :param rev: The child handle.
   :return: 2 type(Joint), The parent joint which were generated, and the symmetrical joint that was generated.
   """
   root = org.controller.root
   org_jnt = root.utilities_group.create_child(Joint, root_name='{0}_org'.format(org.root_name),
                                               matrix=org.get_matrix(), side=org.side, index=org.index)
   rev_jnt = root.utilities_group.create_child(Joint, root_name='{0}_rev'.format(org.root_name),
                                               matrix=rev.get_matrix(), side=rev.side, index=rev.index)

   org.controller.create_parent_constraint(org, org_jnt)
   rev.controller.create_parent_constraint(rev_jnt, rev)

   sym_cnst = rev.create_child(DagNode, node_type='symmetryConstraint',
                               root_name='{0}_symmetryConstraint'.format(rev.root_name))

   org_jnt.plugs['translate'].connect_to(sym_cnst.plugs['targetTranslate'])
   org_jnt.plugs['rotate'].connect_to(sym_cnst.plugs['targetRotate'])
   org_jnt.plugs['scale'].connect_to(sym_cnst.plugs['targetScale'])
   org_jnt.plugs['parentMatrix'].element(0).connect_to(sym_cnst.plugs['targetParentMatrix'])
   org_jnt.plugs['worldMatrix'].element(0).connect_to(sym_cnst.plugs['targetWorldMatrix'])
   org_jnt.plugs['rotateOrder'].connect_to(sym_cnst.plugs['targetRotateOrder'])
   org_jnt.plugs['jointOrient'].connect_to(sym_cnst.plugs['targetJointOrient'])

   sym_cnst.plugs['constraintTranslate'].connect_to(rev_jnt.plugs['translate'])
   sym_cnst.plugs['constraintRotate'].connect_to(rev_jnt.plugs['rotate'])
   sym_cnst.plugs['constraintScale'].connect_to(rev_jnt.plugs['scale'])
   sym_cnst.plugs['constraintRotateOrder'].connect_to(rev_jnt.plugs['rotateOrder'])
   sym_cnst.plugs['constraintJointOrient'].connect_to(rev_jnt.plugs['jointOrient'])

   rev_jnt.plugs['parentInverseMatrix'].element(0).connect_to(sym_cnst.plugs['constraintInverseParentWorldMatrix'])

   for jnt in [org_jnt, rev_jnt]:
       jnt.plugs['v'].set_value(0)

   for axis in ('scaleX', 'scaleY', 'scaleZ'):
       org.plugs[axis].connect_to(rev.plugs[axis])

   return org_jnt, rev_jnt


def apply_symmetry_constraint_on_selected_shape_handles(controller):
   """
   Apply symmetry constraint on selected shape handles. It's in the name of the function... silly.
   :param controller: rig controller
   :return: 2 lists(), of the generated lists
   """
   handles = strs_to_handles_list(controller, controller.scene.ls(sl=True))
   org_handles, rev_handles = get_mirror_handles(handles)
   org_jnts, rev_jnts = symmetry_constrain_handle_shapes(org_handles, rev_handles)
   return org_jnts, rev_jnts


'''