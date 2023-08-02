import logging

import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.common_modules as com
from Snowman3.rigger.rig_factory.objects.node_objects.plug import Plug
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject
from Snowman3.rigger.rig_factory.objects.sdk_objects.sdk_keyframe import SDKKeyFrame
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty


class KeyframeGroup(BaseObject):

    sdk_group = ObjectProperty( name='sdk_group' )
    keyframes = ObjectListProperty( name='keyframes' )
    in_value = DataProperty( name='in_value' )
    in_tangent_type = DataProperty( name='in_tangent_type' )
    out_tangent_type = DataProperty( name='out_tangent_type' )
    index = DataProperty( name='index' )
    suffix = 'Kfgp'


    def __init__(self, **kwargs):
        super(KeyframeGroup, self).__init__(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        controller = com.controller_utils.get_controller()
        controller.scene.autoKeyframe(state=False)
        sdk_group = kwargs.get('sdk_group', None)
        in_value = kwargs.get('in_value', None)
        isolate = kwargs.get('isolate', True)
        keyframe_data = kwargs.get('keyframe_data', None)
        kwargs.setdefault('root_name', sdk_group.root_name)
        if not isinstance(in_value, float):
            raise Exception(
                'You must provide an "in_value" keyword argument of type "float" to create a %s. Not type: %s' % (
                    KeyframeGroup,
                    type(in_value)
                )
            )
        if in_value in [x.in_value for x in sdk_group.keyframe_groups]:
            raise Exception(
                'A keyframe group with the in_value "%s" already exists' % in_value
            )
        index = sdk_group.get_next_avaliable_index()
        kwargs['index'] = index
        kwargs['differentiation_name'] = rig_factory.index_dictionary[index].upper()

        # controller.start_sdk_ownership_signal.emit(None, sdk_group)
        this = super(KeyframeGroup, cls).create(**kwargs)
        this.sdk_group = sdk_group
        sdk_group.keyframe_groups.append(this)
        # controller.end_sdk_ownership_signal.emit(this, sdk_group)
        if keyframe_data is not None:
            this.update_from_data(keyframe_data)
        else:
            if isolate:
                this.sdk_group.isolate()
            this.update()
            # this.sdk_group.driver_plug.set_value(this.in_value)  # << ---- ??
        if this.out_tangent_type:
            this.set_keyframe_out_tangents(this.out_tangent_type)
        if this.in_tangent_type:
            this.set_keyframe_in_tangents(this.in_tangent_type)
        return this


    def update_from_data(self, keyframe_data):
        """
        Creates keys based on the provided data
        """
        sdk_group = self.sdk_group
        all_plugs = [x[0] for x in keyframe_data]
        if len(all_plugs) != len(list(set(all_plugs))):
            raise Exception('Duplicate plugs found: %s' % all_plugs)
        for plug, value in keyframe_data:
            plug = find_plug_object(self.controller, plug)
            if not plug:
                logging.getLogger('rig_build').warning('Plug not found: %s')
            animation_curve = self.sdk_group.get_animation_curve(plug)
            if self.in_value != 0.0 and 0.0 not in animation_curve.keyframes:
                """
                When a Non-zero key is being set,
                and a key with a 0.0 driven value does not exist on the curve,
                create a key with the driven value of 0.0 to hold the default pose
                """
                zero_group = dict((x.in_value, x) for x in self.sdk_group.keyframe_groups).get(0.0, None)
                if zero_group:
                    zero_keyframe = zero_group.create_child(
                        SDKKeyFrame,
                        index=zero_group.index,
                        animation_curve=animation_curve,
                        in_value=0.0,
                        out_value=0.0,
                        parent=animation_curve
                    )
                    zero_group.keyframes.append(zero_keyframe)

            new_keyframe = sdk_group.create_child(
                SDKKeyFrame,
                index=self.index,
                animation_curve=animation_curve,
                in_value=self.in_value,
                out_value=value,
                parent=animation_curve
            )

            self.keyframes.append(new_keyframe)


    def update(self):
        """
        Creates keyframes based on the driven plugs current positions
        Also adds keyframes to adjacent keyframe groups as needed
        """
        sdk_group = self.sdk_group
        for driven_plug in sdk_group.sdk_network.driven_plugs:
            animation_curve = sdk_group.animation_curves.get(driven_plug.name, None)
            default_value = round(driven_plug.default_value, 5)
            current_value = round(driven_plug.get_value(), 5) - default_value
            if not animation_curve and abs(round(current_value, 5)) == 0.0:
                """
                If NO animation curve yet,
                and current value is zero (relative to default),
                and default value is zero,
                Nothing has changed, no need to do set key on this plug
                ***NOTE*** 
                    We could potentially clear out redundant neighbor keys here
                """
                continue

            previous_key_group, next_key_group = self.get_adjacent()

            non_zero_neighbors = False

            if animation_curve:
                if previous_key_group and previous_key_group.in_value in animation_curve.keyframes:
                    if animation_curve.keyframes[previous_key_group.in_value].out_value != 0.0:
                        non_zero_neighbors = True
                if next_key_group and next_key_group.in_value in animation_curve.keyframes:
                    if animation_curve.keyframes[next_key_group.in_value].out_value != 0.0:
                        non_zero_neighbors = True

            current_keyframe = None
            if animation_curve and self.in_value in animation_curve.keyframes:
                """
                If Keyframe already exists,
                Re-Key It! (at the driven plugs current value!)
                This is to update existing keyframes
                """
                current_keyframe = animation_curve.keyframes[self.in_value]
                self.controller.change_keyframe(
                    current_keyframe,
                    out_value=current_value
                )
            if not current_keyframe and abs(round(current_value, 11)) != 0.0:
                """
                If no keyframe has been created yet,
                and current driven plug value is not zero,
                Key It!
                Any time a driven value is not 0.0 (default value) it MUST be keyed
                """
                animation_curve = self.sdk_group.get_animation_curve(driven_plug)
                current_keyframe = sdk_group.create_child(
                    SDKKeyFrame,
                    index=self.index,
                    animation_curve=animation_curve,
                    in_value=self.in_value,
                    out_value=current_value,
                    parent=animation_curve
                )
                self.keyframes.append(current_keyframe)

            if not current_keyframe and non_zero_neighbors:
                """
                If no keyframe has been created yet,
                and there are neighbouring keys with non-zero values,
                Key It!
                In other words:
                if neighbouring keys are all 10.0 for example and this key is 0.0 (default) even though it is default 
                it still needs to be keyed because it is different from its neighbours
                """
                animation_curve = self.sdk_group.get_animation_curve(driven_plug)
                current_keyframe = sdk_group.create_child(
                    SDKKeyFrame,
                    index=self.index,
                    animation_curve=animation_curve,
                    in_value=self.in_value,
                    out_value=0.0,
                    parent=animation_curve
                )
                self.keyframes.append(current_keyframe)
            all_curve_in_values = animation_curve.keyframes.keys()
            if next_key_group and next_key_group.in_value not in all_curve_in_values:
                """
                If the neighbouring (NEXT) KeyframeGroup driver value is not represented in the animation curve,
                Key It! (with the DRIVER value of the KeyframeGroup and DRIVEN value of 0.0)
                """
                next_keyframe = next_key_group.create_child(
                    SDKKeyFrame,
                    index=next_key_group.index,
                    animation_curve=animation_curve,
                    in_value=next_key_group.in_value,
                    out_value=0.0,  # this needs to be zero because any default value is added after the anim curve
                    parent=animation_curve
                )
                next_key_group.keyframes.append(next_keyframe)

            if previous_key_group and previous_key_group.in_value not in all_curve_in_values:
                """
                If the neighbouring (PREVIOUS) KeyframeGroup driver value is not represented in the animation curve,
                Key It! (with the DRIVER value of the KeyframeGroup and DRIVEN value of 0.0)
                """
                previous_keyframe = previous_key_group.create_child(
                    SDKKeyFrame,
                    index=previous_key_group.index,
                    animation_curve=animation_curve,
                    in_value=previous_key_group.in_value,
                    out_value=0.0,  # this needs to be zero because any default value is added after the anim curve
                    parent=animation_curve
                )
                previous_key_group.keyframes.append(previous_keyframe)
            driven_plug.get_value()  # Clean The Graph


    def get_adjacent(self):
        """
        Gets previous and next keyframe groups
        """
        sorted_key_groups = sorted(
            self.sdk_group.keyframe_groups,
            key=lambda x: x.in_value
        )
        key_index = sorted_key_groups.index(self)
        previous_key_group = sorted_key_groups[key_index - 1] if key_index > 0 else None
        next_key_group = sorted_key_groups[key_index + 1] if key_index < len(sorted_key_groups) - 1 else None
        return previous_key_group, next_key_group


    def prepare_to_be_deleted(self):
        """
        if self.in_value == 0.0(default) we must update adjecent keys before deleting
        We must add a key to prevent previous key from changing
        """
        for driven_plug in self.sdk_group.sdk_network.driven_plugs:
            animation_curve = self.sdk_group.animation_curves.get(driven_plug.name, None)
            if animation_curve:
                previous_key_group, next_key_group = self.get_adjacent()
                if next_key_group and previous_key_group:
                    next_key = animation_curve.keyframes.get(next_key_group.in_value, None)
                    previous_key = animation_curve.keyframes.get(previous_key_group.in_value, None)
                    if previous_key and not next_key and round(previous_key.out_value, 11) != 0.0:
                        next_key = next_key_group.create_child(
                            SDKKeyFrame,
                            index=next_key_group.index,
                            animation_curve=animation_curve,
                            in_value=next_key_group.in_value,
                            out_value=0.0,
                            parent=animation_curve
                        )
                        next_key_group.keyframes.append(next_key)
                    if next_key and not previous_key and round(next_key.out_value, 11) != 0.0:
                        previous_key = previous_key_group.create_child(
                            SDKKeyFrame,
                            index=previous_key_group.index,
                            animation_curve=animation_curve,
                            in_value=previous_key_group.in_value,
                            out_value=0.0,
                            parent=animation_curve
                        )
                        previous_key_group.keyframes.append(previous_key)
                driven_plug.get_value()  # Clean The Graph


    def set_keyframe_in_tangents(self, tangent_type):
        self.in_tangent_type = tangent_type
        self.controller.change_keyframe(
            self,
            in_tangent=tangent_type
        )


    def set_keyframe_out_tangents(self, tangent_type):
        self.out_tangent_type = tangent_type
        self.controller.change_keyframe(
            self,
            out_tangent=tangent_type
        )


    def set_keyframe_tangents(self, tangent_type):

        self.in_tangent_type = tangent_type
        self.out_tangent_type = tangent_type

        self.controller.change_keyframe(
            self,
            in_tangent=tangent_type,
            out_tangent=tangent_type
        )


    def teardown(self):
        self.prepare_to_be_deleted()
        self.controller.start_sdk_disown_signal.emit(self, self.sdk_group)
        curve_names = [key.animation_curve.name for key in self.keyframes]
        self.controller.schedule_objects_for_deletion(self.keyframes)
        if curve_names and self.keyframes:
            self.controller.scene.select(cl=True)
            self.controller.scene.selectKey(*curve_names, cl=True)
            self.controller.scene.selectKey(
                curve_names,
                float=(self.in_value,),
                keyframe=True
            )

            self.controller.scene.cutKey(
                animation='keys',
                clear=True,
            )
        self.keyframes = []
        sdk_group = self.sdk_group
        self.sdk_group.keyframe_groups.remove(self)
        self.sdk_group = None
        super(KeyframeGroup, self).teardown()
        self.controller.end_sdk_disown_signal.emit(self, sdk_group)


def find_plug_object(controller, plug):
    if isinstance(plug, Plug):
        return plug
    elif isinstance(plug, str):
        node_name, attribute_name = plug.split('.')
        if node_name in controller.named_objects:
            node = controller.named_objects[node_name]
            if node.plugs.exists(attribute_name):
                return node.plugs[attribute_name]

