import os
import imp
import uuid
import copy
import time
import traceback
import functools
import logging
import json
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as blu
#import rigging_widgets.build_task_executor.callbacks as cbk
#import Snowman3.rigger.rig_factory.build.tasks.task_utilities.legacy_blueprint_utilities as lbu
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as btl
import Snowman3.rigger.rig_factory.system_signals as sig
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as bpu

DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


class BuildTask(object):
    def __init__(
            self,
            build=None,
            name=None,
            parent=None,
            function=None,
            args=None,
            kwargs=None,
            warning=None,
            info=None,
            layer=None,
            namespace=None,
            create_children_function=None,
            always_expand=False
    ):
        super(BuildTask, self).__init__()
        if parent:
            if not isinstance(parent, BuildTask):
                raise Exception('Invalid parent type: %s' % type(parent))
        if build is not None and not isinstance(build, EntityBuild):
            raise Exception('Invalid build type: %s' % type(build))
        self.name = name
        self.build = None
        self.layer = layer
        self.namespace = namespace
        self.function = function
        self.id = str(uuid.uuid4())
        self.children = []
        self.args = args
        self.kwargs = kwargs
        self.warning = warning
        self.info = info
        self.break_point = False
        self.current = False
        self.status = None
        self.error_message = None
        self.parent = parent
        self.create_children_function = create_children_function
        self.seconds_to_complete = None
        self.always_expand = always_expand
        if isinstance(parent, BuildTask):
            parent.children.append(self)
        if build is None and parent and parent.build:
            build = parent.build
        if build:
            self.set_build(build)

    def set_build(self, build):
        if build is not None and not isinstance(build, EntityBuild):
            raise Exception('Invalid build type: %s' % type(build))
        self.build = build
        if build is None:
            if DEBUG:
                logging.getLogger('rig_build').info(
                    '<BuildTask name=%s>.set_build( None )' % self.name
                )
            self.namespace = None
            self.layer = None
        else:
            if DEBUG:
                logging.getLogger('rig_build').info(
                    '<BuildTask name=%s>.set_build( <EntityBuild entity=%s, layer=%s, namespace=%s> )' % (
                        self.name,
                        build.entity,
                        build.layer,
                        build.namespace
                    )
                )
            self.layer = build.layer
            self.namespace = build.namespace
        for child in self.children:
            child.set_build(build)

    def execute(self):
        start = time.time()
        return_value = None
        children_return_value = None
        if DEBUG:
            if self.build is None:
                raise Exception('<BuildTask name="%s">.build is None' % self.name)
            if self.build.children_about_to_be_inserted_callback is None:
                raise Exception(
                    '<EntityBuild name=%s>.children_about_to_be_inserted_callback is None' % self.build.entity)
            if self.build.children_inserted_callback is None:
                raise Exception('<EntityBuild name=%s>.children_inserted_callback is None' % self.build.entity)
            if self.build.task_callback is None:
                raise Exception('<EntityBuild name=%s>.task_callback is None' % self.build.entity)
        logging.getLogger('rig_build').info(
            'Executing %s  layer = %s, namespace = %s current_build_directory=%s local_build_directory=%s' % (
                self.name,
                self.layer,
                self.namespace,
                env.current_build_directory,
                env.local_build_directory
            )
        )
        self.setup_state()
        try:
            if self.function:
                return_value = self.function()
            if self.create_children_function:
                return_value = self.create_children_function()
                logging.getLogger('rig_build').info(str(self.create_children_function))
                if not isinstance(return_value, (dict, list)):
                    raise Exception('Invalid return value for create_children_function: %s' % type(return_value))
                if isinstance(return_value, list):
                    invalid_child_types = [type(x) for x in return_value if not isinstance(x, BuildTask)]
                    if invalid_child_types:
                        raise Exception('Invalid child types returned: %s' % invalid_child_types)
                    self.build.children_about_to_be_inserted_callback(self, len(return_value))
                    self.children.extend(return_value)
                    for child in return_value:
                        logging.getLogger('rig_build').info(
                            '%s generated child task: <BuildTask name=%s, layer=%s, namespace=%s>' % (
                                self.name,
                                child.name,
                                child.layer,
                                child.namespace
                            )
                        )
                        child.parent = self
                        if child.build is None:
                            child.set_build(self.build)
                    self.build.children_inserted_callback(self, return_value)

        except Exception as e:
            self.revert_state()
            self.status = 'failed'
            self.error_message = traceback.format_exc()
            if self.build:
                self.build.task_callback(self)
            raise
        self.revert_state()
        if self.status not in ['warning', 'failed']:
            self.status = 'complete'
        if isinstance(return_value, dict):
            self.set_return_state(return_value)
        elif isinstance(children_return_value, dict):
            self.set_return_state(children_return_value)
        self.seconds_to_complete = time.time() - start
        logging.getLogger('rig_build').info(
            'Completed "%s" in %s seconds' % (
                self.name,
                self.seconds_to_complete
            )
        )
        self.build.task_callback(self)
        return self

    def set_return_state(self, data):
        try:
            json.dumps(data)
            if isinstance(data, dict):
                for key in data:
                    setattr(self, key, data[key])
        except Exception as e:
            logging.getLogger('rig_build').warning('%s returned invalid data: %s' % (self.name, data))

    def __repr__(self):
        return '<%s name=%s>' % (self.__class__.__name__, self.name)

    def setup_state(self):
        env.current_build_directory = self.build.build_directory
        self.build.controller.current_layer = None
        self.build.controller.namespace = self.namespace
        if self.namespace:
            if not self.build.controller.scene.namespace(exists=':%s' % self.namespace):
                self.build.controller.scene.namespace(add=':%s' % self.namespace)
            self.build.controller.scene.namespace(set=':%s' % self.namespace)
        if self.layer and self.layer != os.environ['TT_ENTNAME']:
            self.build.controller.current_layer = self.build.controller.add_layer(self.layer)
        sig.controller_signals['reset'].block(True)

    def revert_state(self):
        self.build.controller.scene.namespace(set=':')
        self.build.controller.namespace = None
        self.build.controller.current_layer = None
        env.current_build_directory = None
        sig.controller_signals['reset'].block(False)


