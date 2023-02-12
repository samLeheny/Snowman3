import cPickle
import math
import os
import re
import types

import maya.cmds as mc
from maya.api import OpenMaya as om2
from maya.api import OpenMayaAnim as oma2
import pymel.core as pm


## ======================================================================
## may seem like overkill but this is a simple
## way to make sure that we're matching very
## specific naming
gLayer_re = re.compile("(LAYER_)([0-9]+)")
gExtras   = pm.PyNode("extras")


## ======================================================================
## om2 utilities
def get_mobject(name):
	sel = om2.MGlobal.getSelectionListByName(name)
	return sel.getDependNode(0)


## ---------------------------------------------------------------------
def get_dag_path(name):
	sel = om2.MGlobal.getSelectionListByName(name)
	return sel.getDagPath(0)


## ---------------------------------------------------------------------
def get_mfn_skin(skin_ob):
	if isinstance(skin_ob, pm.PyNode):
		skin_ob = get_mobject(skin_ob.longName())
	return oma2.MFnSkinCluster(skin_ob)


## ---------------------------------------------------------------------
def get_mfn_mesh(mesh_ob):
	if isinstance(mesh_ob, pm.PyNode):
		mesh_ob = get_mobject(mesh_ob.longName())
	return om2.MFnMesh(mesh_ob)


## ---------------------------------------------------------------------
def get_complete_components(mesh):
	"""
	Return an object component for all the vertices
	on the specified mesh, for specifying vertices
	in the skin weights transfer tools.

	:param mesh: Mesh you wish to have components for
	:type mesh: om2.MFnMesh or pm.nt.Mesh
	:return: an MObject representing the selection of all vertices on the mesh
	:rtype: om2.MFnSingleIndexedComponent
	"""
	assert isinstance(mesh, om2.MFnMesh), "Mesh must be an MFnMesh or pm.nt.Mesh instance."
	comp = om2.MFnSingleIndexedComponent()
	ob = comp.create(om2.MFn.kMeshVertComponent)
	comp.setCompleteData(mesh.numVertices)
	return ob


## ======================================================================
def get_good_weights_path(mesh):

	path = os.path.abspath(os.sep.join((mc.workspace(q=True, rd=True), "data", mesh + ".skinweights")))

	return path


## ---------------------------------------------------------------------
def try_matrix_set(plug, value):
	try:

		plug.set(value)

	except RuntimeError:

		pass


## ---------------------------------------------------------------------
def try_matrix_connect(plug, target):

	try:

		if not plug in target.inputs():
			plug >> target

	except RuntimeError:

		pass





# ----------------------------------------------------------------------------------------------------------------------
def save_skin_weights(mesh, path=None):
	"""
	Export skin cluster weights.
	Args:
		mesh (transform/mesh):
		path (directory):
	"""


	mesh_shape = get_deform_shape(mesh)
	mesh       = mesh_shape.getParent()
	mesh_skin  = get_skin_cluster(mesh)

	assert mesh_skin, "No skin for mesh {0} -- cannot save.".format(mesh)

	mesh_dp    = get_dag_path(mesh_shape.longName())
	skin_mfn   = get_mfn_skin(mesh_skin)
	mesh_mfn   = get_mfn_mesh(mesh_shape)
	components = get_complete_components(mesh_mfn)

	weights, influence_count = skin_mfn.getWeights(mesh_dp, components)

	bind_inputs = [(x.inputs(plugs=True)[0].ctrl_name_tag() if x.isConnected() else None) for x in mesh_skin.bindPreMatrix]
	influence_objects = [x.ctrl_name_tag() for x in mesh_skin.influenceObjects()]

	# Assemble data
	data = {
		"weights"          : list(weights),
		"influence_count"  : influence_count,
		"influence_objects": influence_objects,
		"bind_inputs"      : bind_inputs,
	}

	path = path or get_good_weights_path(mesh)
	with open(path, "w") as fp:
		cPickle.dump(data, fp)

	om2.MGlobal.displayInfo(f'+ Saved skin weights for {mesh} to {path}')





