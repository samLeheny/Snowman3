import traceback
import logging


def process_legacy_lattice_guide_data(this, kwargs):
    """
    This function handles legacy data from the previous version of LatticePart
    This function should be removed once all blueprints have been re-saved with up to date source code.
    """

    if not this.rig_data:
        this.rig_data = dict()

    if 'rig_data' in kwargs and 'lattice_base_transform_matrix' in kwargs['rig_data']:
        kwargs['lattice_base_transform_matrix'] = kwargs['rig_data'].get('lattice_base_transform_matrix')

    if 'rig_data' in kwargs and 'lattice_transform_matrix' in kwargs['rig_data']:
        kwargs['lattice_transform_matrix'] = kwargs['rig_data'].get('lattice_transform_matrix')

    if '_lattice_matrix' in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "_lattice_matrix" found while building "%s". Attempting conversion.' % this
        )
        this.lattice.set_matrix(kwargs['_lattice_matrix'])
        this.lattice.lattice_transform.set_matrix(kwargs['_lattice_matrix'])
        # this.rig_data['lattice_transform_matrix'] = kwargs['_lattice_matrix']

    if '_base_lattice_matrix' in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "_base_lattice_matrix" found while building "%s". Skipping.' % this
        )
        # this.lattice.lattice_base_transform.set_matrix(kwargs['_base_lattice_matrix'])
        # this.rig_data['lattice_base_transform_matrix'] = kwargs['_base_lattice_matrix']

    if 'lattice_points' in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "lattice_points" found while building "%s". Attempting conversion.' % this
        )
        this.lattice.set_shape(kwargs['lattice_points'])
        this.rig_data['shape'] = kwargs['lattice_points']
        this.controller.build_warnings.append(
            'Legacy Data Detected. Copying "s_divisions", "t_divisions" and "u_divisions" into rig_data'
        )
        this.rig_data['s_divisions'] = kwargs['s_divisions']
        this.rig_data['t_divisions'] = kwargs['t_divisions']
        this.rig_data['u_divisions'] = kwargs['u_divisions']

    if 'geometry_names' in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "geometry_names" found while building "%s". Attempting conversion.' % this
        )
        this.rig_data['members'] = dict((x, None) for x in kwargs['geometry_names'])

    if 'lattice_data' in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "lattice_data" found while building "%s". Attempting conversion.' % this
        )
        this.rig_data['attribute_values'] = kwargs['lattice_data']


def process_legacy_lattice_rig_data(this, kwargs):
    """
    This function handles legacy data from the previous version of LatticePart
    This function should be removed once all blueprints have been re-saved with up to date source code.
    """

    if 'guide_blueprint' in kwargs and 'lattice_base_transform_matrix' in kwargs:
        kwargs['guide_blueprint']['lattice_base_transform_matrix'] = kwargs.get('lattice_base_transform_matrix')

    if 'guide_blueprint' in kwargs and 'lattice_transform_matrix' in kwargs:
        kwargs['guide_blueprint']['lattice_transform_matrix'] = kwargs.get('lattice_transform_matrix')

    if '_lattice_matrix' in kwargs and 'lattice_matrix' not in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "_lattice_matrix" found while building "%s". Attempting conversion.' % this
        )
        """
        This is actually a flawed approach in that the base ends up being moved rather than the main lattice..
        Still its the only solution i could find, and the resulting relitive deformation is the same.
        """
        this.deformer.set_matrix(kwargs['_lattice_matrix'])
        this.deformer.lattice_transform.set_matrix(kwargs['_lattice_matrix'])
        this.deformer.lattice_base_transform.set_matrix(kwargs['_lattice_matrix'])

    if '_base_lattice_matrix' in kwargs and 'lattice_matrix' not in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "_base_lattice_matrix" found while building "%s". Attempting conversion.' % this
        )
        this.deformer.lattice_base_transform.set_matrix(kwargs['_base_lattice_matrix'])

    if 'lattice_points' in kwargs and 'lattice_shape' not in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "lattice_points" found while building "%s". Attempting conversion.' % this
        )
        s_divisions, t_divisions, u_divisions = this.deformer.get_divisions()
        lattice_point_count = s_divisions * t_divisions * u_divisions
        if len(kwargs['lattice_points']) == lattice_point_count:
            this.deformer.set_shape(kwargs['lattice_points'])
        else:
            logging.getLogger('rig_build').warning('Legacy Lattice point data mismatch.')

    if 'lattice_data' in kwargs and 'attribute_values' not in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "lattice_data" found while building "%s". Attempting conversion.' % this
        )
        this.deformer.ffd.plugs.set_values(**kwargs['lattice_data'])


