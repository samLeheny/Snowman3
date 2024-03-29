# Title: biped_neck.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
import Snowman3.utilities.rig_utils as rig
import Snowman3.utilities.node_utils as nodes

import Snowman3.rigger.utilities.placer_utils as placer_utils
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator
OrienterManager = placer_utils.OrienterManager
import Snowman3.rigger.parts.class_PartConstructor as class_PartConstructor
PartConstructor = class_PartConstructor.PartConstructor
import Snowman3.rigger.utilities.control_utils as control_utils
SceneControlManager = control_utils.SceneControlManager
import Snowman3.dictionaries.colorCode as color_code
import Snowman3.dictionaries.nameConventions as nameConventions
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
nom = nameConventions.create_dict()
###########################
###########################


class BespokePartConstructor(PartConstructor):

    def __init__(
        self,
        part_name: str,
        side: str = None,
    ):
        super().__init__(part_name, side)

        
    def create_placers(self):
        data_packs = [
            ['Neck', [0, 0, 0], [[0, 1, 0], [0, 0, 1]], [[0, 1, 0], [0, 0, 1]], 1.25, True],
            ['Head', [0, 12.5, 1.8], [[0, 1, 0], [0, 0, 1]], [[0, 1, 0], [0, 0, 1]], 1.25, True],
            ['NeckSettings', [10, 0, 0], [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1, False]
        ]
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                side=self.side,
                part_name=self.part_name,
                position=p[1],
                size=p[4],
                vector_handle_positions=self.proportionalize_vector_handle_positions(p[2], p[4]),
                orientation=p[3],
                has_vector_handles=p[5]
            )
            placers.append(placer_creator.create_placer())
        return placers


    def create_controls(self):
        ctrls = [
            self.initialize_ctrl(
                name='Neck',
                shape='circle',
                color=color_code['M2'],
                size=7,
                side=self.side
            ),
            self.initialize_ctrl(
                name='Head',
                shape='cylinder',
                color=color_code['M2'],
                size=[9, 0.65, 9],
                side=self.side
            ),
            self.initialize_ctrl(
                name='NeckSettings',
                shape='gear',
                color=color_code['settings'],
                size=0.75,
                locks={'v': 1, 't': [1, 1, 1], 'r': [1, 1, 1], 's': [1, 1, 1]},
                side=self.side
            ),
            self.initialize_ctrl(
                name='NeckBend',
                shape='circle',
                color=color_code['M2'],
                size=6,
                side=self.side
            )
        ]
        for i in range(5):
            ctrls.append(
                self.initialize_ctrl(
                    name=f'NeckTweak{i+1}',
                    shape='square',
                    color=self.colors[3],
                    up_direction=[1, 0, 0],
                    size=4,
                    side=self.side
                )
            )
        return ctrls


    def get_connection_pairs(self):
        return (
            ('Head', 'Neck'),
            ('Neck', 'NeckSettings')
        )


    def create_part_nodes_list(self):
        part_nodes = []
        for name in ('Neck', 'Head'):
            part_nodes.append(name)
        return part_nodes


    def get_vector_handle_attachments(self):
        return{}



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        jnt_resolution = 5

        pairs = (('Neck', 'Neck'), ('Head', 'Head'), ('NeckSettings', 'NeckSettings'))
        [gen.match_pos_ori(scene_ctrls[pair[0]], orienters[pair[1]]) for pair in pairs]

        temp_nodes_to_delete = []

        scene_ctrls['NeckSettings'].setParent(transform_grp)

        scene_ctrls['Neck'].setParent(transform_grp)
        gen.buffer_obj(scene_ctrls['Neck'])

        up_obj = pm.spaceLocator(name=f'neckRibbon_up_{nom.locator}')
        up_obj.setParent(scene_ctrls['Neck'])
        gen.zero_out(up_obj)
        up_obj.tz.set(gen.distance_between(obj_1=scene_ctrls['Neck'], obj_2=scene_ctrls['Head']))
        up_obj.setParent(transform_grp)
        temp_nodes_to_delete.append(up_obj)

        scene_ctrls['Head'].setParent(scene_ctrls['Neck'])
        gen.buffer_obj(scene_ctrls['Head'])

        # ...Bind joints -----------------------------------------------------------------------------------------------
        jnts = {'Head': rig.joint(name='Head', joint_type=nom.bindJnt, radius=1.25, side=part.side)}

        jnts['Head'].setParent(scene_ctrls['Head'])
        gen.zero_out(jnts['Head'])

        # ...
        temp_neck_aimer = pm.spaceLocator(name="neck_aimer_TEMP")
        pm.delete(pm.pointConstraint(scene_ctrls['Neck'], temp_neck_aimer))
        pm.delete(pm.aimConstraint(scene_ctrls['Head'], temp_neck_aimer, worldUpType='object', worldUpObject=up_obj,
                                   aimVector=(0, 1, 0), upVector=(0, 0, 1)))
        temp_nodes_to_delete.append(temp_neck_aimer)

        stretch_socket = pm.shadingNode('transform', name='stretch_socket_start', au=1)
        stretch_socket.setParent(temp_neck_aimer)
        gen.zero_out(stretch_socket)
        stretch_socket.setParent(scene_ctrls['Neck'])

        stretch_out_socket = pm.shadingNode('transform', name='stretch_socket_end', au=1)
        stretch_out_socket.setParent(scene_ctrls['Head'])
        gen.zero_out(stretch_out_socket)
        pm.delete(pm.orientConstraint(temp_neck_aimer, stretch_out_socket))

        # ...Roll joint system -----------------------------------------------------------------------------------------
        pm.addAttr(scene_ctrls['NeckSettings'], longName='NeckLen', attributeType='float', minValue=0.001,
                   defaultValue=1, keyable=1)
        # ...Rollers
        neck_length = gen.distance_between(obj_1=orienters['Neck'], obj_2=orienters['Head'])
        bend_ctrl_size = neck_length * 0.5
        neck_roller = rig.limb_rollers(start_node=stretch_socket,
                                       end_node=stretch_out_socket,
                                       roller_name='neck',
                                       roll_axis=(0, 1, 0),
                                       up_axis=(0, 0, 1),
                                       ctrl_color=color_code['M'],
                                       parent=no_transform_grp,
                                       side=part.side,
                                       ctrl_size=bend_ctrl_size,
                                       populate_ctrls=[0, 1, 0],
                                       world_up_obj=stretch_socket,
                                       )
        # ...Ribbon
        ribbon_up_vector = (0, 0, -1)
        if part.side == nom.rightSideTag:
            ribbon_up_vector = (0, 0, 1)

        # ...Create ribbons
        neck_ribbon = rig.ribbon_plane(name='neck', start_obj=stretch_socket, end_obj=stretch_out_socket, up_obj=up_obj,
                                       density=jnt_resolution, side=part.side, up_vector=ribbon_up_vector)
        neck_ribbon['nurbsStrip'].visibility.set(0, lock=1)
        neck_ribbon["nurbsStrip"].setParent(no_transform_grp)
        neck_ribbon["nurbsStrip"].scale.set(1, 1, 1)

        # ...Skin ribbons
        pm.select(neck_roller['jnts'][0], neck_roller['jnts'][1], neck_roller['jnts'][2], replace=1)
        pm.select(neck_ribbon["nurbsStrip"], add=1)
        pm.skinCluster(maximumInfluences=1, toSelectedBones=1)

        # ...Tweak ctrls
        neck_length_node = nodes.multDoubleLinear(input1=f'{scene_ctrls["NeckSettings"]}.NeckLen',
                                                  input2=gen.distance_between(obj_1=scene_ctrls["Neck"],
                                                                              obj_2=scene_ctrls["Head"]))

        # --------------------------------------------------------------------------------------------------------------
        pm.addAttr(scene_ctrls['NeckSettings'], longName='Volume', attributeType='float', minValue=0, maxValue=10,
                   defaultValue=0, keyable=1)

        neck_tweak_ctrls = rig.ribbon_tweak_ctrls(
            ribbon=neck_ribbon['nurbsStrip'], ctrl_name='Neck', length_ends=(scene_ctrls['Neck'], scene_ctrls['Head']),
            length_attr=neck_length_node.output, attr_ctrl=scene_ctrls['NeckSettings'], side=part.side,
            ctrl_color=color_code['M'], ctrl_resolution=jnt_resolution, parent=no_transform_grp,
            ctrl_size=neck_length * 0.4, scale_node=rig_part_container)

        ctrl_pairs = [('NeckBend', neck_roller['ctrls'][1])]
        for i, tweak_ctrl in enumerate(neck_tweak_ctrls):
            ctrl_pairs.append((f'NeckTweak{i+1}', tweak_ctrl))

        for ctrl_str, ribbon_setup_ctrl in ctrl_pairs:
            scene_ctrl = scene_ctrls[ctrl_str]
            scene_ctrl_name = gen.get_clean_name(str(scene_ctrl))
            pm.rename(scene_ctrl, f'{scene_ctrl_name}_TEMP')
            pm.rename(ribbon_setup_ctrl, scene_ctrl_name)
            scene_ctrl.setParent(ribbon_setup_ctrl.getParent())
            gen.zero_out(scene_ctrl)
            gen.match_pos_ori(scene_ctrl, ribbon_setup_ctrl)
            gen.copy_shapes(source_obj=scene_ctrl, destination_obj=ribbon_setup_ctrl, delete_existing_shapes=True)
            scene_ctrls[ctrl_str] = ribbon_setup_ctrl

        rig_part_container.scale.connect(scene_ctrls['NeckBend'].getParent().scale)

        # Adjustable biped_neck length ---------------------------------------------------------------------------------
        neck_len_start_node = pm.shadingNode('transform', name='neck_length_start', au=1)
        neck_len_end_node = pm.shadingNode('transform', name='neck_length_end', au=1)
        neck_len_end_node.setParent(neck_len_start_node)

        pm.matchTransform(neck_len_start_node, scene_ctrls['Neck'])
        pm.delete(pm.aimConstraint(scene_ctrls['Head'], neck_len_start_node, worldUpType='object',
                                   worldUpObject=up_obj, aimVector=(0, 1, 0), upVector=(0, 0, 1)))
        pm.matchTransform(neck_len_end_node, scene_ctrls['Head'])

        neck_length_node.output.connect(neck_len_end_node.ty)
        neck_len_start_node.setParent(scene_ctrls['Neck'])

        scene_ctrls['Head'].getParent().setParent(neck_len_end_node)

        [gen.zero_offsetParentMatrix(ctrl) for ctrl in scene_ctrls.values()]

        for key, node in (('Neck', neck_roller['jnts'][0]),
                          ('Head', jnts['Head'])):
            self.part_nodes[key] = node.nodeName()

        pm.delete(temp_nodes_to_delete)

        return rig_part_container