class EntityBuild(object):
    def __init__(
            self,
            project,
            entity,
            controller,
            build_directory=None,
            parent=None,
            namespace=None,
            guide=False,
            rig_blueprint=None,
            face_blueprint=None,
            rig_blueprint_file_name='rig_blueprint.json',
            face_blueprint_file_name='face_blueprint.json',
            retrieve_data=False,
            task_callback=None,
            children_about_to_be_inserted_callback=None,
            children_inserted_callback=None
    ):
        super(EntityBuild, self).__init__()
        self.project = project
        self.entity = entity
        self.controller = controller
        self.build_directory = build_directory
        self.namespace = namespace
        self.callbacks = None
        self.children = []
        self.parent = parent
        self.guide = guide
        self.rig_blueprint = None
        if rig_blueprint:
            self.set_rig_blueprint(rig_blueprint)
        self.face_blueprint = face_blueprint
        self.rig_blueprint_file_name = rig_blueprint_file_name
        self.face_blueprint_file_name = face_blueprint_file_name
        self.children_about_to_be_inserted_callback = children_about_to_be_inserted_callback
        self.children_inserted_callback = children_inserted_callback
        self.task_callback = task_callback
        if self.parent:
            if not self.task_callback:
                self.task_callback = self.parent.task_callback
            if not self.children_about_to_be_inserted_callback:
                self.children_about_to_be_inserted_callback = self.parent.children_about_to_be_inserted_callback
            if not self.children_inserted_callback:
                self.children_inserted_callback = self.parent.children_inserted_callback
        if parent:
            parent.children.append(self)
        if retrieve_data:
            self.retrieve_data()

    def __repr__(self):
        return '<%s entity=%s>' % (self.__class__.__name__, self.entity)

    def get_root(self):
        root = self
        while root.parent:
            root = root.parent
        return root

    def create_callback(self, function_name):
        if self.controller.scene.mock:
            return functools.partial(
                dummy_callback,
                function_name
            )

        def get_and_call_function(function_name):
            return self.get_build_function(function_name)()

        return functools.partial(
            get_and_call_function,
            function_name
        )

    @property
    def layer(self):
        return self.entity

    def get_build_function(self, function_name):
        file_name = 'build.py'
        build_module_path = '%s/%s' % (self.build_directory, file_name)
        if not os.path.exists(build_module_path):
            raise Exception('File not found: %s' % build_module_path)
        logging.getLogger('rig_build').info('Loading module from: %s' % build_module_path)
        module = imp.load_source(
            file_name.split('.')[0],
            build_module_path
        )
        if self.guide:
            build_object = module.AssetGuideBuilder(
                self.build_directory,
                self.controller
            )
        else:
            build_object = module.AssetRigBuilder(
                self.build_directory,
                self.controller
            )
        build_object.build = self
        build_object._namepace = self.namespace
        build_object.active_blueprint = self.rig_blueprint  # Supports legacy functionality
        if hasattr(build_object, function_name):
            return getattr(
                build_object,
                function_name
            )
        else:
            raise Exception('Function not found: "%s"' % function_name)

    def set_rig_blueprint(self, rig_blueprint):
        if rig_blueprint is None:
            raise Exception('rig_blueprint is None')
        rig_blueprint = copy.deepcopy(rig_blueprint)
        is_root_build = self.entity == os.environ['TT_ENTNAME']
        # Make sure we are in the right state
        if is_root_build and 'guide_blueprint' not in rig_blueprint:
            self.guide = True
        elif self.parent and self.parent.guide:
            if 'guide_blueprint' not in rig_blueprint:
                raise Exception('"guide blueprint" key not found in blueprint for %s' % self.entity)
            self.guide = True
            logging.getLogger('rig_build').info(
                'Extracting guide state blueprint for %s' % self.entity
            )
            rig_blueprint = blu.get_guide_blueprint_from_rig_blueprint(rig_blueprint)
        else:
            self.guide = False
        # If were in guide state, make sure its actually a guide state blueprint
        if self.guide and 'guide_blueprint' in rig_blueprint:
            raise Exception('The blueprint provided doesnt seem to be in guide state...')

        self.rig_blueprint = lbu.update_legacy_blueprint(
            self.project,
            self.entity,
            rig_blueprint
        )
    def retrieve_rig_blueprint(self):
        if self.build_directory is None:
            raise Exception('The build directory for %s is None' % self.entity)
        if not os.path.exists(self.build_directory):
            raise Exception('The build directory did not exist: %s' % self.build_directory)
        new_rig_blueprint = None
        if not self.rig_blueprint:
            rig_blueprint_path = '%s/%s' % (
                self.build_directory,
                self.rig_blueprint_file_name
            )
            if self.entity == os.environ['TT_ENTNAME'] and self.controller.root:  # Get from Scene
                new_rig_blueprint = bpu.get_blueprint()
                logging.getLogger('rig_build').info(
                    'rig_blueprint for %s loaded from scene' % self.entity
                )
            elif os.path.exists(rig_blueprint_path):  # Get from json
                with open(rig_blueprint_path, mode='r') as f:
                    logging.getLogger('rig_build').info(
                        'Loading rig blueprint from json: %s' % rig_blueprint_path
                    )
                    new_rig_blueprint = json.load(f)
            else:
                logging.getLogger('rig_build').critical(
                    'Blueprint path not found: %s' % rig_blueprint_path
                )
        if new_rig_blueprint:
            self.set_rig_blueprint(new_rig_blueprint)


    def retrieve_face_blueprint(self):
        """
        This should probably get the face blueprint right from the controller if entity == TT_ENTNAME
        """
        if self.face_blueprint:
            logging.getLogger('rig_build').info(
                '%s already had a face blueprint loaded. No need to retrieve.' % self.entity
            )
            return

        if not os.path.exists(self.build_directory):
            raise Exception('The build directory did not exist: %s' % self.build_directory)
        face_blueprint_path = '%s/%s' % (self.build_directory, self.face_blueprint_file_name)
        if os.path.exists(face_blueprint_path):
            with open(face_blueprint_path, mode='r') as f:
                self.face_blueprint = json.load(f)
            if not self.face_blueprint.get('groups', None):
                logging.getLogger('rig_build').warning('Face blueprint had no groups: %s' % face_blueprint_path)
            else:
                logging.getLogger('rig_build').warning('Loaded face blueprint: %s' % face_blueprint_path)
        else:
            logging.getLogger('rig_build').info('Face blueprint path not found: %s' % face_blueprint_path)

    def retrieve_callbacks(self):
        if not os.path.exists(self.build_directory):
            raise Exception('The build directory did not exist: %s' % self.build_directory)
        self.callbacks = cbk.get_callbacks(
            self.entity,
            self.build_directory,
            self.controller,
            guide=self.guide,
            blueprint=self.rig_blueprint
        )

    def retrieve_data(self):
        self.retrieve_rig_blueprint()
        self.retrieve_face_blueprint()
        self.retrieve_callbacks()

    def duplicate(self, parent=None):
        this = EntityBuild(
            self.project,
            self.entity,
            self.controller,
            build_directory=self.build_directory,
            parent=parent,
            namespace=self.namespace,
            guide=self.guide,
            rig_blueprint=self.rig_blueprint,
            face_blueprint=self.face_blueprint,
            rig_blueprint_file_name=self.rig_blueprint_file_name,
            face_blueprint_file_name=self.face_blueprint_file_name,
            retrieve_data=False, # Copying data manually, we dont want to auto load
            task_callback=self.task_callback,
            children_about_to_be_inserted_callback=self.children_about_to_be_inserted_callback,
            children_inserted_callback=self.children_inserted_callback
        )
        this.retrieve_data = self.retrieve_data
        for child in self.children:
            child.duplicate(parent=this)
        return this

    def get_toggle_build(self, parent=None):
        toggle_build = self.duplicate()
        toggle_build.guide = not self.guide
        logging.getLogger('rig_build').info(
            'Switching <EntityBuild entity=%s>.guide from %s to %s' % (
                toggle_build.entity,
                self.guide,
                not toggle_build.guide
            )
        )
        if not self.controller.root:
            raise Exception('Rig not found.')
        toggle_blueprint = btl.get_toggle_blueprint()
        toggle_build.set_rig_blueprint(toggle_blueprint)
        for build in list(flatten(toggle_build))[1:]:
            build.rig_blueprint = None
            build.retrieve_rig_blueprint()
        return toggle_build


def flatten(root):
    yield root
    for x in root.children:
        for child in flatten(x):
            yield child


def empty_callable(*args, **kwargs):
    pass


def dummy_callback(function_name):
    logging.getLogger('rig_build').info(function_name)

