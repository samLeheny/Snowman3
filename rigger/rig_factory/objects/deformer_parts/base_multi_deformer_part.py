import logging
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part, PartGuide
from Snowman3.rigger.rig_factory.utilities.decorators import flatten_args
from Snowman3.rigger.rig_math.matrix import Matrix


class BaseMultiDeformerPartGuide(PartGuide):

    default_settings = dict(
        root_name='Bend'
    )

    deformer_matrix = DataProperty(
        name='deformer_matrix',
        default_value=list(Matrix())
    )

    def __init__(self, **kwargs):
        super(BaseMultiDeformerPartGuide, self).__init__(**kwargs)
        self.toggle_class = BaseMultiDeformerPart.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(BaseMultiDeformerPartGuide, cls).create(**kwargs)
        handle = this.create_handle()
        handle.set_matrix(Matrix(this.deformer_matrix))
        handle.mesh.assign_shading_group(this.get_root().shaders[this.side].shading_group)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BaseMultiDeformerPartGuide, self).get_toggle_blueprint()
        blueprint['deformer_matrix'] = list(self.handles[0].get_matrix())
        return blueprint

    def get_blueprint(self):
        blueprint = super(BaseMultiDeformerPartGuide, self).get_blueprint()
        blueprint['deformer_matrix'] = list(self.handles[0].get_matrix())
        return blueprint


class BaseMultiDeformerPart(Part):

    deformers = ObjectListProperty(
        name='deformers'
    )
    deformer_utility_nodes = ObjectListProperty(
        name='deformer_utility_nodes'
    )
    deformer_matrix = DataProperty(
        name='deformer_matrix'
    )

    def __init__(self, **kwargs):
        super(BaseMultiDeformerPart, self).__init__(**kwargs)
        self.data_getters['weights'] = self.get_weights
        self.data_getters['geometry_names'] = self.get_geometry_names
        self.data_setters['weights'] = self.set_weights
        self.data_setters['geometry_names'] = self.add_geometry

    def add_geometry(self, geometry):
        if geometry is None:
            raise Exception('WARNING: %s had "None" added as geometry' % self)
        else:
            if not isinstance(geometry, dict):
                members = dict((x, None) for x in geometry)
            else:
                members = geometry
            missing_geometry = []
            existing_members = dict()
            for key in members:
                if key not in self.controller.named_objects:
                    missing_geometry.append(key)
                else:
                    existing_members[key] = members[key]
            if missing_geometry:
                self.controller.raise_warning(
                    '%s is unable to find the following geometry.\n\n%s' % (
                        self.name,
                        '\n'.join(missing_geometry)
                    )
                )
            if self.deformers:
                for deformer in self.deformers:
                    deformer.add_members(existing_members)
            elif existing_members:
                self.create_deformers(existing_members)

    def create_deformers(self, geometry):
        raise Exception('Not implemented')

    @flatten_args
    def remove_geometry(self, *geometry):
        if not geometry:
            raise Exception('You must provide some geometry to remove')
        geometry = list(map(str, geometry))
        for deformer in self.deformers:
            member_meshs = deformer.get_members()
            for x in geometry:
                if x not in member_meshs:
                    raise Exception('%s does not exist in %s' % (x, self))
            deformer.remove_geometry(geometry)

    def set_members(self, members):
        missing_deformer_ids = []
        for deformer in self.deformers:
            if deformer.segment_name in members:
                deformer_members = members[deformer.segment_name]
                deformer.set_members(deformer_members)
            else:
                missing_deformer_ids.append(deformer.segment_name)
        if missing_deformer_ids:
            self.controller.raise_warning('WARNING: data is missing deformer ids: %s' % (missing_deformer_ids))

    def set_weights(self, weights):
        logger = logging.getLogger('rig_build')

        missing_members = []
        missing_deformer_ids = []
        if not isinstance(weights, dict):
            self.controller.raise_warning('WARNING: %s was provided legacy weights data. skipping' % self)
            return

        for deformer in self.deformers:
            logger.info('Attempting to set weights on %s' % deformer)
            if deformer.segment_name in weights:
                logger.info('Found weights key "%s"' % deformer.segment_name )

                deformer_weights = weights[deformer.segment_name]
                if not isinstance(deformer_weights, dict):
                    raise Exception('Weights type not supported')
                members = deformer.get_members()
                for x in deformer_weights:
                    if x not in members:
                        missing_members.append(x)
                deformer.set_weights(deformer_weights)
            else:
                missing_deformer_ids.append(deformer.segment_name)
        if missing_members:
            self.controller.raise_warning(
                'WARNING: %s did not have the following members. Unable to set weights.\n\n%s' % (
                    self,
                    '\n'.join(list(set(missing_members)))
                )
            )
        if missing_deformer_ids:
            self.controller.raise_warning(
                'WARNING: weights data did not have deformer ids matching: "%s" type(%s)\n cant set weights\n%s\n Ids provided: %s' % (
                    self,
                    type(self).__name__,
                    '\n'.join(list(set(missing_deformer_ids))),
                    weights.keys()
                )
            )

    def get_geometry_names(self):
        if self.deformers:
            geometry_names = []
            for deformer in self.deformers:
                members = deformer.get_members()
                if members:
                    geometry_names.extend(members.keys())
            return list(set(geometry_names))

    def get_members(self):
        if self.deformers:
            return dict((d.segment_name, d.get_members()) for d in self.deformers)

    def get_weights(self, precision=4):  # Called by data getter for blueprint
        if self.deformers:
            return dict((d.segment_name, d.get_weights(precision=precision)) for d in self.deformers)

    def get_blueprint(self):
        blueprint = super(BaseMultiDeformerPart, self).get_blueprint()
        if self.deformers:
            blueprint['members'] = self.get_members()
            blueprint['weights'] = self.get_weights()
            blueprint['geometry_names'] = self.get_geometry_names()
        return blueprint

    def finalize(self):
        super(BaseMultiDeformerPart, self).finalize()
        for deformer in self.deformers:
            deformer.plugs['v'].set_value(False)