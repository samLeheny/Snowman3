import logging
import os
import uuid


def get_log_path():
    log_path = os.getenv('BATCH_LOG_PATH')
    if log_path:
        return log_path
    logs_directory = 'C:/User/61451/Documents/RigProjects/{}'.format( 'build' )
    '''
    logs_directory = 'Y:/{}/assets/type/{}/{}/pipeline/rigging_logs/{}/{}'.format(
        os.getenv('TT_PROJCODE'),
        os.getenv('TT_ASSTYPE'),
        os.getenv('TT_ENTNAME'),
        os.environ['USERNAME'],
        'build'
    )
    '''
    log_path = '{}/{}{}.log'.format(
        logs_directory,
        os.getenv('TT_ENTNAME'),
        uuid.uuid4()
    )
    return log_path


def get_log_level():
    batch_log_level = os.getenv('BATCH_LOG_LEVEL')
    if batch_log_level:
        return int(batch_log_level)
    return logging.WARNING
