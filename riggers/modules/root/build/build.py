import importlib
import pymel.core as pm

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.riggers.modules.root.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)





def build(rig_module, rig_parent=None):


    ctrls = {}


    # ...Create controls -----------------------------------------------------------------------------------------------
    ctrl_data = animCtrls.create_anim_ctrls()

    for key in ctrl_data:
        ctrls[key] = ctrl_data[key].initialize_anim_ctrl()
        ctrl_data[key].finalize_anim_ctrl()

    ctrls["root"].setParent(rig_parent) if rig_parent else None
    ctrls["subRoot"].setParent(ctrls["root"])
    ctrls["cog"].setParent(ctrls["subRoot"])



    # ...Groups --------------------------------------------------------------------------------------------------------
    # ...Settings controls group
    settings_ctrls_grp = pm.group(name="settings_{}".format(nom.group), p=ctrls["subRoot"], em=1)
    # ...Root spaces group
    root_spaces_grp = pm.group(name="globalSpaces_{}".format(nom.group), p=ctrls["subRoot"], em=1)
    # ...Rig modules group
    rig_modules_grp = pm.group(name="rigModules_{}".format(nom.group), p=ctrls["subRoot"], em=1)


    # ...Rig Scale attribute (So root control can only be scaled evenly in all three axes)
    pm.addAttr(ctrls["root"], longName="RigScale", minValue=0.001, defaultValue=1, keyable=1)
    [pm.connectAttr(ctrls["root"] + "." + "RigScale", ctrls["root"] + "." + a) for a in ("sx", "sy", "sz")]

    for key in ("root", "subRoot"):
        [pm.setAttr(ctrls[key] + "." + a, lock=1, keyable=0) for a in ("sx", "sy", "sz")]




    


    return {"controls": ctrls,
            "settings_ctrls_grp": settings_ctrls_grp,
            "root_spaces_grp": root_spaces_grp,
            "rig_modules_grp": rig_modules_grp}