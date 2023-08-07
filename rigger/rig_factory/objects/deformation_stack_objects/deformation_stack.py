"""Dictionary of all the types of nodes that are compatible with the deformation layers system. You can add new ones by
appending a new class as a key and the plug names that are going to be used when making connections.

The syntax to use this might be a bit cumbersome but here's an example:

.. codeblock:: python

   my_object.plugs[my_object.__class__]['in']

As you can see the, you can use the `__class__` magic method from the object you need to dynamically need to get a plug
to easily get the class required as a key for the dictionary.

.. important:: Right now only mesh type nodes are supported. All plugs inside the deformation stack logic still need to
    be parametrized.
This file defines a new type of object that symbolizes the Deformation Stack.

This object is responsible for the following operations:

- Creating deformation layers and populate them with copies of the product geometry.

- Looking through the defined layers and connect them in the specified order.

- Finalizing the stack (a.k.a deleting in between meshes and chaining the deformers).

- Inside this file we also have utility functions that prepare data from the blueprint like sorting the dictionary of
  layers or getting the correct deformation stack when dealing with builds that have parent assets.
"""


import re
import weakref

import typing
import logging
import collections
import Snowman3.rigger.rig_factory.common_modules as com
from Snowman3.rigger.rig_factory.objects.node_objects.plug import Plug
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty


TYPE_IN_OUT_PLUGS_DICT = {
    Mesh: {"in": "inMesh", "out": "outMesh", "secondary_out": "worldMesh"},
    NurbsSurface: {"in": "create", "out": "worldSpace", "secondary_out": "Local"},
    NurbsCurve: {"in": "create", "out": "worldSpace", "secondary_out": "Local"}
}

"""Type for any node object that subclasses Transform, including Transform itself."""
N = typing.TypeVar("N", bound=Transform)


class DeformationLayer(Transform):
    """Object that describes an outliner group with a set of children meshes in order to be rigged by the same setup.

    Attributes:
        meshes_and_plugs_dict (Dict[Dict[str, Plug]]): A dictionary where the keys are the layer's member meshes and the
            keys are the plugs that will be used to connect them amongst one another.

    .. _DeformationLayer:
    """

    meshes_and_plugs_dict = {}

    layer_transforms = ObjectListProperty(name="layer_meshes")

    layer_meshes = ObjectListProperty(name="layer_meshes")

    node_type = DataProperty(
        name="node_type",
        default_value="deformationLayer"
    )

    suffix = "Lyr"

    def __init__(self, *args, **kwargs):
        """

        Args:
            name (str): The name of the layer.

            parent (obs.Transform): The parent transform where the layer is
                going to get created. Usually the DeformationStack's transform. *args: **kwargs:
        """
        super(DeformationLayer, self).__init__(*args, **kwargs)
        self.meshes_and_plugs_dict = {}

    def create_mesh_transform(self, segment_name, differentiation_name, base_mesh):
        """Creates a transform and adds it inside the layer meshes.

        Args:
            segment_name (str): The name of the mesh without suffix.
            base_mesh (obs.Mesh): The product mesh that the transform is going to target to create it's own mesh
                object.
            differentiation_name (str): The name of the layer without suffix.
        """

        child_transform = super(DeformationLayer, self).create_child(
            Transform,
            suffix="Geo",
            segment_name=segment_name,
            differentiation_name=differentiation_name
        )  # type: Transform

        # Add a reference to the original mesh that this transform is going to be copying when creating the meshes
        child_transform.relationships["base_mesh"] = base_mesh

        # Give useful pointers to the deformation layer that it belongs to
        child_transform.relationships["deformation_layer"] = self

        self.layer_transforms.append(child_transform)
        return child_transform

    def create_mesh_for_transform(self, mesh_transform_object):
        """Creates the mesh node for the transform. And adds its inMesh and worldMesh plugs to the dictionaries of
        plugs.

        Args:
            mesh_transform_object (transform.Transform): The parent transform for the newly-created mesh.

        Returns:
            mesh.Mesh: The mesh object child of the created transform.
        """

        # Guarantee that the object has a pointer to the base mesh that it is going to be copying
        if not mesh_transform_object.relationships.get("base_mesh", False):
            msg = "Could not find any base mesh for layer: {}".format(mesh_transform_object.name)
            logging.getLogger("rig_build").critical(msg=msg)
            raise AttributeError(msg)

        logging.getLogger('rig_build').info(
            'Copying mesh: %s %s' % (
                mesh_transform_object.name,
                mesh_transform_object.get_selection_string()
            )
        )

        # Get the base mesh object and copy it
        base_mesh = self.controller.named_objects[
            mesh_transform_object.relationships["base_mesh"].name]  # type: Mesh
        if not isinstance(base_mesh, Mesh):
            raise KeyError("The base mesh object %s is not of type `Mesh`.", base_mesh)

        # Tagging the root_geometry for later
        base_mesh.__dict__.setdefault("is_product_geometry", True)  # hacks, hacks

        child_mesh = self.controller.copy_mesh(
            base_mesh.name,
            mesh_transform_object,
            name="%sShape" % mesh_transform_object.name
        )  # type: Mesh

        # Add relationships to the mesh that it's being copied
        child_mesh.relationships["base_mesh"] = child_mesh.parent.relationships["base_mesh"]

        # Create empty entrance to the orig mesh. This will get updated after the deformers are loaded onto the layer.
        mesh_transform_object.relationships["member_mesh"] = child_mesh
        mesh_transform_object.relationships["orig_mesh"] = child_mesh

        # Assign familiar origin geometry shader
        child_mesh.assign_shading_group(
            self.controller.root.shaders['origin'].shading_group
        )

        # Registers mesh within the container to save the deformers attached to it
        self.controller.root.geometry[child_mesh.name] = child_mesh

        # Initialize input / output plugs
        type_attrs_dict = TYPE_IN_OUT_PLUGS_DICT[child_mesh.__class__]

        self.meshes_and_plugs_dict[child_mesh.name] = {
            "in": child_mesh.plugs[type_attrs_dict["in"]],
            "out": child_mesh.plugs[type_attrs_dict["out"]],
        }
        self.layer_meshes.append(child_mesh)

        return child_mesh


