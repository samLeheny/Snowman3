import logging

"""
This is for when we switch to functional builds
"""


def set_active_blueprint():
    logging.getLogger('rig_build').info('RigState: set_active_blueprint')


def after_finish_create():
    logging.getLogger('rig_build').info('RigState: after_finish_create')


def before_finish_create():
    logging.getLogger('rig_build').info('RigState: before_finish_create')


def after_set_parent_joints():
    logging.getLogger('rig_build').info('RigState: after_set_parent_joints')


def before_set_parent_joints():
    logging.getLogger('rig_build').info('RigState: before_set_parent_joints')


def before_create_parts():
    logging.getLogger('rig_build').info('RigState: before_create_parts')


def after_create_parts():
    logging.getLogger('rig_build').info('RigState: after_create_parts')


def before_create_container():
    logging.getLogger('rig_build').info('RigState: before_create_container')


def after_create_container():
    logging.getLogger('rig_build').info('RigState: after_create_container')


def before_import_geometry():
    logging.getLogger('rig_build').info('RigState: before_import_geometry')


def before_create_origin_geometry():
    logging.getLogger('rig_build').info('RigState: before_create_origin_geometry')


def after_create_origin_geometry():
    logging.getLogger('rig_build').info('RigState: after_create_origin_geometry')


def after_import_geometry():
    logging.getLogger('rig_build').info('RigState: after_import_geometry')


def after_create_parts():
    logging.getLogger('rig_build').info('RigState: after_create_parts')


def after_create_deformation_rig():
    logging.getLogger('rig_build').info('RigState: after_create_deformation_rig')


def before_post_create():
    logging.getLogger('rig_build').info('RigState: before_post_create')


def after_post_create():
    logging.getLogger('rig_build').info('RigState: after_post_create')


def after_finish_create():
    logging.getLogger('rig_build').info('RigState: after_finish_create')


def before_space_switchers():
    logging.getLogger('rig_build').info('RigState: before_space_switchers')


def after_space_switchers():
    logging.getLogger('rig_build').info('RigState: after_space_switchers')


def before_handle_shapes():
    logging.getLogger('rig_build').info('RigState: before_handle_shapes')


def after_handle_shapes():
    logging.getLogger('rig_build').info('RigState: after_handle_shapes')


def before_custom_plugs():
    logging.getLogger('rig_build').info('RigState: before_custom_plugs')


def after_custom_plugs():
    logging.getLogger('rig_build').info('RigState: after_custom_plugs')


def before_sdks():
    logging.getLogger('rig_build').info('RigState: before_sdks')


def after_sdks():
    logging.getLogger('rig_build').info('RigState: after_sdks')


def before_constraints():
    logging.getLogger('rig_build').info('RigState: before_constraints')


def after_constraints():
    logging.getLogger('rig_build').info('RigState: after_constraints')


def before_placements():
    logging.getLogger('rig_build').info('RigState: before_placements')


def after_placements():
    logging.getLogger('rig_build').info('RigState: after_placements')


def before_proxy_shaders():
    logging.getLogger('rig_build').info('RigState: before_proxy_shaders')


def after_proxy_shaders():
    logging.getLogger('rig_build').info('RigState: after_proxy_shaders')


def before_export_data():
    logging.getLogger('rig_build').info('RigState: before_export_data')


def after_export_data():
    logging.getLogger('rig_build').info('RigState: after_export_data')


def before_nonlinears():
    logging.getLogger('rig_build').info('RigState: before_nonlinears')


def after_nonlinears():
    logging.getLogger('rig_build').info('RigState: after_nonlinears')


def before_finalize():
    logging.getLogger('rig_build').info('RigState: before_finalize')


def finalize():
    logging.getLogger('rig_build').info('RigState: finalize')


def after_finalize():
    logging.getLogger('rig_build').info('RigState: after_finalize')


def before_save():
    logging.getLogger('rig_build').info('RigState: before_save')


def execute_pre_publish():
    logging.getLogger('rig_build').info('RigState: execute_pre_publish')


def process_blueprint():
    logging.getLogger('rig_build').info('RigState: process_blueprint')


def pre_publish():
    logging.getLogger('rig_build').info('RigState: pre_publish')


def execute_pre_save():
    logging.getLogger('rig_build').info('RigState: execute_pre_save')


def finalize_rig():
    logging.getLogger('rig_build').info('RigState: finalize_rig')


def finalize_face():
    logging.getLogger('rig_build').info('RigState: finalize_face')
