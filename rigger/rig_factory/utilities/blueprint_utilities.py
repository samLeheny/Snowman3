import os
import json
import uuid
import logging
import traceback
import Snowman3.utilities.version as irv
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut
import Snowman3.rigger.rig_factory.common_modules as com
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer

mirror_sides = dict(left='right', right='left')
DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


def get_blueprint():
    controller = com.controller_utils.get_controller()
    if not controller.root:
        raise Exception('Rig not found')
    for part in controller.root.get_parts(include_self=False):
        if part.layer == controller.current_layer:
            part.part_uuid = str(uuid.uuid4())
    blueprint = generate_blueprint(controller.root)
    snowman_version = irv.get_snowman_version()
    if snowman_version is None:
        snowman_version = 'DEV-%s' % os.environ['USERNAME']
    blueprint['snowman_version'] = snowman_version

    user_name = fut.get_user_name()
    blueprint['user_name'] = user_name

    return blueprint


def get_toggle_blueprint():
    controller = com.controller_utils.get_controller()
    if not controller.root:
        raise Exception('Rig not found')
    for part in controller.root.get_parts(include_self=False):
        if part.layer == controller.current_layer:
            part.part_uuid = str(uuid.uuid4())
    blueprint = generate_toggle_blueprint(controller.root)
    snowman_version = irv.get_snowman_version()
    if snowman_version is None:
        snowman_version = 'DEV-%s' % os.environ['USERNAME']
    blueprint['snowman_version'] = snowman_version

    user_name = fut.get_user_name()
    blueprint['user_name'] = user_name

    return blueprint


def generate_blueprint(part):
    controller = part.controller
    blueprint = part.get_blueprint()
    if blueprint is None:
        raise Exception('%s.get_blueprint() returned None' % part.__class__.__name__)
    if DEBUG:
        try:
            json.dumps(blueprint)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            raise Exception('Unable to serialize blueprint from : %s. See script editor.' % part)
    if isinstance(part, BaseContainer):
        part_blueprints = []
        for sub_part in part.get_parts(recursive=False):
            if controller.current_layer == sub_part.layer:
                part_blueprint = generate_blueprint(sub_part)
                if part_blueprint is None:
                    raise Exception('%s.get_toggle_blueprint() returned None' % sub_part.__class__.__name__)
                part_blueprints.append(part_blueprint)
        blueprint['part_members'] = part_blueprints
    return blueprint


def generate_toggle_blueprint(part):
    controller = part.controller
    blueprint = part.get_toggle_blueprint()
    if blueprint is None:
        raise Exception('%s.get_blueprint() returned None' % part.__class__.__name__)
    if DEBUG:
        try:
            json.dumps(blueprint)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            raise Exception('Unable to serialize blueprint from : %s. See script editor.' % part)
    if isinstance(part, BaseContainer):
        part_blueprints = []
        for sub_part in part.get_parts(recursive=False):
            if controller.current_layer == sub_part.layer:
                part_blueprint = generate_toggle_blueprint(sub_part)
                if part_blueprint is None:
                    raise Exception('%s.get_toggle_blueprint() returned None' % sub_part.__class__.__name__)
                part_blueprints.append(part_blueprint)
        blueprint['part_members'] = part_blueprints
    return blueprint


def get_mirror_blueprint(part):
    blueprint = part.get_mirror_blueprint()
    part_blueprints = []
    if isinstance(part, BaseContainer):
        for sub_part in part.get_parts(recursive=False):
            if sub_part.side in mirror_sides and sub_part.side == part.side:
                part_blueprints.append(get_mirror_blueprint(part))
    blueprint['part_members'] = part_blueprints
    return blueprint


def get_guide_blueprint_from_rig_blueprint(rig_blueprint):
    guide_blueprint = rig_blueprint.get('guide_blueprint')
    if not guide_blueprint:
        raise Exception('"guide_blueprint" key not found')
    part_members = []
    if 'part_members' in rig_blueprint:
        parts_key = 'part_members'
    else:
        parts_key = 'parts'  # Legacy blueprint support (delete when possible)
    for guide_part_blueprint in rig_blueprint.get(parts_key, []):
        part_members.append(
            get_guide_blueprint_from_rig_blueprint(guide_part_blueprint)
        )
    guide_blueprint[parts_key] = part_members
    return guide_blueprint


def get_part_blueprints(blueprints):
    """
    This function extracts nested part dicts from a blueprint and returns them as a flat list of dicts
    The dictionaries returned by this function are 'mutable'
    Changing them will change the contents of the 'blueprint' argument
    :param blueprints:
    :return: flat list of dicts (of parts)
    """
    assert isinstance(blueprints, list)
    parts_info = list()
    for part_blueprint in blueprints:
        sub_parts = part_blueprint.pop('part_members', [])
        parts_info.append(part_blueprint)
        parts_info.extend(get_part_blueprints(sub_parts))
    return parts_info