def create_deformation_layers(deformation_layers_data, entity_name):
    """Creates a deformation stack and the layers that make it up. Then it assigns them a different rig shader.

    Format of the data = (dict[str, list[list[str], int]):

    Args:
        deformation_layers_data (Dict[str: List[List[str], int]]): The deformation data from the blueprint.
        entity_name (str): The name of the build entity, it gets added as a naming element.
    """
    if not deformation_layers_data:
        return None

    controller = com.controller_utilities.get_controller()
    logger = logging.getLogger("rig_build")

    # Add a namespace to the name if the controller has a namespace
    if controller.namespace:
        updated_names_dict = {}
        for layer_name in deformation_layers_data:
            updated_layer_name = '{}:{}'.format(controller.namespace, layer_name)
            layer_items = deformation_layers_data[layer_name]
            updated_layer_items = [["{}:{}".format(controller.namespace, x[0]), x[1]] for x in layer_items]

            updated_names_dict[updated_layer_name] = updated_layer_items
        deformation_layers_data = updated_names_dict

    # Order the dict, by the index value
    ordered_data = order_deformation_layers_data(deformation_layers_data)

    # deformation_stack = DeformationStack(controller)
    deformation_stack = controller.root.utility_geometry_group.create_child(
        DeformationStack,
        segment_name="DeformationStack",
        subsidiary_name=entity_name.replace("_", ""),
    )  # type: DeformationStack

    deformation_stack.create_transforms(ordered_data)
    deformation_stack.create_meshes()

    # Should happen at the very end
    controller.root.deformation_stacks[deformation_stack.name] = deformation_stack

    logger.info("Finished creating the deformation stack members.")

    return deformation_stack



