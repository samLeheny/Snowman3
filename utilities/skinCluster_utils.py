# Title: skinCluster_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel
import numpy as np
import maya.api.OpenMaya as OpenMayaAPI
import maya.api.OpenMayaAnim as OpenMayaAnimAPI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMaya as OpenMaya
###########################
###########################


# Global variables ########

###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
get_skin_cluster
get_MFnSkinCluster_from_skinCluster
get_MfnSkinCluster
get_mesh_from_skin_cluster
get_mesh_components_from_tag_expression
get_skin_cluster_data
compress_weightData
reallocate_jnt_influence
copy_skin_cluster
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################




########################################################################################################################
def get_skin_cluster(obj=None):
    """
    Retrieve skin cluster node from given object.
    Args:
        obj(pyNode): The object to get skin cluster from. If given a transform node, will automatically find its shape node.
    Returns:
        (pyNode): The found skinCluster node.
    """

    skin_cluster = None

    #...If no object provided in arguments, try to get object from current selection
    if not obj:
        selection = pm.ls(sl=1)
        obj = selection[0] if selection else None

    if not obj:
        print(f'Cannot get skin cluster. No object or selection provided.')
        return None

    #...Get shape from object
    shape = obj.getShape() if obj.nodeType() == 'transform' else obj

    #...Get skin cluster
    skin_cluster = mel.eval('findRelatedSkinCluster ' + shape)

    return skin_cluster





########################################################################################################################
def get_MFnSkinCluster_from_skinCluster(skin_cluster):
    """
    Takes a skin cluster in type PyNode and returns it in type MFnSkinCluster
    Args:
        skin_cluster (pyNode): The skin cluster to be returned in type MFnSkinCluster.
    Returns:
        (MFnSkinCluster): Skin cluster.
    """

    selList = OpenMaya.MSelectionList()
    selList.add(skin_cluster)
    clusterNode = OpenMaya.MObject()
    selList.getDependNode(0, clusterNode)
    skinFn = OpenMayaAnim.MFnSkinCluster(clusterNode)
    
    return skinFn





########################################################################################################################
def get_MFnSkinCluster(obj=None):
    """
        Retrieve MFnSkinCluster node from given object.
        Args:
            obj (pyNode): The object to get MFnSkiCluster from. If given a transform node, will automatically find its
                shape node.
        Returns:
            (MFnSkinCluster): The found MFnSkinCluster node.
    """

    #...If no object provided in arguments, try to get object from current selection
    if not obj:
        selection = pm.ls(sl=1)
        obj = selection[0] if selection else None

    if not obj:
        print(f'Cannot get skin cluster. No object or selection provided.')
        return None

    skin_cluster = get_skin_cluster(obj)

    skinFn = get_MFnSkinCluster_from_skinCluster(skin_cluster)

    return skinFn





########################################################################################################################
def get_mesh_from_skin_cluster(skin_cluster):

    geometry = mc.skinCluster(str(skin_cluster), q=1, geometry=1)[0]
    selList = OpenMayaAPI.MSelectionList()
    selList.add(geometry)
    mesh_path = selList.getDagPath(0)

    return geometry, mesh_path





########################################################################################################################
def get_mesh_components_from_tag_expression(skin_cluster, tag='*'):
    """
    Get the mesh components from the component tag expression. Necessary as of Maya 2022.
    Args:
        skin_cluster (pyNode): Skin cluster.
        tag (str, optional): Component tag expression.
    Returns:
        dagPath, MObject: The dagPath tho the shape and the MObject components
    """

    geo = None
    shape_types = ('mesh', 'nurbsSurface', 'nurbsCurve')

    for t in shape_types:
        obj = skin_cluster.listConnections(et=True, t=t)
        if obj:
            geo = obj[0].getShape().name()

    # Get the geo out attribute for the shape
    out_attr = pm.deformableShape(geo, localShapeOutAttr=True)[0]

    # Get the output geometry data as MObject
    sel = OpenMaya.MSelectionList()
    sel.add(geo)
    dep = OpenMaya.MObject()
    sel.getDependNode(0, dep)
    fn_dep = OpenMaya.MFnDependencyNode(dep)
    plug = fn_dep.findPlug(out_attr, True)
    obj = plug.asMObject()

    # Use the MFnGeometryData class to query the components for a tag expression
    fn_geodata = OpenMaya.MFnGeometryData(obj)

    # Components MObject
    components = fn_geodata.resolveComponentTagExpression(tag)

    dagPath = OpenMaya.MDagPath.getAPathTo(dep)

    return dagPath, components