## ---------------------------------------------------------------------
def load_skin_weights(mesh, path=None, rebind=False):
	mesh_shape = get_deform_shape(mesh)
	mesh       = mesh_shape.getParent()
	mesh_skin  = get_skin_cluster(mesh)

	path = path or get_good_weights_path(mesh)
	with open(path, "r") as fp:
		data = cPickle.get_data_from_file(fp)

	weights           = om2.MDoubleArray(data["weights"])
	influence_count   = data["influence_count"]
	influence_objects = data["influence_objects"]
	bind_inputs       = data["bind_inputs"]

	if (not rebind) and mesh_skin:
		## quick check to make sure the influences match
		## you should do more work here!
		assert len(mesh_skin.influenceObjects() == influence_count), "Influence counts do not match."

	if rebind and mesh_skin:
		pm.delete(mesh_skin)
	
	## perform bind
	if rebind:
		pm.select(influence_objects, mesh, r=True)
		mesh_skin = pm.skinCluster(tsb=True, mi=3, dr=4.0, n=f'{mesh}SkClus')

	for index, bind_input in zip(range(influence_count), bind_inputs):
		if bind_input:
			bind_input = pm.PyNode(bind_input)
			try_matrix_connect(bind_input, mesh_skin.bindPreMatrix[index])

	## set weights
	skin_mfn    = get_mfn_skin(mesh_skin)
	mesh_mfn    = get_mfn_mesh(mesh_shape)
	mesh_dp     = get_dag_path(mesh_shape.longName())
	components  = get_complete_components(mesh_mfn)
	all_indices = om2.MIntArray(range(influence_count))

	skin_mfn.setWeights(mesh_dp, components, all_indices, weights)
	
	## I know we saved and loaded these ourselves but due to how floating point
	## numbers work, you've likely introduced a tiny bit of drift that will show
	## up when the character is moved a great distance. Normalizing now will
	## alleviate this and you won't see a visible difference.  Hopefully.
	pm.skinPercent(mesh_skin, mesh_shape, normalize=True)
	
	## This is super important-- thanks Sophia Zauner for the hint
	## In recent versions of Maya if you don't recache bind matrices
	## (which I believe loads them on the GPU) then it's a russian
	## roulette game wrt whether the skin will look correct
	## when you hit play.
	mesh_skin.recacheBindMatrices()

	om2.MGlobal.displayInfo(f'+ Loaded skin weights for {mesh} from {path}')


## ======================================================================
def copy_skin_weights(source, source_skin, target, target_skin):
	source_shape = get_deform_shape(source)
	source_dp    = get_dag_path(source_shape.longName())
	source_mfn   = get_mfn_skin(source_skin)
	source_mesh  = get_mfn_mesh(get_deform_shape(source))
	components   = get_complete_components(source_mesh)

	weights, influence_count = source_mfn.getWeights(source_dp, components)

	## copy over input values / connections
	bind_inputs = [ (x.inputs(plugs=True)[0] if x.isConnected() else None) for x in source_skin.bindPreMatrix ]
	bind_values = [ x.get() for x in source_skin.bindPreMatrix ]
	mat_inputs  = [ (x.inputs(plugs=True)[0] if x.isConnected() else None) for x in source_skin.matrix ]
	mat_values  = [ x.get() for x in source_skin.matrix ]

	for index, bind_value, mat_value in zip(range(influence_count), bind_values, mat_values):
		## can't be guaranteed what state things will be in at this point
		## so set them in a try/catch
		try_matrix_set(target_skin.bindPreMatrix[index], bind_value)
		try_matrix_set(target_skin.matrix[index], mat_value)

	for index, bind_input, mat_input in zip(range(influence_count), bind_inputs, mat_inputs):
		if bind_input:
			try_matrix_connect(bind_input, target_skin.bindPreMatrix[index])
		if mat_input:
			try_matrix_connect(mat_input, target_skin.matrix[index])

	## copy over weights
	target_mfn   = get_mfn_skin(target_skin)
	target_shape = get_deform_shape(target)
	target_mesh  = get_mfn_mesh(target_shape)
	target_dp    = get_dag_path(target_shape.longName())
	components   = get_complete_components(target_mesh)
	all_indices  = om2.MIntArray(range(influence_count))
	
	target_mfn.setWeights(target_dp, components, all_indices, weights)

	## same as with loading and saving, we want to normalize and 
	## recache the bind matrices
	pm.skinPercent(target_skin, target_shape, normalize=True)
	target_skin.recacheBindMatrices()


