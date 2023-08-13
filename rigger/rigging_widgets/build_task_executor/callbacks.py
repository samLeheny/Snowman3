import os
import imp
import logging
import functools
import traceback
from inspect import getmembers, isfunction
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut
import Snowman3.rigger.rig_factory.build.build_guide as bgd
import Snowman3.rigger.rig_factory.build.build_rig as brg


def get_callback(controller, build_directory, guide, function_name, blueprint, namespace=None):
    module = get_build_module(build_directory)
    if guide:
        build_object = module.AssetGuideBuilder(
            build_directory,
            controller
        )
    else:
        build_object = module.AssetRigBuilder(
            build_directory,
            controller
        )
    build_object._namepace = namespace
    if blueprint:
        build_object.active_blueprint = blueprint  # Supports legacy functionality
    if hasattr(build_object, function_name):
        return getattr(
            build_object,
            function_name
        )
    return functools.partial(dummy_callback, function_name)


class EntityCallbacks(object):

    def __init__(self, entity, build_directory, controller, guide=False, blueprint=None):
        self.entity = entity
        self.build_directory = build_directory
        self.controller = controller
        self.guide = guide
        self.blueprint = blueprint

    def __getitem__(self, function_name):
        if self.controller.scene.mock:
            return functools.partial(dummy_callback, function_name)
        return functools.partial(
            get_callback,
            self.controller,
            self.build_directory,
            self.guide,
            function_name,
            self.blueprint
        )


def get_functional_entity_callbacks(entity, build_directory, guide=False):
    logger = logging.getLogger('rig_build')
    show_module_name = '%s_scripts' % os.getenv('PROJECT_CODE').lower()
    try:
        show_module = __import__(show_module_name)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.warning('Unable to fund show module: %s' % show_module_name)
        raise Exception('Failed to import show module: %s' % show_module_name)
    if guide:
        callbacks = dict(getmembers(bgd, isfunction))
        guide_module_path = '%s/build_guide.py' % os.path.dirname(show_module.__file__.replace('\\', '/'))
        if os.path.exists(guide_module_path):
            guide_module = imp.load_source(
                '%s_build_guide' % os.environ['ENTITY_NAME'],
                guide_module_path
            )
            callbacks.update(dict(getmembers(guide_module, isfunction)))
        entity_guide_module_path = '%s/build_guide.py' % build_directory
        if os.path.exists(entity_guide_module_path):
            entity_guide_module = imp.load_source(
                '%s_build_guide' % entity,
                entity_guide_module_path
            )
            callbacks.update(dict(getmembers(entity_guide_module, isfunction)))
    else:
        callbacks = dict(getmembers(brg, isfunction))
        rig_module_path = '%s/build_rig.py' % os.path.dirname(show_module.__file__.replace('\\', '/'))
        if os.path.exists(rig_module_path):
            rig_module = imp.load_source(
                '%s_build_rig' % os.environ['ENTITY_NAME'],
                rig_module_path
            )
            callbacks.update(dict(getmembers(rig_module, isfunction)))
        entity_rig_module_path = '%s/build_rig.py' % build_directory
        if os.path.exists(entity_rig_module_path):
            entity_rig_module = imp.load_source(
                '%s_build_rig' % entity,
                entity_rig_module_path
            )
            callbacks.update(dict(getmembers(entity_rig_module, isfunction)))
    return callbacks


def get_callbacks(entity_name, build_directory, controller, guide=None, blueprint=None):
    '''if fut.get_show_config_data().get('functional_style_builds', False):
        return get_functional_entity_callbacks(
            entity_name,
            build_directory,
            guide=guide
        )
    else:'''
    return EntityCallbacks(
        entity_name,
        build_directory,
        controller,
        guide=guide,
        blueprint=blueprint
    )


def dummy_callback(function_name):
    logging.getLogger('rig_build').info(function_name)


def get_build_module(build_directory, module_name='build.py'):
    """
    Extracts build_directory/build.py as a module
    """
    build_module_path = '%s/%s' % (build_directory, module_name)
    if not os.path.exists(build_module_path):
        raise Exception('File not found: %s' % build_module_path)
    logging.getLogger('rig_build').info('Loading module from: %s' % build_module_path)
    module = imp.load_source(
        module_name.split('.')[0],
        build_module_path
    )
    return module


