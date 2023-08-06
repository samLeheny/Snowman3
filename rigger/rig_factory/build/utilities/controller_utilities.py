import Snowman3.rigger.managers.scene_interactor as scene_interactor
SceneInteractor = scene_interactor.SceneInteractor
import Snowman3.rigger.rig_factory.controllers.controller as controller
Controller = controller.Controller


GLOBALS = {}


def get_controller(initialize=False, asset_name=None, dirpath=None):
    if initialize:
        if GLOBALS.get('controller', None):
            del GLOBALS['controller']
    elif GLOBALS['controller']:
        return GLOBALS['controller']
    GLOBALS['controller'] = Controller.get_controller()  # SceneInteractor()
    GLOBALS['controller'].create_managers(asset_name=asset_name, dirpath=dirpath)
    return GLOBALS['controller']