# ----------------------------------------------------------------------------------------------------------------------
def copy_skin_layer(source, target):
	"""

		Args:
			source ():
			target ():
	"""

	## bugfix:
	## Building the first skincluster on a mesh manually is a Bad Idea.
	## Not sure what else gets set by the command, but if you don't instead
	## allow the command to make the skin and then move the weights you run
	## into issues.

	source_skin = get_skin_cluster(source)

	if source_skin:

		all_target_skins = list(filter(lambda x: x.type() == "skinCluster", get_deformers_for_shape(target)))

		if len(all_target_skins):
			target_skin = pm.deformer(target, type='skinCluster', n='MERGED__' + source_skin.name())[0]

		else:
			# No skins yet-- make sure to use this command
			source_influences = source_skin.influenceObjects()
			pm.select(source_influences, target, r=True)
			target_skin = pm.skinCluster(tsb=True, mi=3, dr=4.0, n=f'{target}SkClus')

		# Never don't neighbours
		target_skin.weightDistribution.set(1) ## neigbours

		copy_skin_weights(source, source_skin, target, target_skin)





# ----------------------------------------------------------------------------------------------------------------------
def transfer_skins(mesh, layer_meshes):
	"""

		Args:
			mesh ():
			layer_meshes ():
	"""

	clean_deformation(mesh)

	
	for layer_mesh in layer_meshes:
		copy_skin_layer(layer_mesh, mesh)





# ----------------------------------------------------------------------------------------------------------------------
def get_layer_transforms(search_string=gLayer_re):
	"""
		Finds and returns all "LAYER_#" transform nodes in the scene.
		Args:
			search_string (string): The string to search for in DAG nodes.
		Returns:
			(list) All found "LAYER_#" transform nodes.
	"""

	result = [x for x in gExtras.getChildren() if search_string.match(str(x))]

	return result





# ----------------------------------------------------------------------------------------------------------------------
def mesh_to_face_layers(mesh, connect_original=False):
	"""
		Populates 'LAYER_#' groups in 'gExtras' group with duplicate meshes and initializes their skin clusters with
			dummy joints, then strings them together in a chain of blend shapes.
			Later, other functions can collapse them into a single chain of nested skin clusters so that the deformation
			is GPU compatible.
		Args:
			mesh (string): Joint name.
			connect_original (numeric): Joint radius.
	"""

	mesh = pm.PyNode(mesh)
	# Get transform
	if mesh.type() == "mesh":
		mesh = mesh.getParent()


	all_duplicates = []

	for layer in get_layer_transforms():
		layer_name = str(layer)
		dummy_name = layer_name + "_DUMMY"
		duplicate_name = "_".join((layer_name, str(mesh)))
		
		# Fail early if the name already exists
		assert not pm.objExists(duplicate_name), "{0} already exists.".format(duplicate_name)

		# Add dummy joints to hold skin weights
		if not pm.objExists(dummy_name):
			dummy = pm.createNode("joint", name=dummy_name)
			pm.parent(dummy, layer)

		# Create duplicate mesh
		duplicate = pm.duplicate(mesh, rr=True)[0]
		duplicate.rename(duplicate_name)
		duplicate.setParent(layer)
		
		all_duplicates.append(duplicate)


	# BlendShape chaining
	all_duplicates = list(sorted(all_duplicates))

	for index in range(1,len(all_duplicates)):
		source = all_duplicates[index-1]
		target = all_duplicates[index]
		pm.blendShape( source, target, weight=(0, 1), before=True, name="{0}_INPUT".format(target) )
	
	if connect_original:
		# Connect to original mesh
		pm.blendShape( all_duplicates[-1], mesh, weight=(0, 1),	before=True, name="{0}_INPUT".format(mesh) )





