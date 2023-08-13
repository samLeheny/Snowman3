import logging
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
from Snowman3.rigger.rig_factory.utilities.decorators import flatten_args
from Snowman3.rigger.rig_math.matrix import Matrix


class BaseDeformerPartGuide(PartGuide):

    default_settings = dict( root_name='Bend' )
    deformer_matrix = DataProperty( name='deformer_matrix', default_value=list(Matrix()) )
    split_deformers = DataProperty( name='split_deformers', default_value=True )

    def __init__(self, **kwargs):
        super(BaseDeformerPartGuide, self).__init__(**kwargs)
        self.toggle_class = BaseDeformerPart.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(BaseDeformerPartGuide, cls).create(**kwargs)
        handle = this.create_handle()
        handle.set_matrix(Matrix(this.deformer_matrix))
        handle.mesh.assign_shading_group(this.get_root().shaders[this.side].shading_group)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BaseDeformerPartGuide, self).get_toggle_blueprint()
        blueprint['deformer_matrix'] = list(self.handles[0].get_matrix())
        blueprint['split_deformers'] = self.split_deformers
        return blueprint

    def get_blueprint(self):
        blueprint = super(BaseDeformerPartGuide, self).get_blueprint()
        blueprint['deformer_matrix'] = list(self.handles[0].get_matrix())
        blueprint['split_deformers'] = self.split_deformers
        return blueprint


class BaseDeformerPart(Part):

    deformer = ObjectProperty(  # This is actually the transform above a deformer handle
        name='deformer'
    )
    deformer_utility_nodes = ObjectListProperty(
        name='deformer_utility_nodes'
    )
    deformer_matrix = DataProperty(
        name='deformer_matrix'
    )
    split_deformers = DataProperty(
        name='split_deformers',
        default_value=True
    )

    def __init__(self, **kwargs):
        super(BaseDeformerPart, self).__init__(**kwargs)
        self.data_getters['members'] = self.get_members
        self.data_getters['weights'] = self.get_weights
        self.data_setters['members'] = self.add_geometry
        self.data_setters['weights'] = self.set_weights
    #
    # def create_deformation_rig(self, **kwargs):
    #     super(BaseDeformerPart, self).create_deformation_rig(**kwargs)
    #     self.add_geometry(kwargs['rig_data']['members'])
    #     self.set_weights(kwargs['rig_data']['weights'])

    def add_geometry(self, geometry):
        logger = logging.getLogger('rig_build')
        if not geometry:
            logger.info('WARNING: %s had "None" added as geometry' % self)
        else:
            if not isinstance(geometry, dict):
                members = dict((x, None) for x in geometry)
            else:
                members = geometry
            if self.controller.namespace:
                namespaced_members = dict()
                for key in members:
                    namespaced_members['%s:%s' % (self.controller.namespace, key)] = members[key]
                members = namespaced_members
            missing_geometry = []
            existing_members = dict()
            already_added_geometry = []

            current_members = self.get_members()
            if not current_members:
                current_members = dict()

            current_geometry_names = [str(x) for x in current_members.keys()]

            for key in members:
                if key not in self.controller.named_objects:
                    missing_geometry.append(key)
                elif key in current_geometry_names:
                    already_added_geometry.append(key)
                else:
                    existing_members[key] = members[key]
            if missing_geometry:
                self.controller.raise_warning(
                    '<%s name=%s> is unable to find the following geometry.\n\n%s' % (
                        self.__class__.__name__,
                        self.name,
                        '\n'.join(missing_geometry)
                    )
                )
            if self.deformer:
                self.deformer.add_members(existing_members)
            else:
                raise Exception('%s Geometry was added before deformer creation.' % self)

    def add_members(self, members):
        missing_members = []
        existing_members = dict()
        for geometry_name in members:
            if geometry_name not in self.controller.named_objects:
                missing_members.append(geometry_name)
            else:
                existing_members[geometry_name] = members[geometry_name]
        if missing_members:
            self.controller.raise_warning(
                '%s Was unable to find the following members. (They will be skipped)\n\n%s' % (
                    self,
                    '\n'.join(missing_members)
                )
            )
        self.deformer.add_members(existing_members)

    def get_weights(self, precision=4):  # Called by data getter for blueprint
        if self.deformer:
            return self.deformer.get_weights(precision=precision)

    def get_members(self):
        if self.deformer:
            return self.deformer.get_members()

    def get_geometry_names(self):
        members = self.get_members()
        if members:
            return members.keys()

    def set_weights(self, weights):
        if weights is None:
            self.controller.raise_warning(
                'WARNING: %s was set to a weights value of "None". (Aborting set_weights function)' % self
            )
            return
        elif not isinstance(weights, dict):
            raise Exception('Weights type not supported')

        if self.controller.namespace:
            namespaced_weights = dict()
            for key in weights:
                namespaced_weights['%s:%s' % (self.controller.namespace, key)] = weights[key]
            weights = namespaced_weights

        members = self.get_members()
        missing_members = []
        for x in weights:
            if x not in members:
                missing_members.append(x)
        if missing_members:
            self.controller.raise_warning(
                '%s did not have the following members. Unable to set weights.\n\n%s' % (
                    self.deformer,
                    '\n'.join(missing_members)
                )
            )
            for x in missing_members:
                weights.pop(x)
        self.deformer.set_weights(weights)

    @flatten_args
    def remove_geometry(self, *geometry):
        if not geometry:
            raise Exception('You must provide some geometry to remove')
        geometry = map(str, geometry)
        geometry = list(geometry)
        current_members = self.get_members()

        remove_geometry_list = [str(x) for x in geometry if x in current_members.keys()]
        self.deformer.remove_geometry(*remove_geometry_list)

        return remove_geometry_list

    def get_blueprint(self):
        blueprint = super(BaseDeformerPart, self).get_blueprint()
        blueprint['split_deformers'] = self.split_deformers
        return blueprint
