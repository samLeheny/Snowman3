import functools
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.task_utilities as tut
import Snowman3.rigger.rig_factory.build.utilities.general_utilities as gut
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
import Snowman3.rigger.rig_factory.objects as obs


# ----------------------------------------------------------------------------------------------------------------------
def get_cheek_driver_tasks(entity_build, parent=None):
    root_task = BuildTask(
        build=entity_build,
        parent=parent,
        name='Cheek Drivers'
    )
    for build in tut.flatten(entity_build):
        entity_task = BuildTask(
            build=build,
            parent=root_task,
            name=build.entity
        )
        for part_blueprint in gut.flatten_blueprint(build.rig_blueprint, include_self=False):
            if part_blueprint['klass'] == 'MouthSlider':
                predicted_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
                    **part_blueprint
                )
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name=predicted_name,
                    function=functools.partial(
                        setup_mouth_drivers,
                        predicted_name
                    )
                )


# ----------------------------------------------------------------------------------------------------------------------
def setup_mouth_drivers(part_name):
    controller = cut.get_controller()
    if part_name not in controller.named_objects:
        raise Exception('part not found: %s' % part_name)
    part = controller.named_objects[part_name]