def process_legacy_feather_rig_data(this, kwargs):

    if 'weights' in kwargs :
        if isinstance(kwargs['weights'], dict):
            weights = dict((str(x), kwargs['weights'][x]) for x in kwargs['weights']) # get rid of unicode keys
            kwargs['weights'] = weights
            key_map = dict(  # At some point i was using metadat "bend_x" but realized we can just use segment name.
                bend_x='BendX', # Here I am  search/replacing the old metadata tag for the objects segment name
                bend_z='BendZ',
                twist='Twist'

            )
            for key in weights:
                if str(key) in key_map:
                    this.controller.build_warnings.append(
                        'Legacy data weights["%s"] found while building "%s". Attempting conversion.' % (key, this)
                    )
                    weights[key_map[str(key)]] = weights.pop(key)

        elif this.deformers and isinstance(kwargs['weights'], list):
            weights = kwargs.pop('weights')
            this.controller.build_warnings.append(
                'Legacy data "weights" found while building "%s". Attempting conversion.' % this
            )
            try:
                for i in range(len(this.deformers)):
                    this.deformers[i].set_weights(weights[i])
            except Exception as e:
                traceback.print_exc()
                this.controller.build_warnings.append(
                    '%s  Failed to set legacy weights. See script editor for details' % this
                )

        if '_geometry_names' in kwargs:  # Handle legacy geometry names
            this.controller.build_warnings.append(
                'Legacy data "_geometry_names" found while building "%s". Attempting conversion.' % this
            )
            this.add_geometry(kwargs['_geometry_names'])


def process_legacy_squish_rig_data(this, kwargs):
    if '_geometry_names' in kwargs:  # Handle legacy geometry names
        this.controller.build_warnings.append(
            'Legacy data "_geometry_names" found while building "%s". Attempting conversion.' % this
        )
        this.add_geometry(kwargs['_geometry_names'])
    elif 'geometry' in kwargs:  # Handle legacy geometry names
        this.controller.build_warnings.append(
            'Legacy data "geometry" found while building "%s". Attempting conversion.' % this
        )
        this.add_geometry(kwargs['geometry'])
    if 'weights' in kwargs:  # Handle legacy weights
        if isinstance(kwargs['weights'], dict):
            weights = dict((str(x), kwargs['weights'][x]) for x in kwargs['weights']) # get rid of unicode keys
            key_map = dict(  # At some point i was using metadat "bend_x" but realized we can just use segment name.
                bend_x='BendX',  # Here I am  search/replacing the old metadata tag for the objects segment name
                bend_z='BendZ',
                squash='SquashY'
            )
            for key in weights.keys():
                if key in key_map:
                    this.controller.build_warnings.append(
                        'Legacy data weights["%s"] found while building "%s". Attempting conversion.' % (key, this)
                    )
                    weights[key_map[key]] = weights.pop(key)
            kwargs['weights'] = weights
        elif this.deformers and isinstance(kwargs['weights'], list):
            weights = kwargs.pop('weights')
            this.controller.build_warnings.append(
                'Legacy data "weights" found while building "%s". Attempting conversion.' % this
            )
            try:
                for i in range(len(this.deformers)):
                    this.deformers[i].set_weights(weights[i])
            except Exception as e:
                traceback.print_exc()
                this.controller.build_warnings.append(
                    '%s  Failed to set legacy weights. See script editor for details' % this
                )


def process_legacy_lattice_squish_rig_data(this, kwargs):

    if '_geometry_names' in kwargs and 'geometry_names' not in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "_geometry_names" found while building "%s". Attempting conversion.' % this
        )
        kwargs['geometry_names'] = kwargs.pop('_geometry_names')

    if 'geometry' in kwargs and 'geometry_names' not in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "geometry" found while building "%s". Attempting conversion.' % this
        )
        kwargs['geometry_names'] = kwargs.pop('geometry')

    if '_lattice_weights' in kwargs:
        this.controller.build_warnings.append(
            'Legacy data "_lattice_weights" found while building "%s". Attempting conversion.' % this
        )
        kwargs['weights'] = kwargs.pop('_lattice_weights')
        kwargs['geometry_names'] = kwargs['weights'].keys()
        kwargs.pop('members', None)

    if this.deformer and 'weights' in kwargs and isinstance(kwargs['weights'], list):
        weights = kwargs.pop('weights')
        if len(weights) > 0:
            if isinstance(weights[0], dict):
                this.controller.build_warnings.append(
                    'Legacy data "weights" format:  list(dict()) found by "%s". Attempting conversion.' % this
                )
                kwargs['weights'] = weights[0]
                kwargs['geometry_names'] = weights[0].keys()


def process_legacy_piston_rig_data(this, kwargs):
    """
    This is to make piston part backward compatible. Delete this on March 31st 2021
    """
    # add an identity matrix for each added joint (the 3rd element)
    # the first 2 elements are body and wheel joints, so ignore them
    # [0, 0,    1, 2, add_an_identity_matrix, 4,    1, 2, add_an_identity_matrix, 4]
    count = kwargs['count']
    identity_matrix = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]
    if 2 + (3 * count) == len(this.matrices):
        for i in range(count):
            this.matrices.insert(i + 1 + (3 * (i + 1)), identity_matrix)
