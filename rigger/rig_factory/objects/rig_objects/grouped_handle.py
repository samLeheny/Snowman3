import logging

from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
#from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint

from Snowman3.rigger.rig_factory.objects.node_objects.curve_construct import CurveConstruct
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from Snowman3.rigger.rig_math.matrix import Matrix
#import rig_factory.environment as env



# ----------------------------------------------------------------------------------------------------------------------
class GroupedMixin(object):
    """
    Adds support for accessing groups above a control/transform by suffix name or top group,
    as well as supporting legacy group indices for backwards compatibility,
    (but any indices other than .groups[0] or .groups[-1] are not advised)
    """
    groups = ObjectListProperty( name='groups' )
    group_suffixes = DataProperty( name='group_suffixes', default_value=[] )


    def get_suffix_id(self, suffix):
        # Check that the given suffix exists, and return the respective group object if so
        camel_check = suffix.capitalize()  # Assumes group names are all eg. "Drv"
        for i, existSuf in enumerate(self.group_suffixes):
            if camel_check == existSuf:
                return i

        # If the suffix isn't found, return None if a supported suffix, or raise an error otherwise
        '''if camel_check not in env.supported_group_suffixes:
            raise NameError("The name {!r} doesn't match any standard group suffix!".format(suffix))'''
        return None


    def get_group_by_suffix(self, suffix):
        suffix_id = self.get_suffix_id(suffix)
        if suffix_id is None:
            # Suffix not found, but a valid name
            return None
        return self.groups[suffix_id]


    # Standard group suffixes (could use __getattr__ but listed for clarity)
    @property
    def tpx(self):
        return self.get_group_by_suffix('tpx')

    @property
    def tpp(self):
        return self.get_group_by_suffix('tpp')

    @property
    def top(self):
        return self.get_group_by_suffix('top')

    @property
    def zro(self):
        return self.get_group_by_suffix('zro')

    @property
    def ofs(self):
        return self.get_group_by_suffix('ofs')

    @property
    def drv(self):
        return self.get_group_by_suffix('drv')

    @property
    def cfx(self):
        return self.get_group_by_suffix('cfx')

    @property
    def cns(self):
        """ Always the group above the control, for animators only """
        return self.get_group_by_suffix('cns')

    @property
    def rzr(self):
        """ DoubleSurfaceSpline/Lip - roll axis zero group for when using offset roll pivot """
        return self.get_group_by_suffix('rzr')

    @property
    def rol(self):
        """ DoubleSurfaceSpline/Lip - roll group for when using offset roll pivot """
        return self.get_group_by_suffix('rol')

    @property
    def rpz(self):
        """ DoubleSurfaceSpline/Lip - 'roll post-zero' inverse offset group for when using offset roll pivot """
        return self.get_group_by_suffix('rpz')

    @property
    def zip(self):
        """ DoubleSurfaceSpline/Lip - group that is blended to center for lip zip """
        return self.get_group_by_suffix('zip')

    # Aliases
    @property
    def first_group(self):
        """ Top group in this hierarchy - Avoided using 'top_group' as it is used often by Parts including part.Part"""
        return self.groups[0]

    @property
    def constraint_group(self):
        """ Riggers use Ofs group for constraints. None if not found. """
        return self.ofs

    @property
    def shard_group(self):
        """ Shards also use Ofs group for constraints for now. None if not found. """
        return self.get_group_by_suffix(env.shard_group_id)

    @property
    def driven_group(self):
        """ Probably fine to use .drv but here for consistency. None if not found. """
        return self.get_group_by_suffix(env.driven_group_id)

    @property
    def anim_group(self):
        """ Animators use Cns group for constraints. None if not found. """
        return self.cns

    # Helper functions
    @classmethod
    def group_suffixes_for_count(cls, group_count, extraEndGroups=None):
        """ Return a tuple of the standard suffixes for the given number of groups

        Always Zro group as highest group, and Cns as lowest (top_group_suffix, bottom_group_suffix)

        extraEndGroups: if groups are to be added before animation Cns group but should be after existing groups eg. Drv
        (No need for extraTopGroups - just increase group_count)
        """
        mid_groups = list(env.standard_group_suffixes)
        if extraEndGroups:
            mid_groups.extend(extraEndGroups)

        suffixes = [env.top_group_suffix]  # Zro group always exists
        if group_count > 2:
            suffixes.extend(mid_groups[-group_count + 2:])
        if group_count > 1:
            suffixes.append(env.bottom_group_suffix)  # Anim Cns group always exists if 2+ controls
        return tuple(suffixes)



