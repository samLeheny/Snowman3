import os
import logging
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as controller_utils
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as blueprint_utils
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.initializers as initializers


# ----------------------------------------------------------------------------------------------------------------------
def toggle_rig_state(build_directory=None):
    controller = controller_utils.get_controller()
    if not controller or not controller.root:
        raise Exception('No rig found.')

    build_root = self.get_build_root(retrieve_data=False,
                                     build_directory=None)  # Data gets retrieved in the build tasks
    first_task_root = tglt.get_toggle_tasks(build_root)
    callback_root = None
    if isinstance(controller.root, obs.Container) and controller.root.use_external_rig_data:
        if controller.root.use_manual_rig_data:
            question_lines = [
                'Have you saved your work?',
                'This blueprint is using external rig data and unsaved rig state work wil be lost.',
                'would you like to continue?'
            ]
            if not self.raise_question(
                    '\n'.join(question_lines),
                    title='Did you save before togging?'
            ):
                return
        callback_root = first_task_root
        first_task_root = erdt.get_export_rig_data_tasks(build_root)

    if callback_root:
        self.build_task_tree(
            first_task_root,
            callback=functools.partial(
                self.build_task_tree,
                callback_root,
                callback=callback
            )
        )
    else:
        self.build_task_tree(
            first_task_root,
            callback=callback
        )


# ----------------------------------------------------------------------------------------------------------------------
def prepare_for_build():
    controller = controller_utils.get_controller()
    controller.scene.refresh(suspend=True)


# ----------------------------------------------------------------------------------------------------------------------
def build():
    prepare_for_build()
    while True:
        task = self.execute_next()
        if self._build_tasks is None:
            break
        elif self._stop_build or task.break_point:
            self.setup_paused_state(task)
            break


# ----------------------------------------------------------------------------------------------------------------------
def rebuild(blueprint):
    controller = self.controller
    if not controller:
        raise Exception('No Controller found.')
    if controller.root:
        if self.raise_question('There seems to be a rig currently loaded. Would you like to delete it ?'):
            ptls.delete_container()
        else:
            return
    controller.reset()
    self.set_root_task(None)
    QApplication.processEvents()
    self.check_then_build_blueprint(blueprint)


# ----------------------------------------------------------------------------------------------------------------------
def check_then_build_blueprint(self, blueprint, build_face=False, callback=None):
    if not isinstance(blueprint, dict):
        self.raise_warning('Invalid blueprint type: %s' % type(blueprint))
        return
    blueprint = lpu.update_legacy_blueprint(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME'],
        blueprint
    )
    self.products_widget.set_blueprint(blueprint)
    if build_face:
        callback = functools.partial(
            self.import_face_blueprint,
            callback=callback
        )
    if not self._check_for_new_products or self.products_widget.is_up_to_date():
        self.show_products_widget()
        self.products_widget.animate_widget_visibility()
        self.build_blueprint(
            blueprint,
            callback=callback
        )

    else:
        self.products_widget.build_callback = functools.partial(
            self.update_blueprint_products,
            blueprint,
            callback=callback
        )
        self.show_products_widget()
        self.products_widget.update_visibility()
        self.products_widget.update_all(True)
        self.products_widget.skip_button_visibility(True)


# ----------------------------------------------------------------------------------------------------------------------
def build_blueprint(self, blueprint, callback=None):
    # try:
    #     btup.setup_local_build_directory()
    # except Exception as e:
    #     logging.getLogger('rig_build').error(traceback.format_exc())
    #     self.raise_warning('Failed to setup build directory. See log for details')
    self.build_task_tree(
        self.get_rig_task_root(
            rig_blueprint=blueprint
        ),
        callback=callback
    )


# ----------------------------------------------------------------------------------------------------------------------
def get_rig_task_root(self, **kwargs):
    if not env.local_build_directory:
        raise Exception('RigWidget.build_directory = None')
    if not os.path.exists(env.local_build_directory):
        os.makedirs(env.local_build_directory)
    logging.getLogger('rig_build').info('Resolving Build Tasks...')
    build_root = self.get_build_root(**kwargs)
    try:
        return initializers.get_root_task(build_root)
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        self.raise_warning(
            'Failed to resolve task root. See log for details',
            window_title='Task resolution failed'
        )
        raise


# ----------------------------------------------------------------------------------------------------------------------
def get_build_root(**kwargs):
    controller = controller_utils.get_controller()
    retrieve_data = kwargs.get('retrieve_data', True)
    build_directory = kwargs.pop('build_directory')
    #build_directory = kwargs.pop('build_directory', env.local_build_directory)
    '''self.update_progress(
        message='Getting Entity Data... ',
        maximum=3
    )
    kwargs.setdefault(
        'task_callback',
        self.build_task_callback
    )
    kwargs.setdefault(
        'children_about_to_be_inserted_callback',
        self.child_tasks_about_to_be_inserted
    )
    kwargs.setdefault(
        'children_inserted_callback',
        self.child_tasks_inserted
    )'''
    builds = []
    if not os.path.exists(build_directory):
        logging.getLogger('rig_build').critical('Build directory doesnt exist: %s' % build_directory)

    if 'rig_blueprint' not in kwargs:
        if not os.path.exists('%s/rig_blueprint.json' % build_directory):
            if controller.root:
                rig_blueprint = blueprint_utils.get_blueprint()
                kwargs['rig_blueprint'] = rig_blueprint

    try:
        for build in initializers.yield_builds(
                os.getenv('PROJECT_CODE'),
                os.getenv('ENTITY_NAME'),
                controller,
                build_directory,
                **kwargs
        ):
            if not build:
                raise Exception('build is None')
            if not build.build_directory:
                logging.getLogger('rig_build').critical('%s has no directory' % build.entity)
            if retrieve_data:
                if not build.build_directory:
                    self.raise_warning('unable to resolve a build_directory for %s' % build.entity)
                self.update_progress(message='%s\nLoading rig_blueprint.json...' % build.entity, value=1)
                build.retrieve_rig_blueprint()
                self.update_progress(message='%s\nLoading face_blueprint.json...' % build.entity, value=2)
                build.retrieve_face_blueprint()
                self.update_progress(message='%s\nLoading callbacks...' % build.entity, value=3)
            build.retrieve_callbacks()
            builds.append(build)
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        self.raise_warning(
            'Failed to resolve build root. See log for details',
            window_title='Build resolution failed'
        )
        raise
    self.show_task_widget()
    return builds[0]


# ----------------------------------------------------------------------------------------------------------------------
def build_task_tree(self, task_root, callback=None):
    if task_root is None:
        raise Exception('Task tree root is None')
    if not task_root.children:
        self.reload_widget_state()
        raise Exception('Task tree root "%s" has no children' % task_root.name)
    self.set_build_callback(callback)
    self.set_root_task(task_root)
    self.show_task_widget()
    if self._auto_build:
        self.build()
    else:
        self.build_task_widget.setup_button_state('stopped')
