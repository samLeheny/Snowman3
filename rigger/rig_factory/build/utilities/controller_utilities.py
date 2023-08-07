import os
import logging
import traceback
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.system_signals as sig
import Snowman3.rigger.rig_factory.utilities.log_utilities as logu
import Snowman3.rigger.rig_factory.utilities.file_utilities as file_utils
from Snowman3.rigger.rig_factory.controllers.rig_controller import RigController
import Snowman3.rigger.rig_factory.common_modules as com


def initialize_base_controller(controller_type=None, mock=False, singleton=True, build_directory=None):
    """
    Simple controller without callbacks for publishing rigs
    """
    if singleton and rig_factory.active_controller:
        raise Exception('A controller has already been initialized')
    if controller_type is None:
        controller_type = RigController
    controller = controller_type.get_controller( mock=mock )

    '''log_path = logu.get_log_path()
    log_level = logu.get_log_level()

    logs_directory = os.path.dirname(log_path)

    if not os.path.exists(logs_directory):
        try:
            os.makedirs(logs_directory)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            raise Exception('Unable to create logs directory: %s' % logs_directory)

    controller.log_path = log_path

    logger = logging.getLogger('rig_build')
    logger.setLevel(log_level)
    file_handler = logging.FileHandler(controller.log_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)'''

    if not build_directory:
        build_directory = file_utils.get_user_build_directory()
    controller.build_directory = build_directory
    if build_directory and os.path.exists(build_directory):
        sig.set_build_directory(build_directory)
    else:
        logging.getLogger('rig_build').warning('Build directory does not exist: %s' % build_directory)
    rig_factory.active_controller = controller
    return controller


def initialize_rig_controller(controller_type=None, mock=False,  singleton=True, build_directory=None):
    """
    Rig controller with callbacks for user interaction
    """

    controller = initialize_base_controller(
        controller_type=controller_type,
        mock=mock,
        singleton=singleton,
        build_directory=build_directory
    )
    controller.register_standard_parts()
    controller.register_standard_containers()
    #com.system_signals.maya_callback_signals['pre_file_new_or_opened'].connect(com.part_tools.reset_controller)
    #com.system_signals.controller_signals['critical_error'].connect(set_critical_state)

    #controller.create_managers(asset_name=asset_name, dirpath=dirpath)
    return controller


def set_critical_state():
    controller = get_controller()
    controller.failed_state = True
    com.part_tools.reset_controller()


def get_controller(asset_name=None, build_directory=None):
    if rig_factory.active_controller:
        return rig_factory.active_controller
    controller = initialize_rig_controller(controller_type=RigController, build_directory=build_directory)
    return controller
