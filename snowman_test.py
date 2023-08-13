import os
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as ctrl_utils

os.environ['PROJECT_CODE'] = 'OptimusPrime'
os.environ['ENTITY_NAME'] = 'OptimusPrime_Robot'

dirpath = r'C:\Users\61451\Documents\Projects\{}\Assets\{}'.format(
    os.environ['PROJECT_CODE'],
    os.environ['ENTITY_NAME']
)


# Controller
controller = ctrl_utils.get_controller(build_directory=dirpath)
import Snowman3.rigger.rig_factory.startup as startup
startup.initialize_common_modules()


# Asset Root
root = controller.create_root(
    'BipedGuide',
    root_name='TestAsset'
)


#Parts
test_part = root.create_part(
    'RootGuide'
)

test_part = root.create_part(
    'HandleGuide',
    root_name='TestPart',
    side='left',
    shape='cube',
    size=1.0,
    create_gimbal=True
)