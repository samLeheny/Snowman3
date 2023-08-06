from collections import Sequence
from itertools import chain, count
from Snowman3.rigger.rig_factory.objects.deformer_objects.deformer import Deformer
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty


class Lattice(Transform):

    ffd = ObjectProperty( name='ffd' )
    lattice_transform = ObjectProperty( name='lattice' )
    lattice_shape = ObjectProperty( name='lattice_shape' )
    lattice_base_transform = ObjectProperty( name='base_lattice' )
    base_lattice_shape = ObjectProperty( name='base_lattice_shape' )

    suffix = 'Lat'


    @classmethod
    def create(cls, **kwargs):
        geometry = kwargs.pop('geometry', [])
        # hardcoded segment name is problematic when making two lattices with the same root_name.
        # We should fix this when it is possible
        legacy_segment_names = kwargs.pop('legacy_segment_names', True)  # get rid of this in v3.0.0

        s_divisions = kwargs.pop('s_divisions', 5)
        t_divisions = kwargs.pop('t_divisions', 5)
        u_divisions = kwargs.pop('u_divisions', 5)

        this = super(Lattice, cls).create(**kwargs)
        (
            m_ffd,
            m_lattice,
            m_base_lattice,
            m_lattice_shape,
            m_base_lattice_shape,
            m_object_set
        ) = this.controller.scene.create_lattice()
        this.ffd = this.create_child(
            Deformer,
            node_type='ffd',
            segment_name='Ffd' if legacy_segment_names else f'{this.segment_name}Ffd',
            m_object=m_ffd
        )

        # The deformation Set is not a framework object but needs to be renamed so it matches conventions.
        ffd_short_name = this.ffd.name.split(':')[-1]
        name_tokens = ffd_short_name.split('_')[0:-1]
        name_tokens.append('Set')
        this.controller.rename(
            this.controller.scene.get_selection_string(m_object_set),
            '_'.join(name_tokens)
        )

        this.lattice_transform = this.create_child(
            Transform,
            segment_name='Lattice' if legacy_segment_names else '%sLattice' % this.segment_name,
            m_object=m_lattice
        )
        this.lattice_shape = this.create_child(
            DagNode,
            node_type='lattice',
            segment_name='LatticeShape' if legacy_segment_names else '%sLatticeShape' % this.segment_name,
            parent=this.lattice_transform,
            m_object=m_lattice_shape
        )
        this.lattice_base_transform = base_lattice = this.create_child(
            Transform,
            segment_name='BaseLattice' if legacy_segment_names else '%sBaseLattice' % this.segment_name,
            m_object=m_base_lattice
        )
        this.base_lattice_shape = this.create_child(
            DagNode,
            node_type='baseLattice',
            segment_name='BaseLatticeShape' if legacy_segment_names else '%sBaseLatticeShape' % this.segment_name,
            parent=base_lattice,
            m_object=m_base_lattice_shape
        )
        this.ffd.plugs['outsideLattice'].set_value(1)
        this.lattice_shape.plugs['sDivisions'].set_value(s_divisions)
        this.lattice_shape.plugs['tDivisions'].set_value(t_divisions)
        this.lattice_shape.plugs['uDivisions'].set_value(u_divisions)
        if geometry:
            this.add_geometry(geometry)
        return this


    def get_divisions(self):
        return (
            self.lattice_shape.plugs['sDivisions'].get_value(4),
            self.lattice_shape.plugs['tDivisions'].get_value(4),
            self.lattice_shape.plugs['uDivisions'].get_value(4)
        )


    def get_point(self, s, t, u):
        return self.controller.scene.get_lattice_point(
            self.lattice_shape.m_object,
            s, t, u
        )


    def get_shape(self):
        s_divisions, t_divisions, u_divisions = self.get_divisions()
        u_data = []
        for u in range(u_divisions):
            t_data = []
            for t in range(t_divisions):
                s_data = []
                for s in range(s_divisions):
                    s_data.append(self.get_point(s, t, u,))
                t_data.append(s_data)
            u_data.append(t_data)
        return u_data


    def set_shape(self, points):
        s_divisions, t_divisions, u_divisions = self.get_divisions()
        if point_depth(points) == 1:
            self.controller.build_warnings.append(
                'Legacy Lattice point data detected. %s is Attempting a conversion.' % self
            )

        else:
            if point_depth(points) != 3:
                self.controller.build_warnings.append(
                    'Lattice point data was not 3 lists deep. Unable to set shape for %s' % self.lattice_shape
                )

                return
            if len(points) != u_divisions:
                self.controller.build_warnings.append(
                    'Lattice point data did not match uDivisions of %s.\nUnable to set shape.' % self.lattice_shape
                )
                return
            for t_data in points:
                if len(t_data) != t_divisions:
                    self.controller.build_warnings.append(
                        'Lattice point data did not match tDivisions of %s.\nUnable to set shape.' % self.lattice_shape
                    )
                    return
                for u_data in t_data:
                    if len(u_data) != s_divisions:
                        self.controller.build_warnings.append(
                            f'Lattice point data did not match sDivisions of {self.lattice_shape}.\n'
                            f'Unable to set shape.')
                        return
            points = flatten_points(points)
        lattice_point_count = s_divisions * t_divisions * u_divisions
        if len(points) != lattice_point_count:
            raise Exception('Invalid lattice point count for %s. %s data points and %s lattice points' % (
                self.lattice_shape,
                len(points),
                lattice_point_count
            ))
        self.controller.scene.setAttr(
            self.lattice_shape.name + '.pt[:]',
            *sum(points, list())
        )


    def reset_shape(self):
        self.controller.scene.reset_lattice(self.lattice_shape.m_object)
        self.controller.scene.select(self.lattice_shape.name)


    def get_weights(self, precision=None):
        return self.ffd.get_weights(precision=precision)


    def set_weights(self, weights):
        self.ffd.set_weights(weights)


    def get_mesh_weights(self, mesh):
        return self.ffd.get_mesh_weights(mesh)


    def set_mesh_weights(self, mesh, weights):
        self.ffd.set_mesh_weights(mesh, weights)


    def get_members(self):
        if self.ffd:
            return self.ffd.get_members()


    def set_members(self, members):
        if members:
            self.ffd.set_members(members)


    def add_members(self, members):
        if members:
            self.ffd.add_members(members)


    def add_geometry(self, *geometry):
        if geometry:
            self.ffd.add_geometry(*geometry)


    def remove_geometry(self, *geometry):
        self.ffd.remove_geometry(*geometry)


    def lattice_fit_to_geo(self):
        """
        Applies translation and scaling to lattice to fit the bounding box of the selected geometry
        """
        geometries = self.controller.scene.get_selected_mesh_names()
        if not geometries:
            raise Exception('No valid geometry selected')
        center_pivot = self.controller.scene.get_bounding_box_center(geometries)
        scale_values = self.controller.scene.get_bounding_box_scale(geometries)

        self.plugs['translate'].set_value(center_pivot)
        self.plugs['scale'].set_value(scale_values)


def flatten_points(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)) and len(arg) > 0 and isinstance(arg[0], (list, tuple, set)):
            nodes.extend(flatten_points(*arg))
        else:
            nodes.append(arg)
    return nodes


def point_depth(seq):
    seq = iter(seq)
    try:
        for level in count():
            seq = chain([next(seq)], seq)
            seq = chain.from_iterable(
                s for s in seq if isinstance(s, Sequence) and len(s) > 0 and isinstance(s[0], Sequence) )
    except StopIteration:
        return level