import pymel.core as pm
import maya.cmds as mc
import importlib
import Snowman3.riggers.utilities.classes.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig

mc.file(new=True, f=True)


limb_rig = LimbRig(limb_name = "testLeg",
                    side = "L",
                    prefab = "plantigrade",
                    segment_names = ["thigh", "calf", "ankle"])
                    
'''limb_rig = LimbRig(limb_name = "testLeg",
                    side = "L",
                    prefab = "plantigrade_doubleKnee",
                    segment_names = ["thigh", "knee", "calf", "ankle"])

limb_rig = LimbRig(limb_name = "testLeg",
                    side = "L",
                    prefab = "digitigrade",
                    segment_names = ["thigh", "calf", "tarsus", "ankle"])

limb_rig = LimbRig(limb_name = "testLeg",
                    side = "L",
                    prefab = "digitigrade_doubleKnees",
                    segment_names = ["thigh", "frontKnee", "calf", "backKnee", "tarsus", "ankle"])

limb_rig = LimbRig(limb_name = "testLeg",
                    side = "L",
                    prefab = "digitigrade_doubleFrontKnee",
                    segment_names = ["thigh", "frontKnee", "calf", "tarsus", "ankle"])'''