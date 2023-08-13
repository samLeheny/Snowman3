from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty, ObjectListProperty
from Snowman3.rigger.rig_factory.objects.deformer_objects.deformer import Deformer


class NonLinear(Transform):

    deformer = ObjectProperty( name='deformer' )  # Use settings_node instead for setting values like 'startAngle' which may be connected in Maya 2020
    handle_transform = ObjectProperty( name='handle_transform' )
    handle_shape = ObjectProperty( name='handle_shape' )
    handle_type = DataProperty( name='handle_type' )
    settings_node = ObjectProperty( name='settings_node' )
    plug_values = dict()
    suffix = 'Nlr'
    deformer_type = None

    @classmethod
    def create(cls, **kwargs):
        this = super(NonLinear, cls).create(**kwargs)
        this.add_geometry(kwargs.get('geometry', []))
        return this

    def create_deformer(self, geometry):
        geometry = [str(x) for x in geometry]
        f = self.controller.scene.create_nonlinear_deformer
        deformer_m_object, handle_m_object, handle_shape_m_object, deformer_set_m_object = f(
            self.deformer_type,
            geometry
        )
        self.deformer = self.create_child(
            Deformer,
            m_object=deformer_m_object
        )

        self.handle_transform = self.create_child(
            Transform,
            m_object=handle_m_object
        )
        self.handle_shape = self.handle_transform.create_child(
            DagNode,
            m_object=handle_shape_m_object,
            suffix='Dhd'
        )
        # Settings are stored on the handle in Maya 2020, instead of the deformer as in earlier Maya versions
        # Eg. curvature (bend), highBound, lowBound, startAngle, endAngle
        # (If using the plugin squash, self.handle_shape is empty so self.deformer is used)
        self.settings_node = self.deformer
        if self.handle_shape and int(self.controller.scene.maya_version) >= 2020:
            self.settings_node = self.handle_shape

        for plug, value in self.plug_values.items():
            self.settings_node.plugs[plug].set_value(value)

        name_tokens = self.deformer.name.split('_')[0:-1]
        name_tokens.append('Set')
        self.controller.scene.rename(
            self.controller.scene.get_selection_string(deformer_set_m_object),
            '_'.join(name_tokens)
        )

    def __init__(self, **kwargs):
        super(NonLinear, self).__init__(**kwargs)

    def get_plug_values(self):
        plug_values = dict()
        if self.settings_node:
            for plug, value in self.plug_values.items():
                plug_values[plug] = self.settings_node.plugs[plug].get_value()
        return plug_values

    def update_plug_values(self, plug_values):
        if self.settings_node:
            for plug, value in plug_values.items():
                plugObj = self.settings_node.plugs[plug]
                if not plugObj.m_plug.isConnected:
                    plugObj.set_value(value)

    def get_weights(self, precision=None):
        if self.deformer:
            return self.deformer.get_weights(precision=precision)

    def set_weights(self, weights):
        if weights and not self.deformer:
            raise Exception('No deformer found. Unable to set weights')
        return self.deformer.set_weights(weights)

    def get_members(self):
        if self.deformer:
            return self.deformer.get_members()

    def set_members(self, members):
        if members:
            if not self.deformer:
                self.create_deformer(members.keys())
            self.deformer.set_members(members)

    def add_members(self, members):
        if members:
            if not self.deformer:
                self.create_deformer(members.keys())
                self.deformer.set_members(members)
            else:
                self.deformer.add_members(members)

    def add_geometry(self, geometry):
        if geometry:
            if self.deformer:
                self.deformer.add_geometry(geometry)
            else:
                self.create_deformer(geometry)

    def remove_geometry(self, geometry):
        if not self.deformer:
            raise Exception('No deformer found.')
        if sorted(geometry) == sorted(self.deformer.get_members().keys()):
            self.controller.schedule_objects_for_deletion(
                self.handle_transform,
                self.handle_shape,
                self.deformer
            )
            self.controller.delete_scheduled_objects()
        else:
            self.deformer.remove_geometry(geometry)

    def teardown(self):
        if self.deformer:
            self.controller.schedule_objects_for_deletion(
                self.handle_transform,
                self.handle_shape,
                self.deformer
            )
        super(NonLinear, self).teardown()