class DeformationStack(Transform):
    """This object defines an ordered container for :ref:`Deformation Layer objects <DeformationLayer>`.

    The order of the layers is relevant to how these are going to be connected during the build.

    .. _DeformationStack:
    """

    stack_deformation_layers = DataProperty(
        name="stack_deformation_layers",
        default_value=[]
    )

    node_type = DataProperty(
        name="node_type",
        default_value="deformationStack"
    )

    stack_base_meshes = weakref.WeakSet()

    suffix = "Grp"

    def __init__(self, **kwargs):
        """

        Args:
            controller (RigController): The active controller.

        Keyword Args:
            entity_name (str): The name of the entity from the build.
        """
        super(DeformationStack, self).__init__(**kwargs)
        self.stack_base_meshes = weakref.WeakSet()

    def create_transforms(self, deformation_layers_data=None):
        """Creates the transforms of all the layers inside given data.

        Args:
            deformation_layers_data (Dict[str, List[str, int]]): The dictionary that contains the names of layers and
                a list of their member meshes, paired with their index within the stack.
        """

        if not deformation_layers_data:
            deformation_layers_data = order_deformation_layers_data(self.controller.root.deformation_layers)

        for layer_name, values in deformation_layers_data.items():

            # Initialize and create layer (transform) object
            layer_object = self.create_child(
                DeformationLayer,
                segment_name=layer_name,
            )  # type: DeformationLayer

            # Create one transform node per mesh inside the list of meshes of the layers
            for mesh_transform_name in values[0]:

                # Raise an error if the mesh name doesn't belong to any object in the scene
                base_mesh_object = self.controller.named_objects.get(mesh_transform_name, None)
                if base_mesh_object:
                    self.stack_base_meshes.add(
                        base_mesh_object.get_children(
                            Mesh,
                            NurbsSurface,
                            NurbsSurface
                        )[0]
                    )
                else:
                    raise KeyError("Invalid mesh: {} | amongst saved deformation layers!".format(mesh_transform_name))

                # Strip the suffix to clean the mesh name when generating the groups
                pruned_name = mesh_transform_name.split("_Geo")[0]

                layer_object.create_mesh_transform(
                    segment_name=pruned_name,
                    differentiation_name=layer_name,
                    base_mesh=self.controller.named_objects["{}Shape".format(mesh_transform_name)]
                )

            self.stack_deformation_layers.append(layer_object)

    def create_meshes(self):
        """Creates a mesh node for every existing member transform inside a layer in the stack.

        The mesh node is also a copy of a specified product mesh.
        """

        for layer in self.stack_deformation_layers:  # type: DeformationLayer
            for trn in layer.layer_transforms:
                layer.create_mesh_for_transform(trn)
            logging.getLogger("rig_build").info("Created meshes for layer: {}".format(layer.name))

    def connect_stack_layers(self, skip_meshes_without_deformers=False):
        """For each of the product's meshes, traces back the copies of the mesh within the deformation layer stack and
        connects the aforementioned nodes in the order defined inside the widget.

        If the mesh that is currently being inspected is receiving a connection inside its `.inMesh` attribute it is
        going to be returned so that the rigger knows that there is some action that needs to be taken care of like
        untagging it as origin geo, removing deformers from the product mesh, etc... .

        Args:
            skip_meshes_without_deformers (bool): If set to True, when connecting members of different layers it will
                ignore those that don't have a deformer attached and look for the next member that does have one. If it
                is the last member mesh of the stack it will still connect it.

        Returns:
            typing.List[str]: A list of strings containing the problematic meshes that will be skipped when connecting
            layers.
        """

        warning_meshes = []

        # Will look down the stack from the product meshes and will connect the meshes that have been copied.
        for msh in self.stack_base_meshes:
            if not hasattr(msh, "is_product_geometry"):
                continue

            # Check if the mesh has an input connection to its inMesh plug
            input_connection = self.controller.scene.listConnections(
                msh.plugs[TYPE_IN_OUT_PLUGS_DICT[msh.__class__]["in"]].name,
                source=True,
                destination=False,
            )
            input_node = None
            if input_connection:
                input_node = self.controller.named_objects.get(input_connection[0], None)

            # Buffer logic for origin geometry compatibility and current deforms on product meshes.
            # Nodes that will pass through this filter are those that are not receiving an incoming connection
            # and hold a pointer to a deformation layer
            if msh.parent.name in self.controller.root.origin_geometry_data.keys():
                warning_meshes.append(msh.parent.name)
                continue
            # If there is not input node the geo is good to be used for connecting
            elif input_node:
                if input_node.relationships.get("deformation_layer", None):
                    pass
                else:
                    warning_meshes.append(msh.parent.name)
                    continue

            # First layer member is the product element, thus get it from the dict
            previous_layer_member_in_plug = msh.plugs[TYPE_IN_OUT_PLUGS_DICT[msh.__class__]["in"]]

            # Matches are meshes from DeformationLayer objects, thus you can get the inputs and outputs of the layer
            for match in self._find_product_copy_in_layers(msh):

                # In case some layer doesnt have a deformer, skip them if they are not the first mesh in the stack
                if skip_meshes_without_deformers:
                    orig_mesh = match.parent.relationships["orig_mesh"]
                    member_mesh = match.parent.relationships["member_mesh"]

                    if orig_mesh == member_mesh:
                        if self.controller.scene.listConnections(member_mesh.plugs["inMesh"].name, source=True):
                            continue

                layer_member_in_out_plugs = match.parent.parent.meshes_and_plugs_dict[match.name]

                out_plug = layer_member_in_out_plugs["out"]  # type: Plug

                logging.getLogger("rig_build").info(
                    "==== Connect {} -> {} ====".format(out_plug,
                                                        previous_layer_member_in_plug)
                )

                # Disconnecting plugs is quite buggy so I'll do that through cmds
                incoming_connection = self.controller.scene.listConnections(previous_layer_member_in_plug.name,
                                                                            source=True,
                                                                            plugs=True)

                if incoming_connection:
                    self.controller.scene.disconnectAttr(incoming_connection[0], previous_layer_member_in_plug.name)

                self.controller.scene.connectAttr(out_plug.name,
                                                  previous_layer_member_in_plug.name,
                                                  force=True)

                previous_layer_member_in_plug = layer_member_in_out_plugs["in"]

            # noinspection PyUnusedLocal
            previous_layer_member_in_plug = msh

        return warning_meshes

    def finalize_stack(self):
        """Cleans up the stack of meshes that only serve the purpose of being an interface for the rigger to edit
        weights.

        This function only tags objects for deletion. The actual destruction coll is made inside the :ref:`finalize
        deformation stack utility function <finalize_deformation_stack>`.

        Returns:
            List[Mesh]: A list of the meshes that will be pruned and set to be deleted.
        """

        del_list = []

        for deform_layer in self.stack_deformation_layers:  # type: DeformationLayer
            for layer_member in deform_layer.layer_transforms:

                # The transform node should hold a relationship link to the orig geo object if there is one
                orig_mesh_obj = layer_member.relationships.get("orig_mesh", None)
                member_mesh_obj = layer_member.relationships.get("member_mesh", None)

                # Putting these into a set will make sure that if they are the same node it's there only once
                for mesh in filter(None, {orig_mesh_obj, member_mesh_obj}):

                    connection_source = self.controller.scene.listConnections(
                        mesh.plugs[TYPE_IN_OUT_PLUGS_DICT[mesh.__class__]["in"]].name,
                        source=True,
                        plugs=True)

                    if not connection_source:
                        out_connection_destination = self.controller.scene.listConnections(
                            mesh.plugs[TYPE_IN_OUT_PLUGS_DICT[mesh.__class__]["secondary_out"]].name,
                            destination=True,
                            plugs=True
                        )
                        if out_connection_destination:
                            for each in out_connection_destination:
                                self.controller.scene.connectAttr(
                                    mesh.plugs[TYPE_IN_OUT_PLUGS_DICT[mesh.__class__]["out"]].name,
                                    each,
                                    force=True
                                )
                        continue

                    # If there is a connection to the node, delete it
                    self.controller.scene.disconnectAttr(
                        connection_source[0],
                        mesh.plugs[TYPE_IN_OUT_PLUGS_DICT[mesh.__class__]["in"]].name)

                    del_list.append(mesh)

        self.controller.schedule_objects_for_deletion(del_list)
        return del_list

    # ==== PRIVATE LOGIC ===============================================================================================

    def _find_product_copy_in_layers(self, base_mesh):
        """Generator that yields objects inside the deformation layers that have been copied from a given base object.
        That object is normally a mesh.

        Args:
             base_mesh (N): Any of the product's meshes.

        Yields:
            mesh.Mesh: Any mesh object that has been copied from the same base mesh as the given layer transform/mesh.
        """

        for layer in self.stack_deformation_layers:
            for msh in layer.layer_meshes:
                if msh.relationships["base_mesh"].name == base_mesh.name:
                    yield msh

    # ==== CONNECTION ORDERING UTILS ===================================================================================

    # noinspection PyTypeChecker
    def update_layers_info(self, inspect_in_between_meshes=True):
        """Updates the deformation stack to reflect the deformers and new orig meshes after these have been imported
        in the build.

        .. warning::
            This part of the code is potentially dangerous as it initializes objects that can get out of sync with the
            current state of the Maya scene after the user's interaction.

            Deleting a skinCluster inside Maya and immediately finalizing the rig is going to break it. To avoid it the
            logic needs a different system to query the *in* and *out* plugs but for the moment the user will have to
            save and rebuild the rig if that is the case.

        .. note::
            Despite potentially dangerous, if another skinCluster is created replacing the old one the finalize process
            will work.

        Args:
            inspect_in_between_meshes (bool): Whether or not to include meshes in the plugs and meshes inspection.

        """

        for deform_layer in self.stack_deformation_layers:  # type: DeformationLayer
            for layer_member in deform_layer.layer_transforms:  # type: Transform

                in_object_in_plug = None
                out_object_out_plug = None

                # If any, get the orig geometry of the layer transform
                orig_geo_object = register_orig_mesh_as_object(layer_member)

                # If we want to include meshes the in and out objects will be the meshes, otherwise it will be the
                # deformers loaded onto the meshes

                orig_mesh = layer_member.relationships["orig_mesh"]
                member_mesh = layer_member.relationships["member_mesh"]

                # If orig_geo_object has a return value, it means it has a deformer attached to it so you must get it
                if orig_geo_object and not inspect_in_between_meshes:
                    group_parts_in_plug, deformer_out_plug = get_deformer_from_mesh(layer_member)

                    in_object_in_plug = group_parts_in_plug  # type: Plug
                    out_object_out_plug = deformer_out_plug  # type: Plug

                if not in_object_in_plug and not out_object_out_plug:
                    in_object_in_plug = orig_mesh.plugs[
                        TYPE_IN_OUT_PLUGS_DICT[orig_mesh.__class__]["in"]]

                    out_object_out_plug = member_mesh.plugs[
                        TYPE_IN_OUT_PLUGS_DICT[orig_mesh.__class__]["out"]]

                    # Some plugs are array plugs. If this is the case it gets the first element.
                    # E.g. worldMesh // really gets connected to -> worldMesh[0]
                    if out_object_out_plug.is_array():
                        out_object_out_plug = out_object_out_plug.element(0)

                # Update the layer plugs dictionary
                deform_layer.meshes_and_plugs_dict[
                    layer_member.relationships["member_mesh"].name] = {"in": in_object_in_plug,
                                                                       "out": out_object_out_plug
                                                                       }

        return None