########################################################################################################################
def get_skin_cluster_data(skin_cluster):
    """

    Args:
        skin_cluster (pyNode):
    Returns:
        (list()):
    """

    dagPath, components = get_mesh_components_from_tag_expression(skin_cluster)

    #...Get mesh attached to skin cluster
    geometry, mesh_path = get_mesh_from_skin_cluster(skin_cluster)

    #...Compose list of vertex IDs
    vert_ids = list(range(0, len(pm.ls(f'{geometry}.vtx[*]', fl=1))))

    #...Get skin cluster dependency node
    selList = OpenMayaAPI.MSelectionList()
    selList.add(mel.eval(f'findRelatedSkinCluster {geometry}'))
    skinPath = selList.getDependNode(0)

    #...Get mesh vertices
    fnSkinCluster = OpenMayaAnimAPI.MFnSkinCluster(skinPath)
    fnVtxComp = OpenMayaAPI.MFnSingleIndexedComponent()
    vtxComponents = fnVtxComp.create(OpenMayaAPI.MFn.kMeshVertComponent)
    fnVtxComp.addElements(vert_ids)

    #...Get weights & influences
    raw_weight_data, influ_count = fnSkinCluster.getWeights(mesh_path, vtxComponents)
    weights_array = np.array(list(raw_weight_data), dtype='float64')
    influ_array = [influ_obj.partialPathName() for influ_obj in fnSkinCluster.influenceObjects()]

    #...Convert to non_zero_weights_array
    non_zero_weights_array, influ_map_array, vert_split_array = compress_weightData(weights_array, influ_count)

    #...Gather Blend Weights
    skinFn = get_MFnSkinCluster_from_skinCluster(skin_cluster)
    blend_weights_mArray = OpenMaya.MDoubleArray()
    skinFn.getBlendWeights(dagPath, components, blend_weights_mArray)

    skin_cluster_data = {
        'name' : str(skin_cluster),
        'non-zero weights array' : np.array(non_zero_weights_array),
        'influence map array' : np.array(influ_map_array),
        'vertex split array' : np.array(vert_split_array),
        'influence array' : np.array(influ_array),
        'geometry' : geometry,
        'blend weights' : np.array(blend_weights_mArray),
        'vertex count' : len(vert_split_array) - 1,
        'influence count' : influ_count,
        'envelope' : pm.getAttr(skin_cluster + '.envelope'),
        'skinning method' : pm.getAttr(skin_cluster + '.skinningMethod'),
        'use components' : pm.getAttr(skin_cluster + '.useComponents'),
        'normalize weights' : pm.getAttr(skin_cluster + '.normalizeWeights'),
        'deform user normals' : pm.getAttr(skin_cluster + '.deformUserNormals')
    }

    return skin_cluster_data





########################################################################################################################
def compress_weightData(weights_array, influ_count):

    #...Convert to non_zero_weights_array
    non_zero_weights_array = []
    influ_counter = 0
    influ_map_chunk = []
    influ_map_chunk_count = 0
    vert_split_array = [influ_map_chunk_count]
    influ_map_array = []

    for w in weights_array:
        if w != 0.0:
            non_zero_weights_array.append(w)
            influ_map_chunk.append(influ_counter)

        #...Update inf counter
        influ_counter += 1
        if influ_counter == influ_count:
            influ_counter = 0

            #...Update vert_split_array
            influ_map_array.extend(influ_map_chunk)
            influ_map_chunk_count = len(influ_map_chunk) + influ_map_chunk_count
            vert_split_array.append(influ_map_chunk_count)
            influ_map_chunk = []

    return non_zero_weights_array, influ_map_array, vert_split_array





