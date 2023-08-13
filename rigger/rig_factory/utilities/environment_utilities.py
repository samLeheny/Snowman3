# python modules
from collections import OrderedDict

# iRig modules
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.part_objects.environment import Environment


def set_snapping(default=0):
    controller = cut.get_controller()

    """
    Eg. set_snapping(self.controller, {'Location1': 'Locator1', 'Location2': 'Locator2'}, default=1)
    :param controller: framework controller eg: self.controller in build.py

    :param data: name and locator name
    :type data: dict

    :param default: sets the default enum used, 0 means it will be set to Origin
    :type default: int

    :return:  None
    """
    if not isinstance(controller.root, Environment):
        return dict(
            info='Rig is type: %s. Set snapping aborted.' % controller.root.__class__.__name__
        )
    export_data_transforms = controller.root.export_data_group.get_children(Transform)
    if not export_data_transforms:
        return dict(
            info='Unable to create set snaps. Container.export_data_group group had no children. '
        )
    locator_dict = OrderedDict()
    misnamed_locators = []
    duplicate_locators = []

    for i in range(len(export_data_transforms)):
        transform_name = export_data_transforms[i].name
        convention = '_SetSnap_Loc_ExportData'
        if convention in transform_name:
            clean_name = transform_name.replace(convention, '').replace('_', ' ').replace(' ', '')
            if not clean_name:  # could be empty string
                misnamed_locators.append(transform_name)
            elif clean_name in locator_dict:
                duplicate_locators.append(clean_name)
            else:
                locator_dict[clean_name] = transform_name
        else:
            misnamed_locators.append(transform_name)

    settings_handle = controller.root.settings_handle

    for cog_name in ('Cog_Zro', 'C_Main_Cog_Zro'):
        cog_zro_grp = controller.named_objects.get(cog_name, None)
        if cog_zro_grp:
            break

    if not cog_zro_grp:
        return dict(
            warning='Unable to locate cog groups: %s/%s' % ('Cog_Zro', 'C_Main_Cog_Zro'),
            status='warning'
        )

    snap_enum_names = 'Origin'
    for clean_name, locator_name in locator_dict.items():
        snap_enum_names += ':%s' % clean_name

    # Create attribute
    snap_plug = settings_handle.create_plug(
        'SnapTo',
        at='enum',
        en=snap_enum_names,
        k=True
    )
    controller.root.add_plugs(snap_plug)

    counter = 1  # Start at 1 as origin is 0
    translate_pma = None
    rotate_pma = None

    # Check if pma is needed due to multiple snapping positions
    if len(locator_dict) > 1:
        translate_pma = controller.root.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='CogSnappingTranslate'
        )
        rotate_pma = controller.root.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='CogSnappingRotate'
        )

    for clean_name, locator_name in locator_dict.items():
        # Use condition nodes to store values
        translate_condition = controller.root.create_child(
            DependNode,
            node_type='condition',
            name='{0}_Translate_Condition'.format(locator_name)
        )
        rotate_condition = controller.root.create_child(
            DependNode,
            node_type='condition',
            name='{0}_Rotate_Condition'.format(locator_name)
        )

        # Set to 0
        for colour in 'RGB':
            translate_condition.plugs['colorIfFalse{0}'.format(colour)].set_value(0)
            rotate_condition.plugs['colorIfFalse{0}'.format(colour)].set_value(0)

        snap_plug.connect_to(translate_condition.plugs['firstTerm'])
        translate_condition.plugs['secondTerm'].set_value(counter)
        snap_plug.connect_to(rotate_condition.plugs['firstTerm'])
        rotate_condition.plugs['secondTerm'].set_value(counter)

        # Connect locator to condition nodes
        controller.scene.connectAttr('{0}.translate'.format(locator_name), translate_condition.plugs['colorIfTrue'].name)
        controller.scene.connectAttr('{0}.rotate'.format(locator_name), rotate_condition.plugs['colorIfTrue'].name)

        # Check if pma exists
        if translate_pma and rotate_pma:
            controller.scene.connectAttr('{0}.outColor'.format(translate_condition),
                           '{0}.input3D[{1}]'.format(translate_pma, counter-1))
            controller.scene.connectAttr('{0}.outColor'.format(rotate_condition),
                           '{0}.input3D[{1}]'.format(rotate_pma, counter - 1))

        else:
            controller.scene.connectAttr(translate_condition.plugs['outColor'].name, cog_zro_grp.plugs['translate'].name)
            controller.scene.connectAttr(rotate_condition.plugs['outColor'].name, cog_zro_grp.plugs['rotate'].name)

        counter += 1

    if translate_pma and rotate_pma:
        controller.scene.connectAttr('{0}.output3D'.format(translate_pma), cog_zro_grp.plugs['translate'].name)
        controller.scene.connectAttr('{0}.output3D'.format(rotate_pma), cog_zro_grp.plugs['rotate'].name)

    snap_plug.set_value(default)
    if duplicate_locators:
        return dict(
            status='warning',
            warning='Found Duplicate Locator Names:\n %s' % ', '.join(duplicate_locators)
        )
    if misnamed_locators:
        return dict(
            info='Found Invalid Locator Names:\n %s' % ', '.join(misnamed_locators)
        )

    return dict(
        info='Setup locators:\n %s' % ', '.join([x[1] for x in locator_dict.values()])
    )