# ==== DATA SORTING AND FILTERING ======================================================================================

def order_deformation_layers_data(data):
    """Transforms the deformation layers data dict into an ordered one and spits it back.

    Args:
        data (Dict[str: List[List[str], int]]): The data from the blueprint related to deformation layers construction.

    Returns:
        Dict[str: List[List[str], int]]: Ordered dict based on the index inside the values of each key.
    """

    return collections.OrderedDict(sorted(data.items(), key=lambda index: index[1][1]))


# ==== LAYER UTILITIES =================================================================================================

def register_orig_mesh_as_object(parent_transform):
    """Looks for children meshes of a given transform node. If the node has more than 1 mesh and the other ones are not
    registered, it will convert the origin ones into framework objects.

    This hasn't been made compatible with other types of nodes like surfaces and curves.

    Args:
        parent_transform (Transform):

    Returns:
        typing.Optional[Mesh]: The Orig mesh (if any). Otherwise None.
    """

    # Create mesh object that points to the Orig mesh
    controller = com.controller_utilities.get_controller()
    children_meshes = controller.scene.listRelatives(parent_transform.name, children=True)

    if not children_meshes or len(children_meshes) == 1:
        return None

    # Filter the orig mesh from the transform children
    orig_mesh_name = list(filter(lambda x: x not in controller.named_objects, children_meshes))
    if len(orig_mesh_name) == 0:
        orig_mesh_name = [y for y in children_meshes if "_Msh" in y or "Orig" in y]
    orig_mesh_name = orig_mesh_name[0]

    # Load the object from the name
    in_mesh_object = controller.named_objects.get(orig_mesh_name, None)
    if not in_mesh_object:
        orig_mesh_m_object = controller.scene.get_m_object(orig_mesh_name)
        in_mesh_object = parent_transform.create_child(Mesh,
                                                       m_object=orig_mesh_m_object)

    # Update the transform's pointers to the origin mesh if there is a new object
    parent_transform.relationships["orig_mesh"] = in_mesh_object if in_mesh_object else \
        parent_transform.relationships["member_mesh"]

    return in_mesh_object


