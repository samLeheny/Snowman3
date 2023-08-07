import re


def get_snowman_version():
    """
    Hoping for a better way to extract the numbers than string split
    """
    version = re.findall(r'Snowman_\d+\.\d+\.\d+', __file__)
    if version:
        return version[0]
    else:
        return None
