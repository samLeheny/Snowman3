import importlib
import pymel.core as pm

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)





def execute(modules):



    '''
    # Create selection sets --------------------------------------------------------------------------------------------
    print("")
    print("Creating selection sets for...")

    print(" - bind joints")
    jntsSet = pm.sets(name=nom.set + '_jnts', empty=1)
    bodyJntsSet = pm.sets(name=nom.set + '_bodyJnts', empty=1)
    pm.sets(jntsSet, include=bodyJntsSet)
    bindJnts = pm.ls('bind_*', type='joint')
    for jnt in bindJnts:
        pm.sets(bodyJntsSet, include=jnt)

    print(" - animation controls")
    ctrlsSet = pm.sets(name=nom.set + '_ctrls', empty=1)
    bodyCtrlsSet = pm.sets(name=nom.set + '_bodyCtrls', empty=1)
    pm.sets(ctrlsSet, include=bodyCtrlsSet)
    animCtrls = pm.ls('anim_*', type='transform')
    for ctrl in animCtrls:
        pm.sets(bodyCtrlsSet, include=ctrl)







    # Redirect module Rig Scale attributes to root control -------------------------------------------------------------
    for module in modules.values():
        if "groups" in module:
            if "rig" in module["groups"]:

                rigGrp = module["groups"]["rig"]

                # Remove connection between module's Rig Scale attribute and its Scale attributes (it's inheriting
                # scale from the greater rig now)
                for attr in ["sx", "sy", "sz"]:
                    pm.setAttr(rigGrp+'.'+attr, lock=0)
                    attrUtils.breakConnections(rigGrp+'.'+attr)
                    pm.setAttr(rigGrp+'.'+attr, lock=1)

                pm.connectAttr(modules["root"]["controls"]["root"]+'.'+attrNom.rigScale, rigGrp+'.'+attrNom.rigScale)





    # Put extra nodes into place under root hierarchy ------------------------------------------------------------------
    def absorbIntoHierarchy (nodeType):
        for module in modules.values():
            if nodeType in module:
                for node in module[nodeType].values():
                    node.setParent(modules["root"]["groups"][nodeType])

    for nodeType in ["globalSpaces", "floatingIkHandles", "floatingIkCurves", "displayCurves", "ribbonPlanes"]:
        absorbIntoHierarchy(nodeType)





    # Setup node visibility --------------------------------------------------------------------------------------------
    print("")
    print("Setting up visibility driving for...")
    print(" - Bind joints")
    print(" - Non-bind joints")
    rigUtils.driveJointsVis()'''

    """print("")
    print("Hiding visibility for...")
    print(" - Locators")
    rigUtils.hideLocs()
    print(" - IK Handles")
    rigUtils.hideIkHandles()

    # Resize locators to conform to rig scale --------------------------------------------------------------------------
    print("")
    print("Conforming locators to rig scale")
    rigUtils.resizeLocators(rigScale)"""





    # Return to scene namespace ----------------------------------------------------------------------------------------
    pm.namespace(set=":")


    # Delete setup rig and the horse it road in on! --------------------------------------------------------------------
    pm.namespace(removeNamespace=nom.setupRigNamespace, deleteNamespaceContent=True)



    # Remove final rig namespace from all objects then delete namespace ------------------------------------------------
    pm.namespace(removeNamespace=":{}".format(nom.finalRigNamespace), mergeNamespaceWithRoot=True)


    #...Lock control transforms (this should be done in each rig module on creation, but in case any controls managed
    #...to slip through...) (Also lock vis attr) ----------------------------------------------------------------------
    for ctrl in pm.ls("*_{}".format(nom.animCtrl), type="transform"):
        rig_utils.apply_ctrl_locks(ctrl)
        ctrl.visibility.set(lock=1, keyable=0)




    '''
    # Lock down attributes on all DAG nodes except animation controls --------------------------------------------------
    # Get all DAG nodes in rig hierarchy, and all transform nodes in scene, then cross reference to get a list of all
    # transforms nodes in rig hierarchy
    allTransforms = pm.ls(type="transform")
    allRigNodes = pm.listRelatives(genUtils.getNode("rootCtrl"), allDescendents=1)

    allNonCtrlTransforms = []

    for obj in allTransforms:
        if obj in allRigNodes:
            if not pm.nodeType(obj) in ["joint", "ikHandle"]:
                if not stringUtils.getCleanName(obj).startswith(f'{nom.animCtrl}_'):
                    allNonCtrlTransforms.append(obj)


    # Remove all controls from list of rig hierarchy transform nodes
    allControls = pm.ls("::anim_*", type="transform")
    for obj in allControls:
        if obj in allNonCtrlTransforms:
            allNonCtrlTransforms.remove(obj)


    for obj in allNonCtrlTransforms:
        attrUtils.lockHideAttr(obj, translate=1, rotate=1, scale=1, shear=1, vis=1)



    # Hide all locators
    for loc in pm.ls(type="locator"):
        try:
            loc.visibility.set(lock=0)
            loc.visibility.set(0)
            loc.visibility.set(lock=1)
        except Exception:
            pass
    # Hide all non-floating IK handles
    for handle in pm.ls(type="ikHandle"):
        if not "floating" in str(handle.getParent()):
            try:
                handle.visibility.set(lock=0)
                handle.visibility.set(0)
                handle.visibility.set(lock=1)
            except Exception:
                pass'''