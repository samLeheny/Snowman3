import copy
import Snowman3.rigger.rig_factory.objects as obs


def flatten_blueprint(blueprint, include_self=True):
    """
    Flattens hierarchical blueprint data into a flat list
    """
    parts = blueprint.get('part_members', [])
    blueprint_list = []
    if include_self:
        blueprint_list.append(blueprint)
    for part_blueprint in parts:
        blueprint_list.extend(flatten_blueprint(part_blueprint))
    return blueprint_list


def kwarg_part_generator(owner, blueprints):
    """
    Generates (Part, kwargs) pairs from nested part blueprints
    """
    for kwargs in blueprints:
        predicted_name = obs.__dict__[kwargs['klass']].get_predicted_name(
            **kwargs
        )
        if predicted_name not in owner.get_root().deleted_parent_entity_part_names:
            sub_kwargs = kwargs.pop('part_members', [])
            kwargs = copy.deepcopy(kwargs)
            kwargs.pop('name', None)
            kwargs.pop('segment_name', None)
            kwargs.pop('segment_names', None)
            new_part = owner.create_part(
                kwargs['klass'],
                **kwargs
            )
            yield kwargs, new_part
            for x in kwarg_part_generator(new_part, sub_kwargs):
                yield x
