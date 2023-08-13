from Snowman3.rigger.rig_factory.objects.creature_objects.base_wing import BaseWing, BaseWingGuide


class BirdWingGuide(BaseWingGuide):

    default_settings = {
        'root_name': 'Wing',
        'size': 1.0,
        'side': 'left',
        'primary_digit_count': 8,
        'secondary_digit_count': 6,
        'tertiary_digit_count': 4,
        'use_bendy_arm': False,
        'digit_class': 'FeatherSimplePartGuide',
        'ribbon_joint_count': 10
    }

    def __init__(self, **kwargs):
        super(BirdWingGuide, self).__init__(**kwargs)
        self.toggle_class = BirdWing.__name__

    def create_members(self):
        super(BirdWingGuide, self).create_members()


class BirdWing(BaseWing):
    def finish_create(self, **kwargs):
        super(BirdWing, self).finish_create()