########################################################################################################################
def reallocate_jnt_influence(skin_cluster, old_jnts, new_jnts, mesh=None, remove_zero_weight_influences=False):
    """
    Moves skin cluster influence weight from one influence object to another.
    Args:
        skin_cluster (pyNode): The skin cluster whose weight to reallocate.
        old_jnts (pyNode/ (pyNodes)): The influence objects to take influence away from.
        new_jnts (pyNode/ (pyNodes): The influence objects to add influence to.
        mesh (pyNode): The mesh, of vertices of the mesh on which to perform reallocation.
        remove_zero_weight_influences (bool): Whether to remove objects as influences after influence reallocation (if
            indeed they no longer have any weight in provided skin cluster.)
    """

    # ...If no object provided in arguments, try to get object from current selection
    if not mesh:
        selection = pm.ls(sl=1)
        mesh = selection[0] if selection else None

    if not mesh:
        print(f'Cannot reallocate joint influences. No mesh or selection provided.')
        return None

    if not isinstance(old_jnts, (list, tuple)):
        old_jnts = (old_jnts,)
    if not isinstance(new_jnts, (list, tuple)):
        new_jnts = (new_jnts,)

    if not len(old_jnts) == len(new_jnts):
        pm.error(f'Cannot reallocate joint influences. The same number of old joints as new joints must be provided.'
                 f'Received {len(old_jnts)} old joints and {len(new_jnts)} new joints.')

    for i, old_jnt in enumerate(old_jnts):
        #...Ensure new joint is an influence on this skin cluster

        #...Transfer skin weights
        pm.skinPercent(skin_cluster, transformMoveWeights=(old_jnt, new_jnts[i]))

    #...Remove influences with zero weights (if desired)
    pm.skinCluster(skin_cluster, e=1, removeUnusedInfluence=1) if remove_zero_weight_influences else None





########################################################################################################################
def copy_skin_cluster(source_obj, destination_objs, remove_unused_influences=False):
    """

    Args:
        source_obj (pyNode): The object you wish to copy the skinning FROM.
        destination_objs (pyNode/ (pyNodes)): The objects you wish to copy the skinning TO.
        remove_unused_influences (bool): Whether to remove any influences objects with zero weighting once the
            new skin cluster has been copied to.
    Returns:
        (pyNode): The new skin cluster(s).
    """

    new_skin_clusters = []

    #...If no objects provided, try to get them from current selection.
    if not source_obj and not destination_objs:
        selection = pm.ls(sl=1, r=1)
        if not len(selection) >= 2:
            pm.error("Cannot copy skin cluster. At least two meshes must be provided.")
            return
        source_obj = selection[0]
        destination_objs = [selection[i] for i in range(1, len(selection))]

    if not isinstance(destination_objs, (list, tuple)):
        destination_objs = (destination_objs,)

    #...Get skin cluster of source object
    source_skin_cluster = get_skin_cluster(source_obj)
    new_skin_clusters.append(source_skin_cluster)

    #...Get a list of the joints the skin cluster is being effected by
    influ_jnts = pm.listConnections(source_skin_cluster, s=True, t="joint")
    for dest_obj in destination_objs:
        #...Skin the destination mesh with the same joints
        dest_skin_cluster = pm.skinCluster(influ_jnts, dest_obj, tsb=1)[0]
        #...Copy skin weights between the source and destination mesh
        ########...If crashing happens here, it might have something to do with ngSkinTool nodes...########
        pm.copySkinWeights(ss=source_skin_cluster, ds=dest_skin_cluster, noMirror=1, sa="closestPoint",
                           ia="closestJoint")

        # Clean up the unused joints (if desired)
        if remove_unused_influences:
            pm.skinCluster(dest_skin_cluster, e=1, removeUnusedInfluence=1)

    return new_skin_clusters