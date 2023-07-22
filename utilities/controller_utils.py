import importlib
import Snowman3.riggers.managers.scene_interactor as scene_interactor
importlib.reload(scene_interactor)
SceneInteractor = scene_interactor.SceneInteractor


GLOBALS = {}


def get_controller(initialize=False):
    if initialize or not GLOBALS.get('c', None):
        if GLOBALS.get('c', None):
            del GLOBALS['c']
        GLOBALS['c'] = SceneInteractor()
        GLOBALS['c'].create_managers(asset_name='Optimus',
                                     dirpath=r'C:\Users\61451\Desktop\OptimusPrime\02_modeling\build')
    return GLOBALS['c']
