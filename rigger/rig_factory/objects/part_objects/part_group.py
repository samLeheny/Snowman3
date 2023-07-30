import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty,\
    ObjectDictProperty


class PartGroupGuide(BaseContainer):

    rig_data = DataProperty( name='rig_data', )
    default_settings = dict( root_name='Group', side='center' )
    base_handles = ObjectListProperty( name='base_handles' )


    def __init__(self, **kwargs):
        super(PartGroupGuide, self).__init__(**kwargs)
        self.toggle_class = PartGroup.__name__


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        kwargs = super(PartGroupGuide, cls).pre_process_kwargs(**kwargs)
        for x in cls.default_settings:
            kwargs.setdefault(x, cls.default_settings[x])
        kwargs['segment_name'] = 'Container'
        return kwargs


    def create_handle(self, **kwargs):
        return self.controller.create_guide_handle(self, **kwargs)


    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            base_type=PartGroupGuide.__name__  # needed by blueprint view
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint


    def get_toggle_blueprint(self):
        blueprint = dict(
            klass=self.toggle_class,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size
        )
        blueprint['base_type'] = PartGroup.__name__
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        blueprint['guide_blueprint'] = self.get_blueprint()
        return blueprint


    def get_mirror_blueprint(self):
        """
        It would be great to just share this function with PartGuide somehow (they are identical)
        :return:
        """
        sides = dict(right='left', left='right')
        if self.side not in sides:
            raise Exception('Cannot mirror "%s" invalid side "%s"' % (self, self.side))
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=sides[self.side],
            size=self.size,
            segment_name=self.segment_name,
        )
        blueprint['disconnected_joints'] = self.disconnected_joints
        mirrored_handle_positions = dict()
        for handle in self.handles:
            search_prefix = rig_factory.settings_data['side_prefixes'][handle.side]
            replace_prefix = rig_factory.settings_data['side_prefixes'][sides[handle.side]]
            position = list(handle.get_translation())
            position[0] = position[0] * -1.0
            mirrored_handle_positions[handle.name.replace(search_prefix, replace_prefix)] = position
        blueprint['handle_positions'] = mirrored_handle_positions
        return blueprint


    def set_root_name(self, root_name):
        self.controller.named_objects.pop(self.name)
        self.root_name = root_name
        self.name = self.__class__.get_predicted_name(
            root_name=self.root_name,
            side=self.side
        )
        self.controller.named_objects[self.name] = self



class PartGroup(BaseContainer):

    guide_blueprint = DataProperty( name='guide_blueprint' )
    deform_joints = ObjectListProperty( name='deform_joints' )
    base_deform_joints = ObjectListProperty( name='base_deform_joints' )
    secondary_handles = ObjectListProperty( name='secondary_handles' )
    disconnected_joints = DataProperty( name='disconnected_joints', default_value=True )
    local_matrix_out_plugs = ObjectDictProperty( name='local_matrix_out_plugs' )
    local_matrix_in_plugs = ObjectDictProperty( name='local_matrix_in_plugs' )
    data_getters = dict()
    data_setters = dict()


    def __init__(self, **kwargs):
        super(PartGroup, self).__init__(**kwargs)
        self.toggle_class = PartGroupGuide.__name__


    def create_handle(self, **kwargs):
        return self.controller.create_standard_handle(self, **kwargs)


    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            guide_blueprint=self.guide_blueprint,
            base_type=PartGroup.__name__,  # needed by blueprint view
        )
        if not self.use_external_rig_data:
            blueprint['rig_data'] = self.get_rig_data()
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint


    def get_rig_data(self):
        return dict((x, self.data_getters[x]()) for x in self.data_getters)


    def get_toggle_blueprint(self):
        blueprint = self.guide_blueprint
        if not self.use_external_rig_data:
            blueprint['rig_data'] = self.get_rig_data()
        blueprint['base_type'] = PartGroup.__name__
        return blueprint


    def reset_handle_limits(self):
        for handle in self.get_handles():
            handle.reset_transform_limits()