def get_deformer_from_mesh(parent_transform):
    """Looks for the input and output of a deformer combination of nodes. If such deformer exists, the function will
    return a pair of nodes to connect the input and the output.

    Args:
        parent_transform (Transform): A transform member of any deformation layer.

    Returns:
        List[Plug]: Depending if the input member transform contains a deformer node, it will
            return the input and output nodes of the deformer or None.
    """

    controller = com.controller_utilities.get_controller()

    orig_mesh = parent_transform.relationships["orig_mesh"]  # type: Mesh
    member_mesh = parent_transform.relationships["member_mesh"]  # type: Mesh

    # Query that the orig mesh is not equal to the member mesh. If not it means the mesh has a deformer
    if orig_mesh == member_mesh:
        return None, None

    # Get the plugs connected to these objects as framework objects

    # Deformer out plug and index
    deformer_node_str, deformer_plug_name = controller.scene.listConnections(
        member_mesh.plugs[TYPE_IN_OUT_PLUGS_DICT[member_mesh.__class__]["in"]].name,
        source=True,
        plugs=True
    )[0].split(".")

    # Matches any number as a str surrounded by []. Then it splits it to separate the name and the index.
    deformer_plug_name, deformer_plug_index, _ = re.split('\\[([0-9]*?)]', deformer_plug_name)
    deformer_plug_index = int(deformer_plug_index)

    # Deformer group parts
    group_parts_node_str, group_parts_plug_name = controller.scene.listConnections(
        orig_mesh.plugs[TYPE_IN_OUT_PLUGS_DICT[orig_mesh.__class__]["secondary_out"]].name,
        destination=True,
        plugs=True
    )[0].split(".")

    # Convert str plugs into FW objects
    deformer_as_obj = controller.named_objects.get(deformer_node_str, None)
    if not deformer_as_obj:
        deformer_as_obj = controller.create_object(DependNode,
                                                   segment_name="{}{}".format(
                                                       deformer_node_str[0].upper(), deformer_node_str[1:]),
                                                   m_object=controller.scene.get_m_object(
                                                       deformer_node_str))  # type: DependNode

    # Set relationships
    deformer_as_obj.relationships.setdefault("deformation_layer", member_mesh.parent.relationships["deformation_layer"])
    member_mesh.parent.relationships.setdefault("member_deformer", deformer_as_obj)

    deformer_out_plug = deformer_as_obj.plugs[deformer_plug_name].element(deformer_plug_index)  # type: Plug

    group_parts_as_obj = controller.named_objects.get(group_parts_node_str, None)
    if not group_parts_as_obj:
        group_parts_as_obj = controller.create_object(DependNode,
                                                      name=group_parts_node_str,
                                                      m_object=controller.scene.get_m_object(
                                                          group_parts_node_str))  # type: DependNode

    group_parts_in_plug = group_parts_as_obj.plugs[group_parts_plug_name]  # type: Plug

    return group_parts_in_plug, deformer_out_plug
