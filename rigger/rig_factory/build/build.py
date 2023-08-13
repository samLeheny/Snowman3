import Snowman3.rigger.rig_factory.build.utilities.mixins as mix

"""
This is the default build.py script copied to assets when none exists in user/build
"""


class AssetRigBuilder(mix.BuildMixin):

    def before_create_container(self):
        """
        This will happen at the very BEGINNING of the build
        """


class AssetGuideBuilder(mix.BuildMixin):

    def before_create_container(self):
        """
        This will happen at the very BEGINNING of the build
        """
