from Snowman3.rigger.rig_factory.objects.part_objects.root import Root
from Snowman3.rigger.rig_factory.objects.part_objects.container import Container, ContainerGuide


class EnvironmentGuide(ContainerGuide):

    @classmethod
    def create(cls, **kwargs):
        kwargs['root_name'] = None
        return super(EnvironmentGuide, cls).create(**kwargs)

    def __init__(self, **kwargs):
        super(EnvironmentGuide, self).__init__(**kwargs)
        self.toggle_class = Environment.__name__


class Environment(Container):

    @classmethod
    def create(cls,  **kwargs):
        return super(Environment, cls).create(**kwargs)

    def __init__(self, **kwargs):
        super(Environment, self).__init__(**kwargs)

    def post_create(self, **kwargs):
        super(Environment, self).post_create(**kwargs)

        # Get Root part object
        root_part = self.find_first_part(Root)

        if root_part:
            for item in self.standin_group:
                # Parent Constraint on Standin Group within an Environment
                self.controller.scene.parentConstraint(
                    root_part.cog_joint,
                    item,
                    mo=True
                )
                # Scale Constraint on Standin Group within an Environment
                self.controller.scene.scaleConstraint(
                    root_part.cog_joint,
                    item,
                    mo=True
                )

