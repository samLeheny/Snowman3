# Title: attribute_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com



###########################
##### Import Commands #####
import importlib
import pymel.core as pm
###########################
###########################


# Global variables ########

###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
compose_attr_data_dictionary
get_attr_data
get_sub_attr_data
add_attr
add_string_attr
add_compound_attr
migrate_attr
migrate_connections
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################



########################################################################################################################
def compose_attr_data_dictionary(attr, node):
    attr_data = {
        'longName': pm.attributeQuery(attr, node=node, longName=1),
        'niceName': pm.attributeQuery(attr, node=node, niceName=1),
        'attributeType': pm.attributeQuery(attr, node=node, attributeType=1),
        'keyable': pm.attributeQuery(attr, node=node, keyable=1),
        'channelBox': pm.attributeQuery(attr, node=node, channelBox=1),
        'enumName': pm.attributeQuery(attr, node=node, listEnum=1),
        'hasMin': pm.attributeQuery(attr, node=node, minExists=1),
        'hasMax': pm.attributeQuery(attr, node=node, maxExists=1),
        'lock': pm.getAttr(node + "." + attr, lock=1),
        'currentValue': pm.getAttr(node + "." + attr),
        'parent': pm.attributeQuery(attr, node=node, listParent=1),
        'children': pm.attributeQuery(attr, node=node, listChildren=1),
        'numberOfChildren': pm.attributeQuery(attr, node=node, numberOfChildren=1),
        'readable': pm.attributeQuery(attr, node=node, readable=1),
        'writable': pm.attributeQuery(attr, node=node, writable=1),
        'shortName': pm.attributeQuery(attr, node=node, shortName=1),
        'child_attributes': None
    }

    # ...Add condition-dependant data
    if attr_data['attributeType'] == 'typed':
        attr_data['attributeType'] = 'string'

    attr_data['minValue'] = pm.attributeQuery(attr, node=node, minimum=1)[0] if attr_data['hasMin'] else None
    attr_data['maxValue'] = pm.attributeQuery(attr, node=node, maximum=1)[0] if attr_data['hasMax'] else None

    try:
        attr_data['defaultValue'] = pm.attributeQuery(attr, node=node, listDefault=1)[0]
    except Exception:
        attr_data['defaultValue'] = None

    return attr_data



########################################################################################################################
def get_attr_data(attr, node):
    """
    Given an attribute, and a node, will compose and return a dictionary of queried data from that attribute. This
        dictionary can be used to recreate the attribute one-to-one elsewhere.
    Args:
        attr (str): The name of the targeted attribute.
        node (mObj): The node the attribute is on.
    Returns:
        (dict): Queried attribute information.
    """

    #...Check attribute exists
    if not pm.attributeQuery(attr, node=node, exists=1):
        print(f"Attribute '{node}.{attr}' does not exist")
        return None

    #...Query attribute information and compose into a dictionary
    attr_data = compose_attr_data_dictionary(attr, node)
    if attr_data['attributeType'] == 'compound':
        if attr_data['numberOfChildren']:
            attr_data['numberOfChildren'] = attr_data['numberOfChildren'][0]
        attr_data = get_sub_attr_data(node, attr_data)


    return attr_data



########################################################################################################################
def get_sub_attr_data(node, attr_data):
    child_attrs = pm.attributeQuery(attr_data["longName"], node=node, listChildren=1)
    attr_data['child_attributes'] = []
    for child_attr in child_attrs:
        child_attr_data = compose_attr_data_dictionary(child_attr, node)
        attr_data['child_attributes'].append(child_attr_data)
    return attr_data




########################################################################################################################
def add_attr(obj, long_name, nice_name='', attribute_type=None, keyable=False, channel_box=False, enum_name=None,
             default_value=0, min_value=None, max_value=None, lock=False, parent='', number_of_children=0,
             child_attributes=None):

    # ...String type
    if attribute_type == 'string':
        add_string_attr(obj, long_name, nice_name=nice_name, keyable=keyable,
                        default_value=default_value, lock=lock, parent=parent)

    else:
        # ...Non-string type
        # ...Compound type
        if attribute_type == "compound":
            add_compound_attr(obj, long_name, nice_name=nice_name, keyable=keyable,
                              number_of_children=number_of_children, child_attributes=child_attributes)
        else:
            if parent:
                pm.addAttr(
                    obj,
                    longName=long_name,
                    niceName=nice_name,
                    attributeType=attribute_type,
                    keyable=keyable,
                    enumName=enum_name,
                    parent=parent
                )
            else:
                pm.addAttr(
                    obj,
                    longName=long_name,
                    niceName=nice_name,
                    attributeType=attribute_type,
                    keyable=keyable,
                    enumName=enum_name,
                )

        attr = f'{obj.nodeName()}.{long_name}'
        if default_value:
            pm.addAttr(attr, e=1, defaultValue=default_value)
            try:
                pm.setAttr(attr, default_value)
            except Exception:
                pass

        pm.addAttr(attr, e=1, minValue=min_value) if min_value else None
        pm.addAttr(attr, e=1, maxValue=max_value) if max_value else None

        pm.setAttr(f'{obj.nodeName()}.{long_name}', lock=True) if lock else None


    if channel_box and not keyable:
        pm.setAttr(f'{obj.nodeName()}.{long_name}', channelBox=True)


    return f'{obj.nodeName()}.{long_name}'



