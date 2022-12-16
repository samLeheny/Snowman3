import pymel.core as pm

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)

# Constants
nom = nameConventions.create_dict()





########################################################################################################################
#############-------------------------------    TABLE OF CONTENTS    ------------------------------------###############
########################################################################################################################
'''
rootCtrl
subRootCtrl
headJnt
headCtrl
transformGrp
noTransformGrp
noTransformGrp_hide
noTransformGrp_show
geoGrp
headGeoGrp
modelGeoGrp
headMesh
spacesGrp
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################





# ----------------------------------------------------------------------------------------------------------------------
def findNodeInChildren(possible_name_tags=None, parent=None, node_prefix=None):

    target_node = None

    possible_nodes = None
    try:
        possible_nodes = parent.getChildren()
    except:
        pass

    if not possible_nodes:
        return(None)


    # Only include nodes under parent
    new_possible_nodes = []
    for obj in possible_nodes:

        for nameTag in possible_name_tags:

            nameString = stringUtils.composeName(name=nameTag, node=node_prefix, config="node_name_num_side")

            if nameString in stringUtils.getCleanName(str(obj)):
                new_possible_nodes.append(obj)

    possible_nodes = new_possible_nodes


    if len(possible_nodes) > 0:

        if len(possible_nodes) == 1:

            target_node = possible_nodes[0]


    # Investigate the various returned nodes in more detail to determine which one to return
    for node in possible_nodes:
        pass

    return (target_node)





# ----------------------------------------------------------------------------------------------------------------------
def root_ctrl():

    root_ctrl = None

    possible_name_tags = ["root", "global"]

    for name_tag in possible_name_tags:

        root_ctrl_string = "{0}_{1}".format(name_tag, nom.animCtrl)
        possible_root_ctrls = pm.ls('::' + root_ctrl_string, type="transform")

        if len(possible_root_ctrls) > 0:

            if len(possible_root_ctrls) == 1:

                root_ctrl = possible_root_ctrls[0]
                break


    return root_ctrl




"""
# ----------------------------------------------------------------------------------------------------------------------
def root_offset_ctrl(debug=None):

    offsetCtrl = None

    possible_name_tags = [
        "subRoot",
        "globalOffset",
    ]

    offsetCtrl = findNodeInChildren(possible_name_tags=possible_name_tags, parent=rootCtrl(), node_prefix=nom.animCtrl)

    return(offsetCtrl)





# ----------------------------------------------------------------------------------------------------------------------
def head_jnt(debug=None):

    headJnt = None

    possible_name_tags = [
        'head',
    ]

    for jntType in [nom.bindJnt, nom.nonBindJnt]:

        for nameTag in possible_name_tags:

            headJntString = stringUtils.composeName(name=nameTag, node=jntType, config='node_name_num_side')
            possibleHeadJnts = pm.ls(headJntString)

            if len(possibleHeadJnts) > 0:

                if len(possibleHeadJnts) == 1:

                    headJnt = possibleHeadJnts[0]
                    return(headJnt)

                else:

                    # Investigate the various returned nodes in more detail to determine which one to return
                    for node in possibleHeadJnts:
                        pass

    return (headJnt)





# ----------------------------------------------------------------------------------------------------------------------
def head_ctrl(debug=None):

    headCtrl = None

    possible_name_tags = [
        'head',
    ]

    for nameTag in possible_name_tags:

        headCtrlString = stringUtils.composeName(name=nameTag, node=nom.animCtrl, config='node_name_num_side')
        possibleHeadCtrls = pm.ls(headCtrlString)

        if len(possibleHeadCtrls) > 0:

            if len(possibleHeadCtrls) == 1:

                headCtrl = possibleHeadCtrls[0]
                break

            else:

                # Investigate the various returned nodes in more detail to determine which one to return
                for node in possibleHeadCtrls:
                    pass


    return (headCtrl)





# ----------------------------------------------------------------------------------------------------------------------
def transform_grp(debug=None):

    transformGrp = None

    possible_name_tags = [
        "transform",
    ]


    transformGrp = findNodeInChildren(possible_name_tags=possible_name_tags, parent=subRootCtrl(), node_prefix=nom.group)

    return (transformGrp)





# ----------------------------------------------------------------------------------------------------------------------
def notransform_grp(debug=None):

    noTransformGrp = None

    possible_name_tags = [
        "noTransform",
    ]


    noTransformGrp = findNodeInChildren(possible_name_tags=possible_name_tags, parent=subRootCtrl(),
                                        node_prefix=nom.group)


    return (noTransformGrp)





# ----------------------------------------------------------------------------------------------------------------------
def notransform_grp_hide(debug=None):

    noTransformGrp_hide = None

    possible_name_tags = [
        "noTransform_hide",
        "noTransform_invisible",
        "noTransform_hidden",
    ]

    noTransformGrp_hide = findNodeInChildren(possible_name_tags=possible_name_tags, parent=noTransformGrp(),
                                        node_prefix=nom.group)

    return (noTransformGrp_hide)





# ----------------------------------------------------------------------------------------------------------------------
def notransform_grp_show(debug=None):

    noTransformGrp_show = None

    possible_name_tags = [
        "noTransform_show",
        "noTransform_visible",
    ]

    noTransformGrp_show = findNodeInChildren(possible_name_tags=possible_name_tags, parent=noTransformGrp(),
                                             node_prefix=nom.group)

    return (noTransformGrp_show)





# ----------------------------------------------------------------------------------------------------------------------
def geo_grp(debug=None):

    geoGrp = None

    possible_name_tags = [
        "geo",
        "geometry",
    ]

    geoGrp = findNodeInChildren(possible_name_tags=possible_name_tags, parent=noTransformGrp_show(), node_prefix=nom.group)


    return (geoGrp)





# ----------------------------------------------------------------------------------------------------------------------
def headGeoGrp(debug=None):

    headGrp = None

    possible_name_tags = [
        "head",
        "face",
        "headGeo",
        "faceGeo",
    ]

    headGrp = findNodeInChildren(possible_name_tags=possible_name_tags, parent=geoGrp(), node_prefix=nom.group)
    if not headGrp:
        headGrp = findNodeInChildren(possible_name_tags=possible_name_tags, parent=modelGeoGrp(), node_prefix=nom.group)


    return (headGrp)





# ----------------------------------------------------------------------------------------------------------------------
def modelGeoGrp(debug=None):

    modelGeoGrp = None

    possible_name_tags = [
        'grp_model',
    ]

    for nameTag in possible_name_tags:

        possibleModelGrps = pm.ls('::' + nameTag)

        if len(possibleModelGrps) > 0:

            if len(possibleModelGrps) == 1:

                modelGeoGrp = possibleModelGrps[0]
                break

            else:

                # Investigate the various returned nodes in more detail to determine which one to return
                for node in possibleModelGrps:
                    pass

    return (modelGeoGrp)
"""




# ----------------------------------------------------------------------------------------------------------------------
def setup_root_ctrl():

    setup_root_ctrl = None

    possible_name_tags = ['setup_root', 'setupRoot', 'setupGlobal', 'setup_global']

    for name_tag in possible_name_tags:

        setup_root_ctrl_string = "{0}_{1}".format(name_tag, nom.nonAnimCtrl)
        possible_setup_root_ctrls = pm.ls("::" + setup_root_ctrl_string, type="transform")

        if len(possible_setup_root_ctrls) > 0:

            if len(possible_setup_root_ctrls) == 1:

                setup_root_ctrl = possible_setup_root_ctrls[0]
                break


    return setup_root_ctrl




"""
# ----------------------------------------------------------------------------------------------------------------------
def mainHeadMesh(debug=None):

    headMesh = None

    possibleTags = ["head", "body", "face"]

    for tag in possibleTags:

        possibleHeadMesh = '::{}_{}'.format(nom.geo, tag)

        if pm.objExists(possibleHeadMesh) == True:

            headMesh = pm.ls(possibleHeadMesh)[0]
            break

    if headMesh:
        # Test that found head mesh is under geo group
        iter = 0
        limit = 100
        geoGroup = geoGrp()
        currentNode = headMesh
        isUnderGeoGrp = False

        while 0 < limit:
            testNode = currentNode.getParent()
            if testNode == geoGroup:
                isUnderGeoGrp = True
                break
            if stringUtils.getCleanName(str(testNode)) in [nom.group+"_model", nom.group+"_geo"]:
                isUnderGeoGrp = True
                break
            else:
                currentNode = testNode

        if isUnderGeoGrp in [False, 0]:
            headMesh = None


    return(headMesh)





# ----------------------------------------------------------------------------------------------------------------------
def spacesGrp(debug=None):

    spacesGrp = None

    possibleTags = ["globalSpaces", "spaces"]

    spacesGrp = findNodeInChildren(possible_name_tags=possibleTags, parent=transformGrp(), node_prefix=nom.group)

    return(spacesGrp)
"""