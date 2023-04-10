# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman3.riggers.utilities.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
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
            ['HandFollowSpace', (6, 9.5, 0), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, 1]], 0.8, False, None],
            ['Upperarm', (0, 0, 0), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]], 1.25, True, None],
            ['Forearm', (26.94, 0, -2.97), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]], 1.25, True, None],
            ['ForearmEnd', (52.64, 0, 0), [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]], 1.25, True, None],
            ['WristEnd', (59, 0, 0), [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]], 0.7, False, 'ForearmEnd'],
            ['IkElbow', (26.94, 0, -35), [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 1.25, False, None]
        ]
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                side=self.side,
                parent_part_name=self.part_name,
                position=p[1],
                size=p[4],
                vector_handle_positions=self.proportionalize_vector_handle_positions(p[2], p[4]),
                orientation=p[3],
                match_orienter=p[6],
                has_vector_handles=p[5]
            )
            placers.append(placer_creator.create_placer())
        return placers



    def create_controls(self):
        ctrl_creators = [
            ControlCreator(
                name='FkUpperarm',
                shape="body_section_tube",
                color=self.colors[0],
                size=[25, 6.5, 6.5],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='FkForearm',
                shape="body_section_tube",
                color=self.colors[0],
                size=[25, 6.5, 6.5],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='FkHand',
                shape="body_section_tube",
                color=self.colors[0],
                size=[6.5, 4, 8],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkHand',
                shape="cylinder",
                color=self.colors[0],
                size=[0.7, 7, 7],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkElbow',
                shape="sphere",
                color=self.colors[0],
                size=[2, 2, 2],
                side=self.side
            ),
            ControlCreator(
                name='Shoulder',
                shape='tag_hexagon',
                color=self.colors[0],
                size=[6, 6, 6],
                up_direction = [0, 1, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkHandFollow',
                shape='tetrahedron',
                color=self.colors[1],
                size=[1.5, 1.5, 1.5],
                side=self.side
            ),
            ControlCreator(
                name='Elbow',
                shape='circle',
                color=self.colors[0],
                up_direction = [1, 0, 0],
                size=4.5,
                side=self.side
            )
        ]
        for limb_segment in ('Upperarm', 'Forearm'):
            for name_tag in ('Start', 'Mid', 'End'):
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{limb_segment}Bend{name_tag}',
                        shape='circle',
                        color=self.colors[1],
                        up_direction=[1, 0, 0],
                        size=3.5,
                        side=self.side
                    )
                )
            for i in range(5):
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{limb_segment}Tweak{i+1}',
                        shape='square',
                        color=self.colors[2],
                        up_direction=[1, 0, 0],
                        size=2,
                        side=self.side
                    )
                )
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls



    def get_connection_pairs(self):
        return (
            ('Forearm', 'Upperarm'),
            ('ForearmEnd', 'Forearm'),
            ('WristEnd', 'ForearmEnd'),
            ('IkElbow', 'Forearm')
        )



    def get_vector_handle_attachments(self):
        return{
            'Upperarm': ['Forearm', 'IkElbow'],
            'Forearm': ['ForearmEnd', 'IkElbow'],
            'ForearmEnd': ['WristEnd', None]
        }




    def build_rig_part(self, part):
        rig_part_container, connector, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)

        limb_rig = LimbRig(
            limb_name=part.name,
            side=part.side,
            prefab='plantigrade',
            segment_names=['Upperarm', 'Forearm', 'Hand'],
            socket_name='Shoulder',
            pv_name='Elbow',
            jnt_positions=[pm.xform(orienters[p], q=1, worldSpace=1, rotatePivot=1) for p in (
                'Upperarm', 'Forearm', 'ForearmEnd', 'WristEnd')],
            pv_position=pm.xform(orienters['IkElbow'], q=1, worldSpace=1, rotatePivot=1)
        )

        # ...Conform LimbRig's PV ctrl orientation to that of PV orienter
        pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
        world_pos = pm.xform(orienters['IkElbow'], q=1, worldSpace=1, rotatePivot=1)
        pm.delete(pm.orientConstraint(orienters['IkElbow'], pv_ctrl_buffer))

        # ...Move contents of limb rig into biped_arm rig module's groups
        [child.setParent(transform_grp) for child in limb_rig.grps['transform'].getChildren()]
        [child.setParent(no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]

        #...Migrate Rig Scale attr over to new rig group
        rig_scale_attr_string = 'RigScale'
        gen.install_uniform_scale_attr(rig_part_container, rig_scale_attr_string)
        for plug in pm.listConnections(f'{limb_rig.grps["root"]}.{rig_scale_attr_string}', destination=1, plugs=1):
            pm.connectAttr(f'{rig_part_container}.{rig_scale_attr_string}', plug, force=1)
        for plug in pm.listConnections(f'{limb_rig.grps["root"]}.{rig_scale_attr_string}', source=1, plugs=1):
            pm.connectAttr(plug, f'{rig_part_container}.{rig_scale_attr_string}', force=1)
        pm.delete(limb_rig.grps['root'])

        ctrl_pairs = [('FkUpperarm', limb_rig.fk_ctrls[0]),
                      ('FkForearm', limb_rig.fk_ctrls[1]),
                      ('FkHand', limb_rig.fk_ctrls[2]),
                      ('IkHand', limb_rig.ctrls['ik_extrem']),
                      ('IkElbow', limb_rig.ctrls['ik_pv']),
                      ('Shoulder', limb_rig.ctrls['socket']),
                      ('Elbow', limb_rig.pin_ctrls[0])]
        for i, limb_segment in enumerate(('Upperarm', 'Forearm')):
            for j, name_tag in enumerate(('Start', 'Mid', 'End')):
                ctrl_pairs.append((f'{limb_segment}Bend{name_tag}', limb_rig.segments[i].bend_ctrls[j]))
            for j, ctrl_list in enumerate(limb_rig.tweak_ctrls[0]):
                ctrl_pairs.append((f'{limb_segment}Tweak{j+1}', limb_rig.tweak_ctrls[i][j]))

        for ctrl_str, limb_setup_ctrl in ctrl_pairs:
            scene_ctrl = scene_ctrls[ctrl_str]
            scene_ctrl_name = gen.get_clean_name(str(scene_ctrl))
            pm.rename(scene_ctrl, f'{scene_ctrl_name}_TEMP')
            pm.rename(limb_setup_ctrl, scene_ctrl_name)
            scene_ctrl.setParent(limb_setup_ctrl.getParent())
            gen.zero_out(scene_ctrl)
            pm.matchTransform(scene_ctrl, limb_setup_ctrl)
            gen.copy_shapes(source_obj=scene_ctrl, destination_obj=limb_setup_ctrl, delete_existing_shapes=True)
            scene_ctrls[ctrl_str] = limb_setup_ctrl

        ik_hand_follow_ctrl_buffer = gen.buffer_obj(scene_ctrls['IkHandFollow'], parent=transform_grp)
        pm.matchTransform(ik_hand_follow_ctrl_buffer, orienters['HandFollowSpace'])

        pm.select(clear=1)
        return rig_part_container
