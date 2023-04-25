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
                side=self.side,
                locks={'s': [1, 1, 1]}
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
        pairs = [('Spine1', 'SpineSettings')]
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
        ribbon.visibility.set(0, lock=1)

        ribbons_grp = pm.group(name='SpineRibbons', p=no_transform_grp, em=1)
        ik_ctrls_grp = pm.group(name='IkSpineCtrls', em=1, p=no_transform_grp)

        fk_ribbon = self.fk_ribbon(ribbon, scene_ctrls, ribbons_grp, spine_orienters)
        ik_translate_ribbon = self.ik_translate_ribbon(scene_ctrls, fk_ribbon['nurbsPlane'], ribbon_parent=ribbons_grp,
                                                       ik_parent=ik_ctrls_grp)
        ik_rotate_ribbon = self.ik_rotate_ribbon(scene_ctrls, ik_translate_ribbon['nurbsPlane'],
                                                 ribbon_parent=ribbons_grp, ik_parent=ik_ctrls_grp)
        ik_output_ribbon = self.ik_output_ribbon(scene_ctrls, ik_rotate_ribbon, ribbon_parent=ribbons_grp,
                                                 jnt_parent=scene_ctrls['IkWaist'].getParent())
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

        self.apply_all_control_transform_locks()

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



    def fk_ribbon(self, ribbon, ctrls, ribbon_parent, orienters):

        setup_ribbon = ribbon

        fk_ribbon = pm.duplicate(setup_ribbon, name='FkSpineRibbon_SURF')[0]
        for attr in gen.all_transform_attrs:
            pm.setAttr(f'{fk_ribbon}.{attr}', lock=0)
        fk_ribbon.setParent(world=1)

        pm.select(fk_ribbon)
        pm.delete(constructionHistory=1)
        pm.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
        pm.select(clear=1)

        fk_ribbon.setParent(ribbon_parent)

        # FK joints --------------------------------------------------------------------------------------------------------
        def position_joint(jnt, u_value, jnt_parent=None):
            pin = gen.point_on_surface_matrix(fk_ribbon.getShape() + ".worldSpace", parameter_V=0.5,
                                                    parameter_U=u_value, decompose=True)
            pin.outputTranslate.connect(jnt.translate)
            gen.break_connections(jnt.translate)
            pm.delete(pin)
            jnt.setParent(jnt_parent) if jnt_parent else None

        fk_1_jnt = rig.joint(name="FkSpine1", joint_type='JNT', radius=1.3)
        position_joint(fk_1_jnt, 1.0, ctrls["FkHips"])

        fk_1_inv_jnt = rig.joint(name="FkSpine1Inv", joint_type='JNT', radius=1)
        pm.delete(pm.pointConstraint(ctrls["FkHips"], fk_1_inv_jnt))
        fk_1_inv_jnt.setParent(fk_1_jnt)
        buffer = gen.buffer_obj(ctrls["FkHips"])

        fk_2_jnt = rig.joint(name="FkSpine2", joint_type='JNT', radius=1.3)
        position_joint(fk_2_jnt, 0.7, ctrls["FkSpine1"])

        fk_2_inv_jnt = rig.joint(name="FkSpine2Inv", joint_type='JNT', radius=1)
        pm.delete(pm.pointConstraint(ctrls["FkSpine2"], fk_2_inv_jnt))
        fk_2_inv_jnt.setParent(fk_2_jnt)
        buffer = gen.buffer_obj(ctrls["FkSpine1"])

        fk_3_jnt = rig.joint(name="FkSpine3", joint_type='JNT', radius=1.3)
        pm.delete(pm.pointConstraint(fk_2_inv_jnt, fk_3_jnt))
        fk_3_jnt.setParent(ctrls["FkSpine2"])

        fk_3_inv_jnt = rig.joint(name="FkSpine3Inv", joint_type='JNT', radius=1)
        pm.delete(pm.pointConstraint(ctrls["FkSpine3"], fk_3_inv_jnt))
        fk_3_inv_jnt.setParent(fk_3_jnt)
        buffer = gen.buffer_obj(ctrls["FkSpine2"])
        buffer.setParent(fk_2_inv_jnt)

        fk_4_jnt = rig.joint(name="FkSpine4", joint_type='JNT', radius=1.3)
        pm.delete(pm.pointConstraint(ctrls["FkSpine3"], fk_4_jnt))
        fk_4_jnt.setParent(ctrls["FkSpine3"])

        fk_4_inv_jnt = rig.joint(name="FkSpine4inv", joint_type='JNT', radius=1)
        pm.delete(pm.pointConstraint(orienters[-1], fk_4_inv_jnt))
        # world_pos = placers['Spine6'].world_position
        # pm.move(world_pos[0], world_pos[1], world_pos[2], fk_4_inv_jnt)
        fk_4_inv_jnt.setParent(ctrls["FkSpine3"])

        buffer = gen.buffer_obj(ctrls["FkSpine3"])
        buffer.setParent(fk_3_inv_jnt)

        fk_jnts = [fk_1_jnt, fk_1_inv_jnt, fk_2_jnt, fk_2_inv_jnt, fk_3_jnt, fk_3_inv_jnt, fk_4_jnt, fk_4_inv_jnt]

        # ...Skin FK Ribbon
        pm.select((fk_jnts[0], fk_jnts[1], fk_jnts[2], fk_jnts[4], fk_jnts[5], fk_jnts[7]), replace=1)
        pm.select(fk_ribbon, add=1)
        pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
        skin_clust = gen.get_skin_cluster(fk_ribbon)

        # ...Refine weights
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[6][0:3]', transformValue=[(fk_jnts[0], 1.0)])
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[5][0:3]', transformValue=[(fk_jnts[0], 1.0)])
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[4][0:3]', transformValue=[(fk_jnts[0], 0.8), (fk_jnts[1], 0.2)])
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[3][0:3]', transformValue=[(fk_jnts[2], 1.0)])
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[2][0:3]', transformValue=[(fk_jnts[4], 0.9), (fk_jnts[5], 0.1)])
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[1][0:3]', transformValue=[(fk_jnts[4], 0.05), (fk_jnts[7], 0.95)])
        pm.skinPercent(skin_clust, fk_ribbon + '.cv[0][0:3]', transformValue=[(fk_jnts[7], 1.0)])

        return {"nurbsPlane": fk_ribbon,
                "fkJnts": fk_jnts}


    def ik_translate_ribbon(self, ctrls, fk_ribbon, ribbon_parent, ik_parent):
        # ...IK Translate nurbs plane
        ik_translate_ribbon = pm.duplicate(fk_ribbon, name='IkTranslateSpineRibbon_SURF')[0]
        for attr in gen.all_transform_attrs:
            pm.setAttr(f'{ik_translate_ribbon}.{attr}', lock=0)
        ik_translate_ribbon.setParent(world=1)
        ik_translate_ribbon.setParent(ribbon_parent)

        # ...IK Translate joints
        def ik_translate_jnt_sys(name, u_value, ctrl, mid=False):
            grp = pm.group(name=f'spine_{name}_ik_translate', p=ik_parent, em=1)

            ctrl_driver_ribbon = fk_ribbon.getShape()
            if mid:
                ctrl_driver_ribbon = ik_translate_ribbon.getShape()
            pin = gen.point_on_surface_matrix(ctrl_driver_ribbon + ".worldSpace", parameter_U=u_value, parameter_V=0.5,
                                              decompose=True)
            pin.outputTranslate.connect(grp.translate)
            pin.outputRotate.connect(grp.rotate)

            ctrl.setParent(ctrl, grp)
            buffer = gen.buffer_obj(ctrl)

            jnt, base_jnt = None, None
            if not mid:
                jnt = rig.joint(name=f'spine_{name}_ik_translate', joint_type='JNT', parent=buffer)
                base_jnt = rig.joint(name=f'spine_{name}_ik_translate_base', joint_type='JNT', parent=buffer)
                [gen.zero_out(j) for j in (jnt, base_jnt)]

                ctrl.translate.connect(jnt.translate)

            return grp, jnt, base_jnt

        ik_translate_bottom_sys = ik_translate_jnt_sys('pelvis', 1.0, ctrls['IkPelvis'])
        ik_translate_mid_sys = ik_translate_jnt_sys('waist', 0.5, ctrls['IkWaist'], mid=True)
        ik_translate_top_sys = ik_translate_jnt_sys('chest', 0.0, ctrls['IkChest'])

        # ...Skin IK Translate Ribbon
        pm.select((ik_translate_bottom_sys[1], ik_translate_top_sys[1]), replace=1)
        pm.select(ik_translate_ribbon, add=1)
        pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
        skin_clust = gen.get_skin_cluster(ik_translate_ribbon)

        # ...Use FK Ribbon as input shape for IK Translate Ribbon's skin cluster
        rig.mesh_to_skinClust_input(fk_ribbon.getShape(), skin_clust)

        # ...Use IK Translate base joints as preBindMatrix inputs for skin cluster to avoid double transforms from the FK
        # ...Ribbon
        ik_translate_bottom_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[0])
        ik_translate_top_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[1])

        # ...Refine weights
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[6][0:3]',
                       transformValue=[(ik_translate_bottom_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[5][0:3]',
                       transformValue=[(ik_translate_bottom_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[4][0:3]',
                       transformValue=[(ik_translate_bottom_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[3][0:3]',
                       transformValue=[(ik_translate_bottom_sys[1], 0.6),
                                       (ik_translate_top_sys[1], 0.4)])
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[2][0:3]',
                       transformValue=[(ik_translate_bottom_sys[1], 0.05),
                                       (ik_translate_top_sys[1], 0.95)])
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[1][0:3]',
                       transformValue=[(ik_translate_top_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0][0:3]',
                       transformValue=[(ik_translate_top_sys[1], 1.0)])

        # ...Template FK Ribbon for visual clarity
        fk_ribbon.getShape().template.set(1)

        return {"nurbsPlane": ik_translate_ribbon}



    def ik_rotate_ribbon(self, ctrls, ik_translate_ribbon, ribbon_parent, ik_parent):
        ik_rotate_ribbon = pm.duplicate(ik_translate_ribbon, name='IkRotateSpineRibbon_SURF')[0]
        for attr in gen.all_transform_attrs:
            pm.setAttr(f'{ik_rotate_ribbon}.{attr}', lock=0)
        ik_rotate_ribbon.setParent(world=1)

        ik_rotate_ribbon.setParent(ribbon_parent)

        # ...IK Rotate joints
        def ik_rotate_jnt_sys(name, u_value, ctrl=None):
            grp = pm.group(name=f'spine_{name}_ik_rotate', p=ik_parent, em=1)

            pin = gen.point_on_surface_matrix(ik_translate_ribbon.getShape() + ".worldSpace", parameter_U=u_value,
                                              parameter_V=0.5, decompose=True)
            pin.outputTranslate.connect(grp.translate)
            pin.outputRotate.connect(grp.rotate)

            jnt = rig.joint(name=f'spine_{name}_ik_rotate', joint_type='JNT')

            offset = gen.buffer_obj(jnt, parent=grp)
            pm.rename(offset, f'spine_{name}_ik_rotate_OFFSET')

            base_jnt = rig.joint(name=f'spine_{name}_ik_rotate_base', joint_type='JNT', parent=offset)

            offset.translate.set(0, 0, 0)

            buffer = gen.buffer_obj(jnt)
            if ctrl:
                ctrl.rotate.connect(buffer.rotate)

            return grp, jnt, base_jnt

        ik_rotate_bottom_sys = ik_rotate_jnt_sys("pelvis", 1.0, ctrls["IkPelvis"])
        ik_rotate_mid_sys = ik_rotate_jnt_sys("waist", 0.5)
        ik_rotate_top_sys = ik_rotate_jnt_sys("chest", 0.0, ctrls["IkChest"])

        # ...Skin IK Rotate Ribbon
        pm.select((ik_rotate_bottom_sys[1], ik_rotate_mid_sys[1], ik_rotate_top_sys[1]), replace=1)
        pm.select(ik_rotate_ribbon, add=1)
        pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
        skin_clust = gen.get_skin_cluster(ik_rotate_ribbon)

        # ...Use IK Translate Ribbon as input shape for IK Rotate Ribbon's skin cluster
        rig.mesh_to_skinClust_input(ik_translate_ribbon.getShape(), skin_clust)

        # ...Use IK Rotate base joints as preBindMatrix inputs for skin cluster to avoid double transforms from the IK
        # ...Translate Ribbon
        ik_rotate_bottom_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[0])
        ik_rotate_mid_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[1])
        ik_rotate_top_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[2])

        # ...Refine weights
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[6][0:3]', transformValue=[(ik_rotate_bottom_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[5][0:3]', transformValue=[(ik_rotate_bottom_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[4][0:3]', transformValue=[(ik_rotate_bottom_sys[1], 0.715),
                                                                                     (ik_rotate_mid_sys[1], 0.285)])
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[3][0:3]', transformValue=[(ik_rotate_mid_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[2][0:3]', transformValue=[(ik_rotate_top_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[1][0:3]', transformValue=[(ik_rotate_top_sys[1], 1.0)])
        pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0][0:3]', transformValue=[(ik_rotate_top_sys[1], 1.0)])

        # ...Template IK Translate Ribbon for visual clarity
        ik_translate_ribbon.getShape().template.set(1)

        return {"nurbsPlane": ik_rotate_ribbon,
                "bottom_sys": ik_rotate_bottom_sys,
                "mid_sys": ik_rotate_mid_sys,
                "top_sys": ik_rotate_top_sys, }



    def ik_output_ribbon(self, ctrls, ik_rotate_ribbon, ribbon_parent, jnt_parent):
        # ...IK Output nurbs plane
        ik_output_ribbon = pm.duplicate(ik_rotate_ribbon["nurbsPlane"], name="IkOutputSpineRibbon_SURF")[0]
        for attr in gen.all_transform_attrs:
            pm.setAttr(ik_output_ribbon + "." + attr, lock=0)
        ik_output_ribbon.setParent(world=1)

        ik_output_ribbon.setParent(ribbon_parent)

        # ...IK Output joints
        def ik_output_jnt_sys(name):
            jnt = rig.joint(name="spine_{}_ik_output".format(name), joint_type='JNT', parent=jnt_parent)

            base_jnt = rig.joint(name="spine_{}_ik_output_base".format(name), joint_type='JNT', parent=jnt_parent)

            [j.translate.set(0, 0, 0) for j in (jnt, base_jnt)]

            ctrls["IkWaist"].translate.connect(jnt.translate)
            ctrls["IkWaist"].rotate.connect(jnt.rotate)

            return jnt, base_jnt

        ik_output_mid_sys = ik_output_jnt_sys("waist")

        # ...Skin IK Rotate Ribbon
        pm.select((ik_rotate_ribbon["bottom_sys"][2], ik_rotate_ribbon["top_sys"][2], ik_output_mid_sys[0]), replace=1)
        pm.select(ik_output_ribbon, add=1)
        pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
        skin_clust = gen.get_skin_cluster(ik_output_ribbon)

        # ...Use IK Rotate Ribbon as input shape for IK Output Ribbon's skin cluster
        rig.mesh_to_skinClust_input(ik_rotate_ribbon["nurbsPlane"].getShape(), skin_clust)

        # ...Use IK Rotate base joints as preBindMatrix inputs for skin cluster to avoid double transforms from the IK
        # ...Translate Ribbon
        ik_rotate_ribbon["bottom_sys"][2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[0])
        ik_rotate_ribbon["top_sys"][2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[1])
        ik_output_mid_sys[1].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[2])

        # ...Refine weights
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[6][0:3]',
                       transformValue=[(ik_rotate_ribbon["bottom_sys"][2], 1.0)])
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[5][0:3]',
                       transformValue=[(ik_rotate_ribbon["bottom_sys"][2], 1.0)])
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[4][0:3]',
                       transformValue=[(ik_rotate_ribbon["bottom_sys"][2], 0.715),
                                       (ik_output_mid_sys[0], 0.285)])
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[3][0:3]', transformValue=[(ik_output_mid_sys[0], 1.0)])
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[2][0:3]',
                       transformValue=[(ik_rotate_ribbon["top_sys"][2], 0.75),
                                       (ik_output_mid_sys[0], 0.25)])
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[1][0:3]',
                       transformValue=[(ik_rotate_ribbon["top_sys"][2], 1.0)])
        pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0][0:3]',
                       transformValue=[(ik_rotate_ribbon["top_sys"][2], 1.0)])

        # ...Template FK Ribbon for visual clarity
        ik_rotate_ribbon["nurbsPlane"].getShape().template.set(1)

        return {"nurbsPlane": ik_output_ribbon}
