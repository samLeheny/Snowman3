from Snowman3.rigger.rig_factory.build.utilities.controller_utilities import get_controller


def set_camera_clipping_planes():
    """Sets the clipping planes of the 'persp' camera to a size created by a bounding box of the imported geometries.
    """
    controller = get_controller()
    if 'RootGeometry_Grp' not in controller.named_objects:
        return
    geo_groups = controller.named_objects['RootGeometry_Grp']
    scene = controller.scene

    # Get bounds of geo
    meshes = scene.listRelatives(geo_groups, ad=1, type='mesh')

    if not meshes:
        return False  # No geo in scene, cancel to avoid weird values
    geo_bounds = scene.exactWorldBoundingBox(geo_groups)
    max_dist_from_origin = max(abs(val) for val in geo_bounds)  # Whichever direction is furthest from the origin
    cam_dist_from_origin = round(max_dist_from_origin * 5 / 100.0) * 100  # Add 20% margin and round to nearest 100
    cam_far = cam_dist_from_origin * 2
    min_range = round(0.1 + cam_far / 50000,
                      3)  # 'Min' clipping range value should be around 1:100000 near:far or closer

    # Clamp attrs for mini-scenes
    cam_far = max(cam_far, 1000.00)  # Min is 10 % of the default clipping
    min_range = max(min_range, 0.001)  # Min is maya min float value

    cams = scene.ls(typ='camera')
    for cam in cams:
        if scene.getAttr(cam + '.orthographic'):
            # Set far distance
            scene.setAttr(cam + '.farClipPlane', cam_far)
            scene.setAttr(cam + '.orthographicWidth', cam_far * 0.8)

            # Position camera back further to avoid near clipping (identify axis with largest default value)
            tfm = scene.listRelatives(cam, p=1)[0]
            max_axis = 'y'
            max_val = 0
            axis_mult = 1
            for axis in 'xyz':
                val = scene.getAttr(tfm + '.t' + axis)
                if abs(val) > max_val:
                    max_axis = axis
                    max_val = abs(val)
                    axis_mult = 1 if val > 0 else -1
            scene.setAttr(tfm + '.t' + max_axis, cam_dist_from_origin * axis_mult)
        else:
            # For persp, have further clipping plane to work with auto focus
            scene.setAttr(cam + '.farClipPlane', cam_far * 2.0)
            scene.setAttr(cam + '.nearClipPlane', min_range * 2.0)

    return
