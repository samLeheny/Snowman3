import importlib
import Snowman3.rigger.rig_factory.objects.node_objects.depend_node as depend_node
importlib.reload(depend_node)
DependNode = depend_node.DependNode
import Snowman3.rigger.rig_factory.objects.base_objects.properties as properties
ObjectProperty = properties.ObjectProperty

class DagNode(DependNode):

    shader = ObjectProperty( name='shader' )
    visible = True


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visible = True


    def assign_shading_group(self, shading_group):
        self.controller.assign_shading_group(shading_group, self)


    def get_dag_path(self):
        return self.controller.get_dag_path(self)


    def create_in_scene(self):
        parent_obj = None
        if isinstance(self.parent, DagNode):
            parent_obj = self.parent.m_object
        self.m_object = self.controller.create_m_depend_node(
            node_type=self.node_type,
            name=self.name,
            parent=parent_obj
        )


    def set_m_object(self, m_object):
        super().set_m_object(m_object)
        self.update_parent()


    def update_parent(self):
        if self.parent:
            # Make sure self and parent mObjects are parented.
            if isinstance(self.parent, DagNode):
                get_parent_name = self.controller.scene.listRelatives(self.name, p=True)
                actual_parent_name = None
                if get_parent_name:
                    actual_parent_name = get_parent_name[0]
                parent_string = self.parent.get_selection_string()
                if parent_string != actual_parent_name:
                    self.controller.scene.parent(self.get_selection_string(), parent_string)
            else:
                # Check mObject parent, connect to Framework object as parent.
                selection_string = self.get_selection_string()
                get_parent = self.controller.scene.listRelatives(selection_string, p=True)
                if get_parent:
                    parent_name = get_parent[0]
                    if parent_name in self.controller.named_objects:
                        parent = self.controller.named_objects[parent_name]
                    if self.parent != parent:
                        self.parent = parent
                        if self not in parent.children:
                            parent.children.append(self)
                        else:
                            self.controller.raise_warning(f"{self} was already a child of {parent}.")
                    else:
                        self.controller.raise_warning(f"{self} was already a parent of {parent}.")
                else:
                    raise Exception("You cannot 'set_m_object()' of a DagNode that doesn't have a parent.")