########################################################################################################################
def add_string_attr(obj, long_name, nice_name='', keyable=False, default_value=0, lock=False, parent=''):
    if parent:
        pm.addAttr(
            obj,
            longName=long_name,
            niceName=nice_name,
            dataType='string',
            keyable=keyable,
            parent=parent
        )
    else:
        pm.addAttr(
            obj,
            longName=long_name,
            niceName=nice_name,
            dataType='string',
            keyable=keyable
        )
    if default_value:
        pm.setAttr(f'{obj.nodeName()}.{long_name}', default_value, type='string', lock=lock)



########################################################################################################################
def add_compound_attr(obj, long_name, nice_name='', keyable=False, number_of_children=0, child_attributes=None):
    pm.addAttr(
        obj,
        longName=long_name,
        niceName=nice_name,
        attributeType='compound',
        keyable=keyable,
        numberOfChildren=number_of_children
    )
    if child_attributes:
        for data in child_attributes:
            add_attr(obj=obj, long_name=data['longName'], keyable=keyable, attribute_type=data['attributeType'],
                     parent=long_name, channel_box=data['channelBox'], enum_name=data['enumName'], lock=data['lock'],
                     nice_name=data['niceName'], default_value=data['defaultValue'], min_value=['minValue'],
                     max_value=['maxValue'])



########################################################################################################################
def migrate_attr(old_node, new_node, attr, include_connections=True, remove_original=True):

    #...Get channel box status of attribute, so it can be preserved in its new location
    channel_box_status = pm.getAttr(f'{old_node.nodeName()}.{attr}', channelBox=1)

    #...If attribute conflicts with an attribute already on new node, merge them
    if pm.attributeQuery(attr, node=new_node, exists=1):
        migrate_connections(f'{old_node.nodeName()}.{attr}', f'{new_node}.{attr}')
        return

    attr_data = get_attr_data(attr, old_node)

    recreated_attr = add_attr(
        new_node,
        long_name=attr_data["longName"],
        nice_name=attr_data["niceName"],
        attribute_type=attr_data["attributeType"],
        keyable=attr_data["keyable"],
        channel_box=attr_data["channelBox"],
        enum_name=attr_data["enumName"],
        default_value=attr_data["defaultValue"],
        min_value=attr_data["minValue"],
        max_value=attr_data["maxValue"],
        parent=attr_data["parent"],
        number_of_children=attr_data['numberOfChildren'],
        child_attributes=attr_data['child_attributes']
    )

    if attr_data['attributeType'] == 'compound':
        for child_attr in attr_data['child_attributes']:
            pm.setAttr(f'{new_node.nodeName()}.{child_attr["longName"]}', child_attr['currentValue'])
    else:
        pm.setAttr(f'{new_node.nodeName()}.{attr}', attr_data["currentValue"])

    if attr_data["lock"]:
        pm.setAttr(f'{new_node.nodeName()}.{attr}', lock=1)

    #...Migrate connections
    if include_connections:
        migrate_connections(f'{old_node}.{attr}', f'{new_node}.{attr}')

    #...Delete attribute in original location to complete apparent migration
    if remove_original:
        pm.deleteAttr(f'{old_node.nodeName()}.{attr}')

    if channel_box_status:
        pm.setAttr(f'{new_node}.{attr}', channelBox=1)



########################################################################################################################
def migrate_connections(old_attr, new_attr):

    plugs = pm.listConnections(old_attr, source=1, destination=0, plugs=1)
    for plug in plugs:
        pm.connectAttr(plug, new_attr, force=1)
        pm.disconnectAttr(plug, old_attr)

    plugs = pm.listConnections(old_attr, source=0, destination=1, plugs=1)
    for plug in plugs:
        pm.connectAttr(new_attr, plug, force=1)



########################################################################################################################
def add_attr_from_data(node, attr_data):
    add_attr(
        node,
        long_name=attr_data['longName'],
        nice_name=attr_data['niceName'],
        attribute_type=attr_data['attributeType'],
        keyable=attr_data['keyable'],
        channel_box=attr_data['channelBox'],
        enum_name=attr_data['enumName'],
        default_value=attr_data['defaultValue'],
        min_value=attr_data['minValue'],
        max_value=attr_data['maxValue'],
        parent=attr_data['parent'],
        number_of_children=attr_data['numberOfChildren'],
        child_attributes=attr_data['child_attributes']
    )
    return f'{node}.{attr_data["longName"]}'