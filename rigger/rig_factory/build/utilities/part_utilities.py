import logging
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.part_objects.root import Root
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_neck import BipedNeck
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_neck_fk import BipedNeckFk
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_neck_ik import BipedNeckIk
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_neck import QuadrupedNeck
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_neck_fk_spline import BipedNeckFkSpline
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_neck_fk_spline import QuadrupedNeckFkSpline


# ----------------------------------------------------------------------------------------------------------------------
def setup_settings_handle():
    controller = cut.get_controller()
    position_settings_handle(controller)
    container = controller.root
    if container.settings_handle:
        parent_joint = get_neck_joint(controller)
        if not parent_joint:
            parent_joint = get_main_joint(controller)
        if not parent_joint:
            return dict(
                status='warning',
                warning='Parent joint not found'
            )
        controller.create_parent_constraint(
            parent_joint,
            container.settings_handle.groups[0],
            mo=True
        )
        controller.create_scale_constraint(
            parent_joint,
            container.settings_handle.groups[0],
            mo=True
        )


# ----------------------------------------------------------------------------------------------------------------------
def position_settings_handle(controller, minimum_size=1.0):
    container = controller.root
    meshs = controller.scene.listRelatives(
        container.root_geometry_group.name,
        ad=True,
        type='mesh'
    )
    bbox = controller.scene.get_bounding_box(meshs)
    height = bbox[4] - bbox[1]
    width = bbox[3] - bbox[0]
    depth = bbox[5] - bbox[2]

    average_size = float(height + width + depth) / 3.0
    handle_size = average_size * 0.2
    if handle_size < minimum_size:
        handle_size = minimum_size

    container.settings_handle.groups[0].plugs['translate'].set_value(
        [
            0.0,
            bbox[4] + handle_size,
            0.0
        ]
    )

    container.settings_handle.plugs.set_values(
        overrideEnabled=True,
        overrideRGBColors=True,
        overrideColorRGB=env.colors['highlight'],
    )
    container.settings_handle.default_color = env.colors['highlight']

    shape_matrix = container.settings_handle.get_shape_matrix()
    shape_matrix.set_scale([handle_size, handle_size * -1.0, handle_size])
    container.settings_handle.set_shape_matrix(shape_matrix)


# ----------------------------------------------------------------------------------------------------------------------
def get_main_joint(controller):
    root_types = ( Root, )
    container = controller.root
    for part in container.find_parts(*root_types):
        parent_joint = part.cog_joint
        return parent_joint


# ----------------------------------------------------------------------------------------------------------------------
def get_neck_joint(controller):
    neck_types = (
        BipedNeck,
        BipedNeckFk,
        BipedNeckIk,
        BipedNeckFkSpline,
        QuadrupedNeckFkSpline,
        QuadrupedNeck
    )
    container = controller.root
    neck_parts = container.find_parts(*neck_types)
    if neck_parts:
        parent_joint = neck_parts[0].joints[-1]
        if len(neck_parts) > 1:
            logging.getLogger('rig_build').warning(
                'Multiple neck parts found. Parenting settings handle to the first found: %s' % (parent_joint)
            )
        return parent_joint