# ----------------------------------------------------------------------------------------------------------------------
class GroupedHandle(CurveConstruct, GroupedMixin):

    mirror_plugs = DataProperty( name='mirror_plugs', default_value=[] )
    space_switcher = ObjectProperty( name='space_switcher' )
    gimbal_handle = ObjectProperty( name='gimbal_handle' )
    gimbal_scale = DataProperty( name='gimbal_scale', default_value=0.9 )
    rotation_order = DataProperty( name='rotation_order', default_value='xyz' )


    @classmethod
    def create(cls, **kwargs):
        group_count = kwargs.setdefault( 'group_count', env.standard_group_count )
        parent = kwargs.pop( 'parent', None )
        handle_segment_name = kwargs.pop( 'segment_name', None )
        index = kwargs.pop( 'index', None )
        group_suffixes = kwargs.pop('group_suffixes', None)
        if group_suffixes:
            group_suffixes = group_suffixes[-group_count:]  # Keep the right-most group names if group_count is shorter
        else:
            # Use groups according to convention
            group_suffixes = GroupedMixin.group_suffixes_for_count(group_count)

        # Create groups above handle
        suffixes = []
        groups = []
        for i, suffix in enumerate(group_suffixes):
            group = parent.create_child(
                Transform,
                segment_name=handle_segment_name,
                suffix=suffix,
                **kwargs )
            parent = group
            suffixes.append(suffix)
            groups.append(group)

        # Create handle itself under groups
        this = super().create(
            parent=parent,
            segment_name=handle_segment_name,
            index=index,
            **kwargs
        )
        this.group_suffixes = suffixes
        this.groups = groups

        if kwargs.get('create_gimbal'):
            side = this.side

            this.gimbal_handle = this.create_child(
                CurveConstruct,
                shape=this.shape,
                axis=this.axis,
                segment_name=this.segment_name,
                functionality_name=this.functionality_name,
                subsidiary_name='Gimbal'
            )
            this.gimbal_handle.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )
            shape_matrix = Matrix()
            shape_matrix.set_scale([
                this.size * this.gimbal_scale,
                this.size * this.gimbal_scale,
                this.size * this.gimbal_scale,
            ])
            this.gimbal_handle.plugs['shapeMatrix'].set_value(shape_matrix)
            visibility_plug = this.create_plug(
                'gimbalVisibility',
                at='double',
                k=False,
                dv=0.0,
                min=0.0,
                max=1.0
            )
            visibility_plug.set_channel_box(True)
            for curve in this.gimbal_handle.curves:
                visibility_plug.connect_to(curve.plugs['visibility'])
            this.plugs['rotateOrder'].set_channel_box(True)
            this.plugs['rotateOrder'].connect_to(this.gimbal_handle.plugs['rotateOrder'])
        if 'rotation_order' in kwargs:
            rotation_order = kwargs.pop('rotation_order')
            this.set_rotation_order(rotation_order)

        return this

    def get_current_space_handle(self):
        if self.space_switcher:
            return self.space_switcher.targets[self.plugs['parentSpace'].get_value()]

    def add_standard_plugs(self):
        super().add_standard_plugs()
        if self.gimbal_handle:
            root = self.owner.get_root()
            if root:
                root.add_plugs(
                    self.plugs['gimbalVisibility'],
                    keyable=False
                )
        else:
            logging.getLogger('rig_build').warning(
                'Warning: Can\'t to find root for "%s". Unable to add standard plugs' % self
            )

    def stretch_shape(self, end_position):

        super().stretch_shape(
            end_position
        )
        if self.gimbal_handle:
            self.gimbal_handle.stretch_shape(
                end_position
            )

    def set_shape_matrix(self, matrix):
        super().set_shape_matrix(matrix)
        if self.gimbal_handle:
            gimbal_matrix = Matrix(matrix)
            gimbal_matrix.set_scale([x * self.gimbal_scale for x in matrix.get_scale()])
            self.gimbal_handle.plugs['shapeMatrix'].set_value(list(gimbal_matrix))

    def multiply_shape_matrix(self, matrix):
        super().multiply_shape_matrix(matrix)
        if self.gimbal_handle:
            gimbal_matrix = Matrix(matrix)
            gimbal_matrix.set_scale([x * self.gimbal_scale for x in matrix.get_scale()])
            self.gimbal_handle.multiply_shape_matrix(gimbal_matrix)

    def get_rotation_order(self):
        return env.rotation_orders[self.plugs['rotateOrder'].get_value()]

    def set_rotation_order(self, value):
        self.plugs['rotateOrder'].set_value(env.rotation_orders.index(value))

    def set_shape(self, new_shape, delete_current=True):
        curves = super().set_shape(
            new_shape,
            delete_current=delete_current
        )
        if hasattr(self, 'gimbal_handle'):
            self.normalize_gimbal_shape()
        return curves

    def normalize_gimbal_shape(self):
        if self.gimbal_handle:
            new_curves = self.gimbal_handle.set_shape(self.shape)
            if new_curves and self.plugs.exists('gimbalVisibility'):
                for new_curve in new_curves:
                    self.plugs['gimbalVisibility'].connect_to(new_curve.plugs['visibility'])

            # Grab shape matrix of main handle
            handle_shape_matrix_plug = self.plugs['shapeMatrix']
            handle_shape_matrix = Matrix(handle_shape_matrix_plug.get_value())

            # Multiply shape matrix by 0.9
            scale_matrix = Matrix(scale=[self.gimbal_scale, self.gimbal_scale, self.gimbal_scale])
            gimbal_shape_matrix = handle_shape_matrix.__mul__(scale_matrix)

            # Apply new gimbal shape matrix
            self.gimbal_handle.plugs['shapeMatrix'].set_value(list(gimbal_shape_matrix))

    def create_grouped_joint(self, parent):
        groups = []
        for i, control_group in enumerate(self.groups):
            group = control_group.create_child(
                Transform,
                functionality_name=control_group.suffix,
                parent=parent
            )
            parent = group
            groups.append(group)
        if not self.gimbal_handle:
            joint = self.create_child(
                Joint,
                functionality_name='Ctrl',
                parent=parent
            )
        else:
            control_group = self.create_child(
                Transform,
                functionality_name='Ctrl',
                parent=parent
            )
            joint = self.gimbal_handle.create_child(
                Transform,
                subsidiary_name='Gimbal',
                parent=control_group
            )
        return joint



