from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty


class SpaceSwitcher(Transform):

    targets = ObjectListProperty( name='targets' )
    translate = DataProperty( name='translate', default_value=True )
    rotate = DataProperty( name='rotate', default_value=True )
    scale = DataProperty( name='scale', default_value=False )
    dv = DataProperty( name='dv', default_value=0 )

    suffix = 'Ssch'

    def teardown(self):
        return super(SpaceSwitcher, self).teardown()
