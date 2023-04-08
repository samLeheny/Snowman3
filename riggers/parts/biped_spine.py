# Title: biped_spine.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

import Snowman3.utilities.node_utils as nodes
importlib.reload(nodes)

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
        size = 0.8
        creators = []
        for i in range(self.jnt_count):
            n = i + 1
            has_vector_handles = True
            size = 1.25
            if i == range(self.jnt_count):
                has_vector_handles = False
                size = size
            placer_creator = PlacerCreator(
                name=f'Spine{n}',
                side=self.side,
                parent_part_name=self.part_name,
                position=(0, spine_seg_length * i, 0),
                size=size,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 1, 0], [0, 0, 1]], size),
                orientation=[[0, 1, 0], [0, 0, 1]],
                has_vector_handles=has_vector_handles
            )
            creators.append(placer_creator)
        placer_creator = PlacerCreator(
            name=f'SpineSettings',
            side=self.side,
            parent_part_name=self.part_name,
            position=(15, 0, 0),
            size=size*0.8,
            has_vector_handles=False
        )
        creators.append(placer_creator)
        [placers.append(creator.create_placer()) for creator in creators]
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
                size = 14,
                side=self.side
            ),
            ControlCreator(
                name='IkWaist',
                shape='circle',
                color=color_code[self.side],
                size=14,
                side=self.side
            ),
            ControlCreator(
                name='IkPelvis',
                shape='circle',
                color=color_code[self.side],
                size=14,
                side=self.side
            )
        ]
        ctrl_creators += ik_ctrl_creators
        fk_ctrl_creators = [
            ControlCreator(
                name='FkSpine1',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                up_direction = [0, -1, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkSpine2',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                up_direction = [0, -1, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkSpine3',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                up_direction = [0, -1, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkHips',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
                side=self.side
            )
        ]
        ctrl_creators += fk_ctrl_creators
        tweak_ctrl_creators = [
            ControlCreator(
                name=f'SpineTweak{i+1}',
                shape='square',
                color=color_code['M3'],
                size=12,
                side=self.side
            ) for i in range(self.segment_count+1)
        ]
        ctrl_creators += tweak_ctrl_creators
        ctrl_creators.append(
            ControlCreator(
                name='SpineSettings',
                shape='gear',
                color=color_code['settings'],
                size=1,
                locks={'v': 1, 't': [1, 1, 1], 'r': [1, 1, 1], 's': [1, 1, 1]},
                side=self.side
            )
        )
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls



    def get_connection_pairs(self):
        pairs = []
        for i in range(self.segment_count):
            n = i + 1
            pairs.append(
                (f'Spine{n+1}', f'Spine{n}')
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
        seg_count = part.construction_inputs['segment_count']
        segment_lengths = [gen.distance_between(orienters[f'Spine{i+1}'],
                                                orienters[f'Spine{i+2}']) for i in range(seg_count)]
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
                    pairs.append((i + 1, i + 2))
                    pair_values.append((spine_length_increments[i - 1], increment))
                    break
        distance_weights = []
        for ctrl_placement, pair_value in zip(fk_ctrl_placement, pair_values):
            distances = [abs(abs(ctrl_placement) - abs(value)) for value in pair_value]
            distance_sum = sum(distances)
            distance_weights.append([dist / distance_sum for dist in distances])
        for i in range(3):
            gen.position_between(fk_ctrls[i], (orienters[f'Spine{pairs[i][1]}'], orienters[f'Spine{pairs[i][0]}']),
                                 distance_weights[i], include_orientation=True)


    def build_rig_part(self, part):
        rig_part_container, connector, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)

        segment_count = part.construction_inputs['segment_count']
        bind_jnt_count = segment_count + 1

        spine_orienters = [orienters[f'Spine{i+1}'] for i in range(segment_count+1)]

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

        def snap_ctrl_to_orienter(ctrl_key, orienter):
            pm.matchTransform(scene_ctrls[ctrl_key], orienter)
        snap_ctrl_to_orienter('IkPelvis', orienters[f'Spine1'])
        snap_ctrl_to_orienter('IkChest', orienters[f'Spine{segment_count + 1}'])
        spine_mid_num = self.find_mid_value(self.jnt_count)
        if isinstance(spine_mid_num, int):
            snap_ctrl_to_orienter('IkWaist', orienters[f'Spine{spine_mid_num}'])
        else:
            pm.delete(pm.parentConstraint(spine_orienters[spine_mid_num[0]], spine_orienters[spine_mid_num[1]],
                                          scene_ctrls['IkWaist']))

        pm.matchTransform(scene_ctrls['SpineSettings'], orienters['SpineSettings'])
        scene_ctrls['SpineSettings'].setParent(transform_grp)

        fk_spine_ctrls = [scene_ctrls[f'FkSpine{i+1}'] for i in range(3)]
        self.position_fk_ctrls(part, fk_spine_ctrls, orienters)
        gen.position_between(scene_ctrls['FkHips'], (orienters[f'Spine1'], fk_spine_ctrls[0]), (0.333, 0.667),
                             include_orientation=True)

        for i in range(segment_count+1):
            tweak_ctrl = scene_ctrls[f'SpineTweak{i+1}']
            pm.matchTransform(tweak_ctrl, orienters[f'Spine{i+1}'])

        # Ribbon system ------------------------------------------------------------------------------------------------
        poly_strip = self.build_poly_strip_at_orienters(spine_orienters)
        poly_strip_edges = self.get_edges_from_poly_strip(poly_strip, self.segment_count)
        nurbs_curves = self.nurbs_curve_from_poly_edges(poly_strip_edges)
        pm.delete(poly_strip)
        refined_curves = [self.refine_curve(curve) for curve in nurbs_curves]
        ribbon = self.surface_from_curves(refined_curves, name=f'{part.name}_SURF')

        ribbons_grp = pm.group(name='SpineRibbons', p=no_transform_grp, em=1)
        ik_ctrls_grp = pm.group(name='IkSpineCtrls', em=1, p=no_transform_grp)

        fk_ribbon = build_fk_ribbon.build(ribbon, scene_ctrls, ribbons_grp, spine_orienters)
        ik_translate_ribbon = build_ik_translate_ribbon.build(
            scene_ctrls, fk_ribbon['nurbsPlane'], ribbon_parent=ribbons_grp, ik_parent=ik_ctrls_grp)
        ik_rotate_ribbon = build_ik_rotate_ribbon.build(
            scene_ctrls, ik_translate_ribbon['nurbsPlane'], ribbon_parent=ribbons_grp, ik_parent=ik_ctrls_grp)
        ik_output_ribbon = build_ik_output_ribbon.build(
            scene_ctrls, ik_rotate_ribbon, ribbon_parent=ribbons_grp, jnt_parent=scene_ctrls['IkWaist'].getParent())
        pm.delete(ribbon)

        bind_jnts = self.create_bind_joints(grp_parent=no_transform_grp, ctrls=scene_ctrls,
                                            bind_jnt_count=bind_jnt_count, ribbon=ik_output_ribbon['nurbsPlane'],
                                            rig_part_transform=transform_grp)

        for ctrl, indices in zip((scene_ctrls['IkPelvis'], scene_ctrls['IkWaist'], scene_ctrls['IkChest']),
                                 ((0, 1), (2, 3, 4), (5,))):
            for i in indices:
                mod = gen.buffer_obj(bind_jnts[i], suffix='MOD')
                mult_matrix = nodes.multMatrix(matrixIn=(ctrl.worldMatrix, mod.parentInverseMatrix))
                nodes.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputScale=mod.scale)

        # Control scaling ----------------------------------------------------------------------------------------------
        for ctrl in (scene_ctrls['IkPelvis'], scene_ctrls['IkWaist'], scene_ctrls['IkChest']):
            node = ctrl.getParent(generations=2)
            mult_matrix = nodes.multMatrix(
                matrixIn=(transform_grp.worldMatrix, node.parentInverseMatrix))
            nodes.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputScale=node.scale)

        # Install tweak controls above bind joints ---------------------------------------------------------------------
        vis_attr_name = 'TweakCtrls'
        settings_ctrl = scene_ctrls['SpineSettings']
        pm.addAttr(settings_ctrl, longName=vis_attr_name, attributeType='enum', keyable=0, enumName='Off:On')
        pm.setAttr(f'{settings_ctrl}.{vis_attr_name}', channelBox=1)

        for i in range(bind_jnt_count):
            ctrl = scene_ctrls[f'SpineTweak{i+1}']
            pm.connectAttr(f'{settings_ctrl}.{vis_attr_name}', ctrl.getShape().visibility)


        # Spine volume -------------------------------------------------------------------------------------------------
        settings_ctrl = scene_ctrls['SpineSettings']
        volume_attr_name = 'SpineVolume'
        pm.addAttr(settings_ctrl, longName=volume_attr_name, attributeType='float', minValue=0, maxValue=10,
                   defaultValue=0, keyable=1)

        len_1 = pm.shadingNode('arcLengthDimension', au=1)
        len_2 = pm.shadingNode('arcLengthDimension', au=1)
        for length in (len_1, len_2):
            length.visibility.set(0, lock=1)
            length.uParamValue.set(4.0)
            length.vParamValue.set(0.5)

        len_1.getParent().setParent(fk_ribbon['nurbsPlane'])
        len_2.getParent().setParent(ik_output_ribbon['nurbsPlane'])

        fk_ribbon['nurbsPlane'].worldSpace[0].connect(len_1.nurbsGeometry)
        ik_output_ribbon['nurbsPlane'].worldSpace[0].connect(len_2.nurbsGeometry)

        div = nodes.floatMath(floatA=len_1.arcLength, floatB=len_2.arcLength, operation=3)

        remap = nodes.remapValue(inputValue=f'{settings_ctrl}.{volume_attr_name}', inputMax=10, outputMin=1,
                                 outputMax=div.outFloat)

        for i in (2, segment_count):
            for attr in ('sx', 'sz'):
                pm.connectAttr(remap.outValue, f'{scene_ctrls[f"SpineTweak{i}"].getParent()}.{attr}')

        # IK control pivot height settings -----------------------------------------------------------------------------
        pivot_height_attr_name = 'PivotHeight'
        for node_set in (('SpineSettings', [],), ('IkPelvis', [ik_rotate_ribbon['bottom_sys'][1].getParent()],),
                         ('IkChest', [ik_rotate_ribbon['top_sys'][1].getParent()])):
            ctrl = scene_ctrls[node_set[0]]
            target_nodes = node_set[1]
            target_nodes.append(ctrl)
            pm.addAttr(ctrl, longName=pivot_height_attr_name, keyable=1, attributeType='float', defaultValue=0)
            for node in target_nodes:
                pm.connectAttr(f'{ctrl}.{pivot_height_attr_name}', f'{node}.rotatePivotY')

        return rig_part_container



    def create_bind_joints(self, grp_parent, ctrls, bind_jnt_count, ribbon, rig_part_transform):
        bind_jnts_grp = pm.group(name='spine_bindJnts', p=grp_parent, em=1)
        bind_jnts = []
        bind_jnt_attach_nodes = []
        for i in range(bind_jnt_count):
            jnt = rig.joint(name=f'Spine{i + 1}', joint_type='BIND', radius=1.25)
            jnt_buffer = gen.buffer_obj(jnt)
            pin = gen.point_on_surface_matrix(ribbon.getShape() + '.worldSpace',
                                              parameter_V=0.5, parameter_U=1 - ((1.0 / 6) * i), decompose=True)
            attach = pm.group(name=f'{jnt}_ATTACH', em=1, p=bind_jnts_grp)
            pin.outputTranslate.connect(attach.translate)
            pin.outputRotate.connect(attach.rotate)
            jnt_buffer.setParent(attach)
            jnt_buffer.translate.set(0, 0, 0)
            mult_matrix = nodes.multMatrix(matrixIn=(rig_part_transform.worldMatrix, jnt_buffer.parentInverseMatrix))
            nodes.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputScale=jnt_buffer.scale)
            bind_jnts.append(jnt)
            bind_jnt_attach_nodes.append(attach)
            tweak_ctrl = ctrls[f'SpineTweak{i + 1}']
            tweak_ctrl.setParent(jnt.getParent())
            gen.zero_out(tweak_ctrl)
            jnt.setParent(tweak_ctrl)
        return bind_jnts



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
            curve_name = pm.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)[0]
            curve = pm.PyNode(curve_name)
            curves.append(curve)
        pm.select(clear=1)
        for curve in curves:
            gen.delete_history(curve)
        return curves



    def refine_curve(self, curve):
        new_point_positions = []
        curve_point_params = (0, 0.5, 1.5, 3, 4.5, 5.5, 6)
        for i, param in enumerate(curve_point_params):
            point = pm.shadingNode('pointOnCurveInfo', name=f'TEMP{i+1}', au=1)
            curve.getShape().worldSpace[0].connect(point.inputCurve)
            point.parameter.set(param)
            new_position = [point.result.position.get()[i] for i in range(3)]
            new_point_positions.append(new_position)
        new_curve = gen.nurbs_curve(name='TEMP_Spine_CRV', form='open', degree=3,
                                    cvs=new_point_positions)
        pm.delete(curve)
        return new_curve




    def surface_from_curves(self, curves, name):
        surface = pm.loft(curves[0], curves[1], name=name, uniform=1, close=0, autoReverse=1, degree=3, sectionSpans=1,
                          range=0, polygon=0, reverseSurfaceNormals=1)[0]
        gen.delete_history(surface)
        pm.delete(curves)
        return surface
