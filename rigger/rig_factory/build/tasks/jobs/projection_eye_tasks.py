import os
import logging
import colorsys
import functools
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_math.utilities as rmu
import Snowman3.rigger.rig_factory.objects as obs
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.utilities.general_utilities as gut
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode


def get_projection_eye_tasks(entity_builds, parent_task):
    root_task = BuildTask(
        parent=parent_task,
        name='Projection Eyes'
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=root_task,
            name=build.entity
        )
        for part_blueprint in gut.flatten_blueprint(build.rig_blueprint, include_self=False):
            if part_blueprint.get('klass') == 'ProjectionEye':
                BuildTask(
                    parent=entity_task,
                    name=part_blueprint.get('name'),
                    create_children_function=functools.partial(
                        generate_projection_eye_tasks,
                        part_blueprint
                    )
                )


def generate_projection_eye_tasks(part_blueprint):
    controller = cut.get_controller()
    predicted_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
        **part_blueprint
    )
    if predicted_name not in controller.named_objects:
        raise Exception('Part "%s" not found' % predicted_name)
    controller = cut.get_controller()
    part = controller.named_objects[predicted_name]

    side_prefix = rig_factory.settings_data['side_prefixes'][part.side]

    # Check if place3DTexture is using upper case P or lower case P
    locator_check = controller.scene.ls('*Place3dTexture_ExportData')
    if locator_check:
        p_prefix = 'P'
    else:
        p_prefix = 'p'

    texture_aov_locator_name = '%s_%s_AOV_%slace3dTexture_ExportData' % (
        side_prefix,
        part.root_name,
        p_prefix
    )
    texture_place_locator_name = '%s_%s_%slace3dTexture_ExportData' % (
        side_prefix,
        part.root_name,
        p_prefix
    )
    control_locator_name = '%s_%s_Control_ExportData' % (
        side_prefix,
        part.root_name
    )
    shader_task = BuildTask(
        name='Setup Eye Shader',
        function=functools.partial(
            setup_eye_shader,
            part.name,
            control_locator_name
        )
    )
    texture_position_task = BuildTask(
        name='Texture position',
        function=functools.partial(
            place_part_texture_group_node,
            part.name,
            [texture_aov_locator_name, texture_place_locator_name]
        )
    )
    dilation_task = BuildTask(
        name='Dilation',
        function=functools.partial(
            setup_dilation,
            part.name,
            control_locator_name
        )
    )
    pupil_shape_task = BuildTask(
        name='Pupil Shape',
        function=functools.partial(
            setup_pupil_shape,
            part.name
        )
    )
    eye_color_task = BuildTask(
        name='Eye Color',
        function=functools.partial(
            setup_color,
            part.name,
            control_locator_name
        )
    )
    dilation_offset_task = BuildTask(
        name='Dilation Offset',
        function=functools.partial(
            setup_dilation_offset,
            part.name
        )
    )
    aov_locator_task = BuildTask(
        name='Constrain Texture AOV Locator',
        function=functools.partial(
            constrain_texture_aov_locator,
            part.name,
            texture_aov_locator_name,
        )
    )
    place_locator_task = BuildTask(
        name='Constrain Texture Place Locator',
        function=functools.partial(
            constrain_texture_place_locator,
            part.name,
            texture_place_locator_name,
        )
    )

    return [
        shader_task,
        texture_position_task,
        dilation_task,
        pupil_shape_task,
        eye_color_task,
        dilation_offset_task,
        aov_locator_task,
        place_locator_task
    ]

def set_part_rig_data(part_name, key, value):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    if not value:
        return dict(
            status='warning',
            warning='Unable invalid geometry names: %s' % value
        )
    if key not in part.data_setters:
        return dict(
            status='warning',
            warning='Unable to find data setter for %s.%s existing setters: %s' % (part_name, key, part.data_setters.keys())
        )
    part.data_setters[key](value)


