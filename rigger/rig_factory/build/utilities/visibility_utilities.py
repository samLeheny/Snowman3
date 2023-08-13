import logging
import traceback
import Snowman3.rigger.rig_factory.objects as obs
from Snowman3.rigger.rig_factory.objects.face_objects.face import Face
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm_bendy import BipedArmBendy
from Snowman3.rigger.rig_factory.objects.creature_objects.bird_wing import BirdWing
from Snowman3.rigger.rig_factory.objects.part_objects.root import Root
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_main import BipedMain
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_main import QuadrupedMain
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_back_leg import QuadrupedBackLeg
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_bendy_back_leg import QuadrupedBendyBackLeg
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_leg import BipedLeg
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_leg_bendy import BipedLegBendy
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.part_objects.autowheel import Autowheel
from Snowman3.rigger.rig_factory.objects.deformer_parts.new_lattice_squish import NewLatticeSquish


def setup_visibility_plugs():
    """
    Sets up visibility attributes on Containers based on conditions (parts existing etc)
    """
    controller = cut.get_controller()
    container = controller.root

    secondary_handles = []
    bendy_vis_exception_parts = []

    faces = container.find_parts(Face)

    leg_parts = container.find_parts(
        BipedLeg,
        BipedLegBendy
    )

    quad_leg_parts = container.find_parts(
        QuadrupedBackLeg,
        QuadrupedBendyBackLeg
    )

    wings = container.find_parts(BirdWing)

    for face in faces:
        bendy_vis_exception_parts.extend(face.get_parts())

    for wing in wings:
        bendy_vis_exception_parts.extend(wing.get_parts(BipedArmBendy))

    for part in container.get_parts():
        if part not in bendy_vis_exception_parts:
            secondary_handles.extend(part.secondary_handles)

    autowheel_parts = container.find_parts(Autowheel)

    if container.standin_group:
        placement_visibility_plug = container.settings_handle.create_plug(
            'placementsVis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )
        placement_visibility_plug.connect_to(container.placement_group.plugs['visibility'])
        container.add_plugs(placement_visibility_plug, keyable=False)

    if faces:
        face_vis_plug = lazy_create_plug(
            container.settings_handle,
            'Face_Control_Vis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )
        face_sub_handle_plug = lazy_create_plug(
            container.settings_handle,
            'faceSubControlVis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )
        for face in faces:
            face_vis_plug.connect_to(face.plugs['visibility'])
            for part in face.get_parts():
                for handle in part.secondary_handles:
                    face_sub_handle_plug.connect_to(handle.plugs['visibility'])

    if secondary_handles:
        secondary_handle_plug = lazy_create_plug(
            container.settings_handle,
            'bendyVis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )
        for handle in secondary_handles:
            secondary_handle_plug.connect_to(handle.plugs['visibility'])

    if leg_parts:
        foot_placement_plug = lazy_create_plug(
            container.settings_handle,
            'foot_placements',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )

        for leg_part in leg_parts:
            foot_placement_plug.connect_to(leg_part.heel_placement_node.plugs['visibility'])
            foot_placement_plug.connect_to(leg_part.ball_placement_node.plugs['visibility'])

    if quad_leg_parts:
        foot_placement_plug = lazy_create_plug(
            container.settings_handle,
            'foot_placements',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )

        for quad_leg_part in quad_leg_parts:
            foot_placement_plug.connect_to(quad_leg_part.ball_placement_node.plugs['visibility'])

    bifrost_group_names = [
        'Bifrost_Grp'
    ]
    bifrost_groups = [x for x in bifrost_group_names if controller.scene.objExists(x)]
    if bifrost_groups:
        bifrost_plug = container.settings_handle.create_plug(
            'bifrostGeoVis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )
        container.add_plugs(bifrost_plug, keyable=False)

        for bifrost_group in bifrost_groups:
            try:
                controller.connectAttr(bifrost_plug.name, '{0}.visibility'.format(bifrost_group))
            except Exception as e:
                logging.getLogger('rig_build').error(traceback.format_exc())

    root_visibility_plug = container.settings_handle.plugs['RootCtrlVis']

    for part in controller.root.get_parts():
        if isinstance(part, (Root,)):
            root_ctrls = [handle for handle in part.get_handles() if 'Gimbal' not in handle.name][
                         :-1]  # excluding the COG
            for ctrl in root_ctrls:
                root_visibility_plug.connect_to(ctrl.children[2].plugs['visibility'])
        if isinstance(part, (BipedMain, QuadrupedMain)):
            for handle in part.get_handles():
                if 'Gimbal' not in handle.name:
                    root_visibility_plug.connect_to(handle.children[2].plugs['visibility'])

    geometry_roots = container.geometry_group.get_children(
        Transform
    )
    for geometry_object in geometry_roots:
        controller.root.settings_handle.plugs['geometryVis'].connect_to(
            geometry_object.plugs['visibility']
        )

    if autowheel_parts:
        wheel_placements_plug = lazy_create_plug(
            container.settings_handle,
            'wheels_placements',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )

        for autowheel_part in autowheel_parts:
            wheel_placements_plug.connect_to(autowheel_part.left_wheel_placement_node.plugs['visibility'])
            wheel_placements_plug.connect_to(autowheel_part.right_wheel_placement_node.plugs['visibility'])

    squash_parts = container.find_parts(NewLatticeSquish)
    if squash_parts:
        squash_plug = lazy_create_plug(
            container.settings_handle,
            'squashLatticeVis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )

        for squash_part in squash_parts:
            squash_plug.connect_to(squash_part.deformer.plugs['visibility'])


def lazy_create_plug(node, name, **kwargs):
    """
        setup_visibility_plugs() can get executed multiple times, so we need to not create plugs more than once
    """
    if node.plugs.exists(name):
        return node.plugs[name]
    plug = node.create_plug(name, **kwargs)
    node.controller.root.add_plugs(plug)
    return plug


def crowd_geo_vis():
    # takes the hi res geo vis toggles and plugs them to the crowd geo
    controller = cut.get_controller()
    root = controller.root
    crowd_geo = []
    failed_plugs = []

    # find crowd geo (if any)
    for mesh_trn in filter(None, [x.parent for x in root.geometry.values() if isinstance(x, obs.Mesh)]):
        if mesh_trn.name.endswith('Crowd_Geo'):
            crowd_geo.append(mesh_trn)

    # find connection on hires geo and plug it to crowd geo
    for c_mesh in crowd_geo:
        try:
            mesh_shape = root.geometry[c_mesh.name.replace('Crowd_Geo', 'GeoShape')]
            mesh = mesh_shape.parent

            # checking if mesh has visibility connected
            if mesh.plugs['v'].is_connected():
                # get attribute connected to mesh vis
                try:
                    # the plug exists in framework
                    plugin = controller.named_objects[
                        controller.scene.listConnections(mesh.plugs['v'].name, s=True, d=False, p=True)[0]]
                except:
                    # the plug is a non framework node
                    maya_plug = controller.scene.listConnections(mesh.plugs['v'].name, s=True, d=False, p=True)[0]
                    plug_node = controller.initialize_node(maya_plug.split('.')[0])
                    plugin = plug_node.initialize_plug(maya_plug.split('.')[1])
            else:
                # set plugin to mesh visibility attribute
                plugin = mesh.plugs['v']

            # find if parent groups have vis connected
            parent_grps = []
            grp_name = mesh.parent
            # checking up to three top groups or until finding the "Geo_Grp"
            for i in range(3):
                if grp_name.name != 'Geo_Grp':
                    # if the top group has visibility toggle, append to list
                    if grp_name.plugs['v'].is_connected():
                        parent_grps.append(grp_name)
                    grp_name = grp_name.parent

            # connect to crowd if the mesh or the top groups have vis toggles
            if mesh.plugs['v'].is_connected() or parent_grps:
                # disconnect current connection on crowd geo (if any)
                if c_mesh.plugs['v'].is_connected():
                    # the attribute connected to the crowd object may not always be a framework registered node
                    c_plugin = controller.scene.listConnections(c_mesh.plugs['v'].name, s=True, d=False, p=True)[0]
                    controller.scene.disconnectAttr(c_plugin, c_mesh.plugs['v'].name)

                # connect attributes to crowd mesh vis
                if parent_grps:
                    mdl_node = parent_grps[0].plugs['v'].multiply(plugin)
                    if len(parent_grps) == 2:
                        mdl_node_2 = mdl_node.multiply(parent_grps[1].plugs['v'])
                        if len(parent_grps) == 3:
                            mdl_node_3 = mdl_node_2.multiply(parent_grps[2].plugs['v'])
                            mdl_node_3.connect_to(c_mesh.plugs['v'])
                        else:
                            mdl_node_2.connect_to(c_mesh.plugs['v'])
                    else:
                        mdl_node.connect_to(c_mesh.plugs['v'])
                else:
                    plugin.connect_to(c_mesh.plugs['v'])

        except Exception as e:
            failed_plugs.append(c_mesh.name)
            logging.getLogger('rig_build').error("Crowd geo vis error: \n {}".format(traceback.format_exc()))

    if failed_plugs:
        return dict(
            status='warning',
            warning="Couldn't copy vis toggles for:\n{}\nCheck crowd geo names matches hi-res geo".format(failed_plugs)
        )
