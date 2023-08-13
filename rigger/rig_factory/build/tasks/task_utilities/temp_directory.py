import logging
import os
import time
import traceback


temp_base = 'C:/Users/61451/Documents/RigProjects/snowman_temp'

'''
def get_temp_directory(name):
    directory = '{}/{}/{}/{}'.format(
        temp_base,
        os.environ.get('PROJECT_CODE', 'Unknown_Project'),
        os.environ.get('ENTITY_NAME', 'Unknown_Entity'),
        name
    )
    while not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            time.sleep(1)
    return directory
'''
