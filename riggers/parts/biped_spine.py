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
OrienterManager = placer_utils.OrienterManager

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman2.riggers.modules.biped_spine.build.subModules.fk_ribbon as build_fk_ribbon
importlib.reload(build_fk_ribbon)

import Snowman2.riggers.modules.biped_spine.build.subModules.ik_translate_ribbon \
    as build_ik_translate_ribbon
importlib.reload(build_ik_translate_ribbon)

import Snowman2.riggers.modules.biped_spine.build.subModules.ik_rotate_ribbon \
    as build_ik_rotate_ribbon
importlib.reload(build_ik_rotate_ribbon)

import Snowman2.riggers.modules.biped_spine.build.subModules.ik_output_ribbon as build_ik_output_ribbon
importlib.reload(build_ik_output_ribbon)

import Snowman2.riggers.modules.biped_spine.setup.subModules.waist_ribbon as waist_ribbon
importlib.reload(waist_ribbon)
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
        segment_count: int = 6
    ):
        super().__init__(part_name, side)
        self.segment_count = segment_count
        self.jnt_count = segment_count + 1


    def create_placers(self):
        spine_length = 42.0
        spine_seg_length = spine_length / self.segment_count
        placers = []
        for i in range(self.jnt_count):
            n = i + 1
            has_vector_handles = True
            size = 1.25
            if i == range(self.jnt_count):
                has_vector_handles = False
                size = 0.8
            placer_creator = PlacerCreator(
                name=f'Spine{str(n)}',
                side=self.side,
                parent_part_name=self.part_name,
                position=(0, spine_seg_length * i, 0),
                size=size,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 1, 0], [0, 0, 1]], size),
                orientation=[[0, 1, 0], [0, 0, 1]],
                has_vector_handles=has_vector_handles
            )
            placers.append(placer_creator.create_placer())
        return placers



    def get_vector_handle_attachments(self):
        attachments = {}
        for i in range(self.segment_count):
            attachments[f'Spine{i+1}'] = [f'Spine{i+2}', None]
        return attachments



    def create_controls(self):
        ctrl_creators = []
        ik_ctrl_creators = [
            ControlCreator(
                name = 'IkChest',
                shape = 'circle',
                color = color_code[self.side],
                size = 14
            ),
            ControlCreator(
                name='IkWaist',
                shape='circle',
                color=color_code[self.side],
                size=14
            ),
            ControlCreator(
                name='IkPelvis',
                shape='circle',
                color=color_code[self.side],
                size=14
            )
        ]
        ctrl_creators += ik_ctrl_creators
        fk_ctrl_creators = [
            ControlCreator(
                name='FkSpine1',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                up_direction = [0, -1, 0]
            ),
            ControlCreator(
                name='FkSpine2',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                up_direction = [0, -1, 0]
            ),
            ControlCreator(
                name='FkSpine3',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                up_direction = [0, -1, 0]
            ),
            ControlCreator(
                name='FkHips',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
            )
        ]
        ctrl_creators += fk_ctrl_creators
        tweak_ctrl_creators = [
            ControlCreator(
                name=f'SpineTweak{i+1}',
                shape='square',
                color=color_code['M3'],
                size=12,
            ) for i in range(self.segment_count+1)
        ]
        ctrl_creators += tweak_ctrl_creators
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls



    def get_connection_pairs(self):
        pairs = []
        for i in range(self.segment_count):
            n = i + 1
            pairs.append(
                (f'Spine{str(n+1)}', f'Spine{str(n)}')
            )
        return tuple(pairs)



    def find_mid_value(self, count):
        even_count = False
        if count % 2 == 0:
            even_count = True
        if even_count:
            return int(count / 2), int((count / 2) + 1)
        else:
            return int(((count - 1) / 2) + 1)


    def position_fk_ctrls(self, part, fk_ctrls, orienters):
        segment_lengths = [gen.distance_between(orienters[i], orienters[i + 1]) for i in range(len(orienters) - 1)]
        total_spine_length = sum(segment_lengths)
        top_fk_ctrl_position = 0.855
        fk_ctrl_count = 3
        fk_ctrl_placement_mults = [(top_fk_ctrl_position / fk_ctrl_count) * i for i in range(1, (fk_ctrl_count + 1))]
        fk_ctrl_placement = [total_spine_length * mult for mult in fk_ctrl_placement_mults]
        spine_length_increments = []
        for i, length in enumerate(segment_lengths):
            if i == 0:
                spine_length_increments.append(length)
            else:
                spine_length_increments.append(spine_length_increments[i - 1] + length)
        pairs = []
        pair_values = []
        for placement in fk_ctrl_placement:
            for i, increment in enumerate(spine_length_increments):
                if increment > placement:
                    pairs.append((i, i + 1))
                    pair_values.append((spine_length_increments[i - 1], increment))
                    break
        distance_weights = []
        for ctrl_placement, pair_value in zip(fk_ctrl_placement, pair_values):
            distances = [abs(abs(ctrl_placement) - abs(value)) for value in pair_value]
            distance_sum = sum(distances)
            distance_weights.append([dist / distance_sum for dist in distances])
        for i in range(3):
            gen.position_between(fk_ctrls[i], (orienters[pairs[i][1]], orienters[pairs[i][0]]), distance_weights[i],
                                 include_orientation=True)


    def build_rig_part(self, part):
        segment_count = part.construction_inputs['segment_count']
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)

        scene_ctrl_managers = {}
        for ctrl in part.controls.values():
            scene_ctrl_managers[ctrl.name] = SceneControlManager(ctrl)

        scene_ctrls = {}
        for key, manager in scene_ctrl_managers.items():
            scene_ctrls[key] = manager.create_scene_control()

        for ctrl_key in ['IkPelvis', 'IkWaist', 'IkChest']:
            scene_ctrls[ctrl_key].setParent(transform_grp)

        scene_ctrls['FkHips'].setParent(transform_grp)
        previous_ctrl = None
        for i, ctrl_key in enumerate([f'FkSpine{j+1}' for j in range(3)]):
            if i == 0:
                scene_ctrls[ctrl_key].setParent(transform_grp)
            else:
                scene_ctrls[ctrl_key].setParent(previous_ctrl)
            previous_ctrl = scene_ctrls[ctrl_key]

        for i in range(part.construction_inputs['segment_count']+1):
            scene_ctrls[f'SpineTweak{i+1}'].setParent(transform_grp)

        def snap_ctrl_to_orienter(ctrl_key, orienter_key):
            orienter_manager = OrienterManager(part.placers[orienter_key])
            orienter = orienter_manager.get_orienter()
            pm.matchTransform(scene_ctrls[ctrl_key], orienter)
        snap_ctrl_to_orienter('IkPelvis', f'Spine{1}')
        snap_ctrl_to_orienter('IkChest', f'Spine{segment_count + 1}')
        spine_mid_num = self.find_mid_value(self.jnt_count)
        if isinstance(spine_mid_num, int):
            snap_ctrl_to_orienter('IkWaist', f'Spine{spine_mid_num}')
        else:
            spine_mid_num_pair = spine_mid_num
            orienter_managers = [OrienterManager(part.placers[f'Spine{str(num)}']) for num in spine_mid_num_pair]
            orienters = [manager.get_orienter() for manager in orienter_managers]
            pm.delete(pm.parentConstraint(orienters[0], orienters[1], scene_ctrls['IkWaist']))

        orienters = []
        for i in range(part.construction_inputs['segment_count']+1):
            key = f'Spine{i + 1}'
            orienter_manager = OrienterManager(part.placers[key])
            orienters.append(orienter_manager.get_orienter())

        fk_spine_ctrls = [scene_ctrls[f'FkSpine{i+1}'] for i in range(3)]
        self.position_fk_ctrls(part, fk_spine_ctrls, orienters)

        gen.position_between(scene_ctrls['FkHips'], (orienters[0], fk_spine_ctrls[0]), (0.333, 0.667),
                             include_orientation=True)

        for i, orienter in enumerate(orienters):
            tweak_ctrl = scene_ctrls[f'SpineTweak{i+1}']
            pm.matchTransform(tweak_ctrl, orienter)

        # Ribbon system ------------------------------------------------------------------------------------------------
        # Uses several ribbons layered via connected skinClusters.
        # There are four ribbons: FK ribbon > IK Translate > IK Rotate > IK Output (final output ribbon)
        poly_strip = self.build_poly_strip_at_orienters(orienters)
        poly_strip_edges = self.get_edges_from_poly_strip(poly_strip, self.segment_count)
        nurbs_curves = self.nurbs_curve_from_poly_edges(poly_strip_edges)
        pm.delete(poly_strip)


        '''ribbon_sys = waist_ribbon.install(orienters)
        ribbon_sys["nurbsPlane"].setParent(armature_module.module_ctrl.mobject)
        ribbon_sys["nurbsPlane"].visibility.set(0, lock=1)
        ribbon_sys["nurbsPlane"].inheritsTransform.set(0, lock=1)

        ribbon_sys["joints_group"].setParent(armature_module.module_ctrl.mobject)

        # ...Group to house ribbons
        ribbons_grp = pm.group(name="SpineRibbons", p=no_transform_grp, em=1)

        ik_ctrls_grp = pm.group(name="IkSpineCtrls", em=1, p=no_transform_grp)

        # ...FK
        fk_ribbon = build_fk_ribbon.build(transform_grp, scene_ctrls, ribbon_parent=ribbons_grp)
        # ...IK Translate
        ik_translate_ribbon = build_ik_translate_ribbon.build(
            scene_ctrls, fk_ribbon["nurbsPlane"], ribbon_parent=ribbons_grp, ik_parent=ik_ctrls_grp)
        # ...IK Rotate
        ik_rotate_ribbon = build_ik_rotate_ribbon.build(scene_ctrls, ik_translate_ribbon["nurbsPlane"],
                                                        ribbon_parent=ribbons_grp, ik_parent=ik_ctrls_grp)
        # ...IK Output
        ik_output_ribbon = build_ik_output_ribbon.build(scene_ctrls, ik_rotate_ribbon, ribbon_parent=ribbons_grp,
                                                        jnt_parent=scene_ctrls["IkWaist"].getParent())'''

        return rig_part_container


    def build_poly_strip_at_orienters(self, orienters):
        geo_cells = []
        segment_lengths = [gen.distance_between(orienters[i], orienters[i + 1]) for i in range(len(orienters) - 1)]
        total_spine_length = sum(segment_lengths)
        for i in range(len(orienters) - 1):
            segment_length = gen.distance_between(orienters[i], orienters[i + 1])
            cell = pm.polyPlane(h=segment_length, w=total_spine_length / 15, sx=1, sy=1, axis=(0, 0, 1))[0]
            pm.matchTransform(cell, orienters[i])
            offset = gen.buffer_obj(cell)
            cell.ty.set(segment_length / 2)
            cell.setParent(world=1)
            pm.delete(offset)
            geo_cells.append(cell)
        for i in range(len(geo_cells) - 1):
            this_cell = geo_cells[i]
            this_cell_verts = (this_cell.getShape().vtx[2], this_cell.getShape().vtx[3])
            next_cell = geo_cells[i + 1]
            next_cell_verts = (next_cell.getShape().vtx[0], next_cell.getShape().vtx[1])
            for vert_pair in zip(this_cell_verts, next_cell_verts):
                this_vert, next_vert = vert_pair
                this_vert_position = pm.pointPosition(this_vert, world=1)
                next_vert_position = pm.pointPosition(next_vert, world=1)
                avg_position = [sum((this_vert_position[i], next_vert_position[i])) / 2 for i in range(3)]
                pm.move(avg_position[0], avg_position[1], avg_position[2], this_vert)
                pm.move(avg_position[0], avg_position[1], avg_position[2], next_vert)
        poly_strip = pm.polyUnite(geo_cells, n='cell')[0]
        gen.delete_history(poly_strip)
        pm.select(poly_strip.getShape().vtx[:], replace=1)
        pm.polyMergeVertex(distance=0.0001)
        gen.delete_history(poly_strip)
        pm.select(clear=1)
        return poly_strip



    def get_edges_from_poly_strip(self, poly_strip, segment_count):
        edge_indices = [[j+(3*i) for i in range(segment_count)] for j in range(1, 3)]
        edges = [[poly_strip.getShape().e[i] for i in edge_indices[j]] for j, edge_index_set in enumerate(edge_indices)]
        return edges


    def nurbs_curve_from_poly_edges(self, poly_edges):
        curves = []
        for edges in poly_edges:
            pm.select(edges, replace=1)
            curves.append(pm.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)[0])
        pm.select(clear=1)
        for curve in curves:
            gen.delete_history(curve)
        print(curves)
        return curves