def setup_eye_shader(part_name, control_locator_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    side_prefix = rig_factory.settings_data['side_prefixes'][part.side]

    # Environment Variables
    prj_name = os.getenv('PROJECT_CODE')
    asset_type = os.getenv('TT_ASSTYPE')

    asset_texture_path = 'Y:/{}/assets/type/{}/Eyes/work/elems/textures/'.format(prj_name, asset_type)
    irig_texture_path = '{}/static/eye_textures/'.format(os.path.dirname(rig_factory.__file__.replace('\\', '/')))
    if os.path.exists(asset_texture_path):
        texture_path = asset_texture_path
    elif os.path.exists(irig_texture_path):
        texture_path = irig_texture_path
    else:
        return dict(
            status='warning',
            warning='Path not found: %s' % irig_texture_path
        )

    # Check for Export Data locators from Asset Department
    if control_locator_name not in controller.named_objects:
        return dict(
            status='warning',
            warning='Locator not found: %s' % control_locator_name
        )
    control_locator = controller.named_objects[control_locator_name]

    # If this exists, then build THE NEW PUPIL SYSTEM WITH TEXTURE SHAPES ON PUPILS
    if control_locator.plugs.exists('eyeShapeSwitch'):

        # create place2d texture
        eye_place2d_texture = part.create_child(
            DependNode,
            node_type='place2dTexture',
            name='{}_{}_place2dTexture'.format(side_prefix, part.root_name)
        )
        eye_place2d_texture.plugs['repeatUV'].set_value([1.65, 1.65])
        eye_place2d_texture.plugs['offset'].set_value([-0.325, -0.325])
        eye_place2d_texture.plugs['wrapU'].set_value(0)
        eye_place2d_texture.plugs['wrapV'].set_value(0)
        eye_place2d_texture.plugs['stagger'].set_value(1)

        # create files with eye path
        eye_types = ['Human', 'Snake', 'Heart', 'Star']
        eye_tx_files = []
        eyes_conditions = []
        for eye in eye_types:
            tx_file = part.create_child(
                DependNode,
                node_type='file',
                name='{}_{}_{}_UV_file'.format(side_prefix, part.root_name, eye)
            )
            tx_file.plugs['defaultColor'].set_value([0.0, 0.0, 0.0])
            tx_file.plugs['fileTextureName'].set_value(
                texture_path + 'Eyes_VTwo_{}_UV_1K_raw.tif'.format(eye))
            tx_file.plugs['colorSpace'].set_value('raw')

            # connect to place2dTexture
            eye_place2d_texture.plugs['outUV'].connect_to(tx_file.plugs['uvCoord'])
            eye_place2d_texture.plugs['outUvFilterSize'].connect_to(tx_file.plugs['uvFilterSize'])
            shd_attributes = ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", "stagger",
                              "wrapU", "wrapV", "repeatUV", "vertexUvOne", "vertexUvTwo", "vertexUvThree",
                              "vertexCameraOne", "noiseUV", "offset", "rotateUV"]
            for at in shd_attributes:
                eye_place2d_texture.plugs[at].connect_to(tx_file.plugs[at])

            # create conditions for each file
            eye_condition = part.create_child(
                DependNode,
                node_type='condition',
                name='{}_{}_{}_UV_condition'.format(side_prefix, part.root_name, eye)
            )
            tx_file.plugs['outColor'].connect_to(eye_condition.plugs['colorIfTrue'])
            eye_condition.plugs['secondTerm'].set_value(eye_types.index(eye))
            control_locator.plugs['eyeShapeSwitch'].connect_to(eye_condition.plugs['firstTerm'])

            eyes_conditions.append(eye_condition)
            eye_tx_files.append(tx_file)

        # condition nodes connections
        eyes_conditions[3].plugs['outColor'].connect_to(eyes_conditions[2].plugs['colorIfFalse'])
        eyes_conditions[2].plugs['outColor'].connect_to(eyes_conditions[1].plugs['colorIfFalse'])
        eyes_conditions[1].plugs['outColor'].connect_to(eyes_conditions[0].plugs['colorIfFalse'])

        # create floatMaths for dilation on pupils
        dil_floatmaths = []
        for n in ['Dilation_Corr', 'SetRange', 'RemapVal_Div', 'Iris_RemapVal_Mult', 'Iris_RemapVal_Min']:
            dil_math = part.create_child(
                DependNode,
                node_type='floatMath',
                name='{}_{}_{}_floatMath'.format(side_prefix, part.root_name, n)
            )
            dil_floatmaths.append(dil_math)

        control_locator.plugs['dilation'].connect_to(dil_floatmaths[0].plugs['floatA'])
        dil_floatmaths[0].plugs['floatB'].set_value(0.85)
        dil_floatmaths[0].plugs['operation'].set_value(2)

        dil_floatmaths[0].plugs['outFloat'].connect_to(dil_floatmaths[1].plugs['floatB'])
        dil_floatmaths[1].plugs['operation'].set_value(1)
        dil_floatmaths[1].plugs['outFloat'].connect_to(dil_floatmaths[2].plugs['floatB'])
        dil_floatmaths[2].plugs['operation'].set_value(3)
        dil_floatmaths[2].plugs['outFloat'].connect_to(dil_floatmaths[3].plugs['floatB'])
        eyes_conditions[0].plugs['outColorG'].connect_to(dil_floatmaths[3].plugs['floatA'])
        dil_floatmaths[3].plugs['operation'].set_value(2)
        dil_floatmaths[3].plugs['outFloat'].connect_to(dil_floatmaths[4].plugs['floatB'])
        dil_floatmaths[4].plugs['operation'].set_value(4)

        # This is commented out for now
        # If in the event we need to include control over the Colour of the eyes and provide animation with that control
        # this can then be uncommented
        # Purpose: So that each of the colour entry that make up the iris ramp can be controlled by the user
        part.ramp_node.plugs['colorEntryList'].element(3).child(1).connect_to(
            part.ramp_node.plugs['colorEntryList'].element(1).child(1)
        )

        # Since the iris ramp that follows the dilation was removed,
        # we are setting a default value for this colour entry
        part.ramp_node.plugs['colorEntryList'].element(3).child(0).set_value(0.175)

        # create pupil color ramp
        pupil_color = part.create_child(
            DependNode,
            node_type='ramp',
            name='{}_{}_pupil_ramp'.format(side_prefix, part.root_name)
        )
        pupil_color.plugs['interpolation'].set_value(0)
        dil_floatmaths[4].plugs['outFloat'].connect_to(pupil_color.plugs['vCoord'])
        eyes_conditions[0].plugs['outColorR'].connect_to(pupil_color.plugs['uCoord'])
        pupil_color.plugs['colorEntryList'].element(0).child(1).set_value([1.0, 1.0, 1.0])
        pupil_color.plugs['colorEntryList'].element(0).child(0).set_value(0.98)
        pupil_color.plugs['colorEntryList'].element(1).child(1).set_value([0.0, 0.0, 0.0])

        # connect sclera mask
        sclera_layered_tx = part.create_child(
            DependNode,
            node_type='layeredTexture',
            name='{}_{}_sclera_layeredTx'.format(side_prefix, part.root_name)
        )
        sclera_mask_ramp = part.create_child(
            DependNode,
            node_type='ramp',
            name='{}_{}_sclera_mask'.format(side_prefix, part.root_name)
        )
        sclera_mask_ramp.plugs['type'].set_value(4)
        sclera_mask_ramp.plugs['interpolation'].set_value(0)
        sclera_mask_ramp.plugs['colorEntryList'].element(0).child(1).set_value([0.0, 0.0, 0.0])
        sclera_mask_ramp.plugs['colorEntryList'].element(0).child(0).set_value(0.0)
        sclera_mask_ramp.plugs['colorEntryList'].element(1).child(1).set_value([1.0, 1.0, 1.0])
        sclera_mask_ramp.plugs['colorEntryList'].element(1).child(0).set_value(0.31)

        sclera_mask_ramp.plugs['outColorR'].connect_to(sclera_layered_tx.plugs['inputs'].element(0).child(1))
        sclera_layered_tx.plugs['inputs'].element(0).child(2).set_value(1)

        part.ramp_node.plugs['colorEntryList'].element(0).child(1).connect_to(
            sclera_layered_tx.plugs['inputs'].element(0).child(0)
        )

        sclera_layered_tx.plugs['inputs'].element(1).child(0).set_value([0.0, 0.0, 0.0])
        sclera_layered_tx.plugs['inputs'].element(1).child(2).set_value(1)
        pupil_color.plugs['outAlpha'].connect_to(sclera_layered_tx.plugs['inputs'].element(1).child(1))

        part.ramp_node.plugs['outColor'].connect_to(sclera_layered_tx.plugs['inputs'].element(2).child(0))
        sclera_layered_tx.plugs['inputs'].element(2).child(2).set_value(1)

        # connect layered texture outcolor to projection image
        sclera_layered_tx.plugs['outColor'].connect_to(part.projection_node.plugs['image'])

        # make attribute on controller and connect to locator
        pupil_shape_plug = part.handles[1].create_plug(
            'PupilShape',
            at='enum',
            keyable=True,
            en="Human:Snake:Heart:Star",
            dv=0
        )
        pupil_shape_plug.connect_to(control_locator.plugs['eyeShapeSwitch'])
        part.get_root().add_plugs(pupil_shape_plug)

    else:  # KEEP OLD PUPIL SYSTEM that has no pupil shapes and just a simple ramp for the eyes

        set_range = part.create_child(
            DependNode,
            node_type='setRange',
            segment_name='SetRange'
        )

        part.handles[1].plugs['InnerDilation'].connect_to(set_range.plugs['valueX'])
        inner_dilation_clamp = part.create_child(
            DependNode,
            node_type='clamp',
            segment_name='InnerDilation'
        )

        inner_dilation_add = part.create_child(
            DependNode,
            node_type='addDoubleLinear',
            segment_name='InnerDilation'
        )

        set_range.plugs['maxX'].set_value(0.260)
        set_range.plugs['oldMaxX'].set_value(1.0)
        set_range.plugs['outValueX'].connect_to(inner_dilation_clamp.plugs['inputR'])
        inner_dilation_clamp.plugs['outputR'].connect_to(inner_dilation_add.plugs['input1'])
        inner_dilation_add.plugs['input2'].set_value(0.02)
        inner_dilation_clamp.plugs['minR'].set_value(0.00)
        inner_dilation_clamp.plugs['maxR'].set_value(0.65)

        inner_dilation_clamp.plugs['outputR'].connect_to(
            part.ramp_node.plugs['colorEntryList'].element(1).child(0))
        inner_dilation_add.plugs['output'].connect_to(part.ramp_node.plugs['colorEntryList'].element(3).child(0))

        # connect iris ramp to projection image
        part.ramp_node.plugs['outColor'].connect_to(part.projection_node.plugs['image'])


