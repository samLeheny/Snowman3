import os
import logging
import traceback
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as bpu
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.initializers as bti

build_directory = r'C:\Users\61451\Desktop\OptimusPrime\02_modeling\build'


# ----------------------------------------------------------------------------------------------------------------------
def toggle_rig_state(controller, callback=None, build_directory=None):
    build_root = get_build_root(retrieve_data=False, build_directory=build_directory, controller=controller)



# ----------------------------------------------------------------------------------------------------------------------
def get_build_root(**kwargs):
    controller = kwargs.pop('controller')
    retrieve_data = kwargs.get('retrieve_data', True)
    build_directory = kwargs.pop('build_directory') #  env.local_build_directory)
    #kwargs.setdefault( 'task_callback', self.build_task_callback )
    #kwargs.setdefault( 'children_about_to_be_inserted_callback', self.child_tasks_about_to_be_inserted )
    #kwargs.setdefault( 'children_inserted_callback', self.child_tasks_inserted )
    builds = []
    if 'rig_blueprint' not in kwargs:
        if not os.path.exists(f'{build_directory}/rig_blueprint.json'):
            if controller.root:
                rig_blueprint = bpu.get_blueprint()
                kwargs['rig_blueprint'] = rig_blueprint

    for build in bti.yield_builds(
            'OptimusPrime',
            'Optimus',
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
    return builds[0]


########################################################################################################################
