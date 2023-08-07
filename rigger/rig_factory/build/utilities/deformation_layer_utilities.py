import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.rigger.rig_factory.objects.deformation_stack_objects.deformation_stack as stk


def set_evaluation_settings():
    """Sets the eval mode *DG* and *GPU Override* to *Disabled*"""

    controller = com.controller_utilities.get_controller()
    controller.scene.evaluationManager(mode="off")  # Set to DG
    controller.scene.optionVar(intValue=["gpuOverride", 0])


def connect_stack_layers(entity_name):
    """Connects the stack layers based on the values defined in the plugs dictionaries of its member layers.
    It also needs to fix the issue with the shader getting lost.
    ToDo: Add fix shader logic here | Sometimes connecting layers causes a bug where the texture of the product mesh
    turns green as if it had no shader despite it having one.
    """

    deformation_stack = get_stack_from_entity_name(entity_name)  # type: stk.DeformationStack

    # Only run logic if the entity does have deformation layers
    if not deformation_stack:
        return None

    # Update the info based on the loaded deformers
    deformation_stack.update_layers_info(inspect_in_between_meshes=True)

    # Get and raise any warnings that may arise when trying to connect the self
    conflict_geometries = deformation_stack.connect_stack_layers(skip_meshes_without_deformers=False)

    if not conflict_geometries:
        return None

    warning_lines = [
        'There are some incoming connections to some product meshes!',
        'Check if the following are being deformed or have been tagged as Origin Geometries.',
        "\n Skipping: {}".format(sorted([str(x) for x in conflict_geometries]))
    ]
    return dict(
        status="warning",
        warning='\n'.join(warning_lines)
    )


def finalize_deformation_stack(entity_name):
    """Optimizes the deformation stack by deleting all in-between meshes inside of it that only serve the purpose of
    being an interface for the rigger to edit. This way the stack becomes GPU-friendly.

    .. _finalize_deformation_stack:
    """
    controller = com.controller_utilities.get_controller()

    deformation_stack = get_stack_from_entity_name(entity_name)

    # Only run logic if the entity does have deformation layers
    if not deformation_stack:
        return None

    # Update the stack after all meshes are chained
    deformation_stack.update_layers_info(inspect_in_between_meshes=False)

    # stack with no meshes without deformers
    deformation_stack.connect_stack_layers(skip_meshes_without_deformers=True)
    deformation_stack.finalize_stack()

    controller.delete_scheduled_objects()


def get_stack_from_entity_name(entity_name):
    """Get the stack being constructed during the build process out of the entity name.

    Args:
        entity_name (str): The name of the build.

    Returns:
        DeformationStack: The currently active deformation stack.
    """

    controller = com.controller_utilities.get_controller()

    # filters the only stack that belongs to the current working entity and casts it into a list
    entity_stack = list(filter(
        lambda x: "_{}_".format(entity_name.replace("_", "")
                                ) in x.name, controller.root.deformation_stacks.values()))

    if not len(entity_stack):
        return None

    return entity_stack[0]