# ----------------------------------------------------------------------------------------------------------------------
class StandardHandle(GroupedHandle):

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('create_gimbal', True)
        kwargs.setdefault('group_count', env.standard_group_count)
        this = super().create(**kwargs)
        return this



# ----------------------------------------------------------------------------------------------------------------------
class GimbalHandle(StandardHandle):

    @classmethod
    def create(cls, **kwargs):
        kwargs['create_gimbal'] = True
        this = super().create(**kwargs)
        return this



# ----------------------------------------------------------------------------------------------------------------------
class LocalHandle(GroupedHandle):

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('create_gimbal', True)
        this = super().create(**kwargs)
        if this.side in ['left', 'right']:
            this.mirror_plugs = ['translateX', 'translateY', 'translateZ']
        elif this.side == 'center':
            this.mirror_plugs = ['translateX', 'rotateZ', 'rotateY']
        return this



# ----------------------------------------------------------------------------------------------------------------------
class WorldHandle(GroupedHandle):

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('create_gimbal', True)
        this = super().create(**kwargs)
        if this.side in ['left', 'right']:
            this.mirror_plugs = ['translateX', 'rotateZ']
        elif this.side == 'center':
            this.mirror_plugs = ['translateX', 'rotateZ']
        return this



# ----------------------------------------------------------------------------------------------------------------------
class CogHandle(GroupedHandle):

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('create_gimbal', True)
        this = super().create(**kwargs)
        if this.side == 'center':
            this.mirror_plugs = ['rotateZ']
        return this