# ----------------------------------------------------------------------------------------------------------------------
def get_deform_shape(obj):
	"""
		Gets the visible geometry shape regardless of whether the object is deformed or not.
		Args:
			obj (object): The object to get deformed shape from.
		Return:
			(shape node) The found deformed shape.


	"""
	obj = pm.PyNode(obj)
	if obj.type() in ["nurbsSurface", "mesh", "nurbsCurve"]:
		obj = obj.getParent()

	shapes = pm.PyNode(obj).getShapes()
	if len(shapes) == 1:
		return shapes[0]

	else:
		real_shapes = [x for x in shapes if not x.intermediateObject.get()]
		return real_shapes[0] if len(real_shapes) else None





# ----------------------------------------------------------------------------------------------------------------------
def get_deformers_for_shape(item):
	"""
		Get the deformers from an object's history that only effect that particular mesh, and not inputs from other
			meshes (i.e. meshes driving blendShapes).
		Args:
			item (dag object): The object to get deformers on.
		Return:
			(list) Found deformers.
	"""

	result = []

	# Get deformer history
	geometry_filters = pm.ls(pm.listHistory(item), type="geometryFilter")

	# Get deformed shape of item
	shape = get_deform_shape(item)

	shape_sets = None
	if shape:
		shape_sets = pm.ls(pm.listConnections(str(shape)), type="objectSet")

	if not shape_sets:
		return

	for deformer in geometry_filters:
		def_set = pm.ls(pm.listConnections(deformer), type="objectSet")[0]
		if def_set in shape_sets:
			result.append(deformer)

	return result






# ----------------------------------------------------------------------------------------------------------------------
def get_skin_cluster(item):

	deformers = get_deformers_for_shape(item)

	if not deformers:

		return None

	else:

		skins = list(filter(lambda x: x.type() == "skinCluster", deformers))

		assert len(skins) < 2, "Cannot use get_skin_cluster on meshes with stacked skins."

		skin = skins[0] if len(skins) else None
		if skin:
			## I got into the habit of doing this any time
			## I touch a skin. Neighbors should be the
			## default but AD doesn't want to change old
			## workflows.
			skin.weightDistribution.set(1) ## neigbours

		return skin






# ----------------------------------------------------------------------------------------------------------------------
def get_layer_shapes_for_mesh(mesh):
	"""
		Gets mesh objects from extras layer groups.
		Args:
			mesh (transform/shape):
		Return:
			(list) all found meshes.
	"""

	layers = get_layer_transforms()
	all_children = sum([x.getChildren() for x in layers], [])
	mesh_targets = filter(lambda x:x.ctrl_name_tag().endswith(mesh.rpartition(":")[-1]), all_children)

	return list(mesh_targets)





# ----------------------------------------------------------------------------------------------------------------------
def clean_deformation(x):

	pm.delete(get_deformers_for_shape(x))


## ======================================================================
## build

"""
import face_cake_setup as fcs

target = "body_GEO"

## Set up the duplicate editing system
fcs.mesh_to_face_layers(target)

skins = [
	"LAYER_0_body_GEO",
	"LAYER_1_body_GEO",
	"LAYER_2_body_GEO",
]

## run only when saving skins out
# for skin in skins:
# 	fcs.save_skin_weights(skin)

for skin in skins:
	fcs.load_skin_weights(skin, rebind=True)

## you can also get the layers shapes for the target directly
layer_shapes = fcs.get_layer_shapes_for_mesh(target)

## and this does the final transfer
fcs.transfer_skins(target, layer_shapes)

"""