def constrain_texture_place_locator(part_name, texture_place_locator_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    texture_place_locator = controller.named_objects.get(texture_place_locator_name)
    if not texture_place_locator:
        return dict(
            status='warning',
            warning='Locator not found: %s' % texture_place_locator
        )

    controller.scene.parentConstraint(
        part.place_texture_plx,
        texture_place_locator,
    )
    controller.scene.scaleConstraint(
        part.place_texture_plx,
        texture_place_locator
    )


def constrain_texture_aov_locator(part_name, texture_aov_locator_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    texture_aov_locator = controller.named_objects.get(texture_aov_locator_name)
    if not texture_aov_locator:
        return dict(
            status='info',
            info='Node not found: %s' % texture_aov_locator_name
        )

    controller.scene.parentConstraint(
        part.place_texture_plx,
        texture_aov_locator,
    )
    controller.scene.scaleConstraint(
        part.place_texture_plx,
        texture_aov_locator
    )


def setup_color(part_name, locator_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    if locator_name not in controller.named_objects:
        return dict(
            status='warning',
            warning='Locator not found: %s' % locator_name
        )
    control_locator = controller.named_objects[locator_name]

    hsv_color = [0.63, 0.8, 1.0]
    missing_plugs = []
    for i, attr in enumerate(['primHue', 'primSat', 'primVal']):
        if control_locator.plugs.exists(attr):
            hsv_color[i] = control_locator.plugs[attr].get_value()
        else:
            missing_plugs.append('%s.%s' % (locator_name, attr))

    hue, saturation, value = hsv_color

    # primVal is actually gamma not brightness, convert it to brightness
    pre_processed_color_value = value
    if value:
        value = rmu.gamma_correct(1.0, value)
    else:
        logging.getLogger('rig_build').info('primVal attr for %s is currently set to 0.0' % locator_name)
    # it's should also get multiplied by 0.4 (comes from eye shader netwrok)
    value = value * 0.4

    hsv_color = [hue, saturation, value]

    rgb_color = list(colorsys.hsv_to_rgb(*hsv_color))

    # a little darker color for outer iris
    inner_iris_col = [x * 0.6 for x in rgb_color]
    outer_iris_color = [x * 1.2 for x in rgb_color]
    part.ramp_node.plugs['colorEntryList'].element(2).child(1).set_value(inner_iris_col)

    if part.sclera_color:
        part.ramp_node.plugs['colorEntryList'].element(2).child(1).set_value([0.77, 0.77, 0.77])
        # if control_locator.plugs.exists('redScleraWhite'):
        control_locator.plugs['redScleraWhite'].connect_to(part.outer_color_correct.plugs['inColorR'])
        control_locator.plugs['greenScleraWhite'].connect_to(part.outer_color_correct.plugs['inColorG'])
        control_locator.plugs['blueScleraWhite'].connect_to(part.outer_color_correct.plugs['inColorB'])
        # part.inner_color_correct.plugs['colorEntryList'].set_value(6)
    else:
        part.ramp_node.plugs['colorEntryList'].element(3).child(1).set_value(outer_iris_color)

    feedback_info = 'HSV color: %s\nRGB color: %s\nSclera color: %s\ninner iris color: %s\nouter iris color: %s\npre_processed_color_value = %s\nPost Processed color value = %s' % (
            hsv_color,
            rgb_color,
            part.sclera_color,
            inner_iris_col,
            outer_iris_color,
            pre_processed_color_value,
            value

        )
    if missing_plugs:
        feedback_info += '\nPlugs missing: %s' % ', '.join(missing_plugs)
    return dict(
        info=feedback_info
    )


def setup_pupil_shape(part_name):
    value = 0
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    if part.handles[1].plugs.exists('PupilShape'):
        part.handles[1].plugs['PupilShape'].set_value(value)
        controller.scene.addAttr(
            part.handles[1].plugs['PupilShape'].name,
            e=True,
            dv=part.handles[1].plugs['PupilShape'].get_value()
        )


def setup_dilation(part_name, locator_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    control_locator = controller.named_objects.get(locator_name)
    if not control_locator:
        return dict(
            status='warning',
            warning='Unable to setup dilation. Locator not found: %s' % control_locator
        )
    dilation = 0.18
    missing_dilation_plug = False
    if control_locator.plugs.exists('dilation'):
        dilation = control_locator.plugs['dilation'].get_value()
    else:
        missing_dilation_plug = True

    part.handles[1].plugs['InnerDilation'].set_value(dilation)
    controller.scene.addAttr(
        part.handles[1].plugs['InnerDilation'].name,
        e=True,
        dv=part.handles[1].plugs['InnerDilation'].get_value()
    )
    part.handles[1].plugs['InnerDilation'].connect_to(control_locator.plugs['dilation'])

    if missing_dilation_plug:
        return dict(
            status='warning',
            warning='plug missing: %s.dilation' % locator_name
        )


def setup_dilation_offset(part_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    if part.iris_dilation_offset is None:
        return dict(
            info='Unable to set dilation offset. %s.iris_dilation_offset is None' % part.name
        )
    part.iris_dilation_offset.plugs['floatB'].set_value(
        0.175 - part.iris_dilation_offset.plugs['floatA'].get_value()
    )


def place_part_texture_group_node(part_name, locator_names):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]

    for locator_name in locator_names:
        if controller.scene.objExists(locator_name):
            matrix = controller.scene.xform(locator_name, ws=True, m=True, q=True)
            part.place_texture_group_node.set_matrix(Matrix(matrix))
            return
    return dict(
        status='warning',
        warning='Locators not found: %s' % locator_names
    )

