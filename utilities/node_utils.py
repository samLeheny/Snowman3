# Title: node_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: A collection of functions that allow the creation of specific nodes and the handling of their data all at
# once. Beats taking up several lines of code every time you bring a new node into a scene.


###########################
##### Import Commands #####
import pymel.core as pm
###########################
###########################



########################################################################################################################
#############-------------------------------    TABLE OF CONTENTS    ------------------------------------###############
########################################################################################################################
'''
floatMath
floatConstant
addDoubleLinear
multDoubleLinear
remapValue
reverse
curveInfo
pointOnCurveInfo
pointOnSurfaceInfo
multiplyDivide
plusMinusAverage
condition
fourByFourMatrix
multMatrix
clamp
blendMatrix
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################





########################################################################################################################
def floatMath(name=None, floatA=None, floatB=None, operation=0, outFloat=None):
    """
        Creates a floatMath utility node to specifications provided in arguments.
        Args:
            name (string): Node's name.
            floatA (numeric/ mObject attribute plug): 'floatA' attr input. Takes either a numeric value, or if arg is
                mPlug type, connects plug into 'floatA' attr.
            floatB (numeric/ mPlug): 'floatB' attr input. Takes either a numeric value, or if arg is
                mPlug type, connects plug into 'floatB' attr.
            operation (int (0 to 6)/ string): Setting for the 'operation' input value. Give either the index of the
                operation you want, or a corresponding string (see 'operation_strings' dictionary in function body)
            outFloat (mPlug): Attribute plug for node's output to pipe into.
        Returns:
            (utility node) The new floatMath node.
    """



    # Assemble a dictionary that converts accepted strings from the operation argument to numeric values that the
    # floatMath node's 'operation' attribute expects
    operation_strings = {
        "add": 0, "addition": 0, "sum": 0, "plus": 0,
        "subtract": 1, "subtraction": 1, "minus": 1,
        "multiply": 2, "mult": 2, "times": 2, "product": 2,
        "divide": 3, "division": 3, "divided by": 3, "div": 3,
        "min": 4, "minimum": 4,
        "max": 5, "maximum": 5,
        "power": 6, "exponent": 6, "exponentiation": 6, "exp": 6
    }


    # ...Create node
    if name:
        node = pm.shadingNode("floatMath", name=name, asUtility=1)
    else:
        node = pm.shadingNode("floatMath", asUtility=1)


    # ...Pass arguments to floatMath input attributes 'floatA' and 'floatB'. If the provided arguments are numeric
    # ...types, set the attributes to match them. If they are mObject attributes, connect them to the floatMath node's
    # ...input attributes.

    # ...floatA
    if floatA:

        if isinstance(floatA, (int, float)):
            node.floatA.set(floatA)
        else:
            pm.connectAttr(floatA, node.floatA)

    # ...floatB
    if floatB:

        if isinstance(floatB, (int, float)):
            node.floatB.set(floatB)
        else:
            pm.connectAttr(floatB, node.floatB)



    # ...Set floatMath node's operation attribute
    if isinstance(operation, int):
        pass
    elif isinstance(operation, str):
        if operation in operation_strings:
            operation = operation_strings[operation]

    node.operation.set(operation)



    # ....Connect node's outFloat attribute to its destination
    if outFloat:
        node.outFloat.connect(outFloat)



    return node





########################################################################################################################
def floatConstant(name=None, inFloat=None, outFloat=None):
    """
        Creates a floatConstant utility node to specifications provided in arguments.
        Args:
            name (string): Node's name.
            inFloat (numeric/ mObject attribute plug): 'inFloat' attr inFloat. Takes either a numeric value, or if arg
                is mPlug type, connects plug into 'inFloat' attr.
            outFloat (mPlug): Attribute plug for node's outFloat to pipe into.
        Returns:
            (utility node) The new floatConstant node.
    """


    # ...Create node
    if name:
        node = pm.shadingNode("floatConstant", name=name, asUtility=1)
    else:
        node = pm.shadingNode("floatConstant", asUtility=1)


    # ...Pass arguments to floatConstant inFloat attribute 'inFloat'. If the provided argument is numeric type, set the
    # ...attribute to match it. If it is an mObject attribute, connect it to the node's inFloat attribute.

    # ...inFloat
    if inFloat:

        if isinstance(inFloat, (int, float)):
            node.inFloat.set(inFloat)
        else:
            inFloat.connect(node.inFloat)


    # ....Connect node's outFloat attribute to its destination
    if outFloat:
        node.outFloat.connect(outFloat)



    return node





########################################################################################################################
def addDoubleLinear(name=None, input1=None, input2=None, output=None, force=False):
    """
        Creates a addDoubleLinear utility node to specifications provided in arguments.
        Args:
            name (string): Node's name.
            input1 (numeric/ mObject attribute plug): 'input1' attr input. Takes either a numeric value, or if arg is
                mPlug type, connects plug into 'input1' attr.
            input2 (numeric/ mPlug): 'input2' attr input. Takes either a numeric value, or if arg is
                mPlug type, connects plug into 'input2' attr.
            output (mPlug): Attribute plug node's output to pipe into.
        Returns:
            (utility node) The new addDoubleLinear node.
    """



    # ...Create multDoubleLinear node
    if name:
        node = pm.shadingNode("addDoubleLinear", name=name, asUtility=1)
    else:
        node = pm.shadingNode("addDoubleLinear", asUtility=1)

    # ...Pass arguments to addDoubleLinear input attributes 'input1' and 'input2'. If the provided arguments are numeric
    # ...types, set the attributes to match them. If they are mObject attributes, connect them to the addDoubleLinear
    # ...node's input attributes.



    # ...input1
    if input1:

        if isinstance(input1, (int, float)):
            node.input1.set(input1)
        else:
            pm.connectAttr(input1, node.input1)

    # ...input2
    if input2:

        if isinstance(input2, (int, float)):
            node.input2.set(input2)
        else:
            pm.connectAttr(input2, node.input2)



    # ...Connect node's output attribute to its destination
    if output:
        if not isinstance(output, (tuple, list)):
            node.output.connect(output, force=1)
        else:
            for plug in output:
                pm.connectAttr(node.output, plug, force=force)


    return node





########################################################################################################################
def multDoubleLinear(name=None, input1=None, input2=None, output=None):
    """
        Creates a multDoubleLinear utility node to specifications provided in arguments.
        Args:
            name (string): Node's name.
            input1 (numeric/ mObject attribute plug): 'input1' attr input. Takes either a numeric value, or if arg is
                mPlug type, connects plug into 'input1' attr.
            input2 (numeric/ mPlug): 'input2' attr input. Takes either a numeric value, or if arg is
                mPlug type, connects plug into 'input2' attr.
            output (mPlug): Attribute plug node's output to pipe into.
        Returns:
            (utility node) The new multDoubleLinear node.
    """


    # ...Create multDoubleLinear node
    if name:
        node = pm.shadingNode("multDoubleLinear", name=name, asUtility=1)
    else:
        node = pm.shadingNode("multDoubleLinear", asUtility=1)

    # ...Pass arguments to multDoubleLinear input attributes 'input1' and 'input2'. If the provided arguments are
    # ...numeric types, set the attributes to match them. If they are mObject attributes, connect them to the
    # ...multDoubleLinear node's input attributes.

    # ...input1
    if input1:

        if isinstance(input1, (int, float)):
            node.input1.set(input1)
        else:
            pm.connectAttr(input1, node.input1)

    # ...input2
    if input2:

        if isinstance(input2, (int, float)):
            node.input2.set(input2)
        else:
            pm.connectAttr(input2, node.input2)



    # ...Connect node's output attribute to its destination
    if output:
        pm.connectAttr(node.output, output)



    return node





########################################################################################################################
def remapValue(name=None, inputValue=0, inputMin=0, inputMax=1, outputMin=0, outputMax=1, outValue=None):


    if name:
        node = pm.shadingNode("remapValue", name=name, au=1)
    else:
        node = pm.shadingNode("remapValue", au=1)


    if inputValue:
        if isinstance(inputValue, (float, int)):
            node.inputValue.set(inputValue)
        else:
            pm.connectAttr(inputValue, node.inputValue)


    if inputMin:
        if isinstance(inputMin, (float, int)):
            node.inputMin.set(inputMin)
        else:
            pm.connectAttr(inputMin, node.inputMin)


    if inputMax:
        if isinstance(inputMax, (float, int)):
            node.inputMax.set(inputMax)
        else:
            pm.connectAttr(inputMax, node.inputMax)


    if outputMin:
        if isinstance(outputMin, (float, int)):
            node.outputMin.set(outputMin)
        else:
            pm.connectAttr(outputMin, node.outputMin)


    if outputMax:
        if isinstance(outputMax, (float, int)):
            node.outputMax.set(outputMax)
        else:
            pm.connectAttr(outputMax, node.outputMax)


    if outValue:
        if isinstance(outValue, (list, tuple)):
            for plug in outValue:
                pm.connectAttr(node.outValue, plug)

        else:
            node.outValue.connect(outValue)


    return node





########################################################################################################################
def reverse(name=None, input=None, output=None, output_x=None, output_y=None, output_z=None):

    if name:
        node = pm.shadingNode("reverse", name=name, au=1)
    else:
        node = pm.shadingNode("reverse", au=1)


    if input:
        if isinstance(input, (float, int)):
            node.input.set(input)
        else:
            input.connect(node.input)


    if output:
        node.output.connect(output)

    if output_x:
        node.outputX.connect(output_x)
    if output_y:
        node.outputX.connect(output_y)
    if output_z:
        node.outputX.connect(output_z)


    return node





########################################################################################################################
def curveInfo():
    pass





########################################################################################################################
def pointOnCurveInfo():
    pass





########################################################################################################################
def pointOnSurfaceInfo(name=None, useLocal=True, inputSurface=None, turnOnPercentage=True, parameterV=1, parameterU=1,
                       resultPosition=None, resultNormal=None, resultNormalizedNormal=None, resultTangentU=None,
                       resultNormalizedTangentU=None, resultTangentV=None, resultNormalizedTangentV=None):



    # ...Create node
    node = None
    if name:
        node = pm.shadingNode("pointOnSurfaceInfo", name=name, au=1)
    else:
        node = pm.shadingNode("pointOnSurfaceInfo", au=1)


    # ...Plug in input surface
    if inputSurface:
        if inputSurface.nodeType() != "nurbsSurface":
            pm.error("Invalid argument given to parameter: '{0}'. Needs node type: '{1}'".format("input_surface",
                                                                                                 "nurbsSurface"))
        if useLocal:
            pm.connectAttr(inputSurface.local, node + ".inputSurface")
        else:
            pm.connectAttr(inputSurface.worldSpace, node + ".inputSurface")


    # ...Set parameters
    if isinstance(turnOnPercentage, bool):
        node.turnOnPercentage.set(turnOnPercentage)
    else:
        pm.connectAttr(turnOnPercentage, node.turnOnPercentage)


    if isinstance(parameterV, (int, float)):
        node.parameterV.set(parameterV)
    else:
        pm.connectAttr(parameterV, node.parameterV)


    if isinstance(parameterU, (int, float)):
        node.parameterU.set(parameterU)
    else:
        pm.connectAttr(parameterU, node.parameterU)



    # ...Connect outputs (if provided)
    pm.connectAttr(resultPosition, node.result.position) if resultPosition else None
    pm.connectAttr(resultNormal, node.result.normal) if resultNormal else None
    pm.connectAttr(resultNormalizedNormal, node.result.normalizedNormal) if resultNormalizedNormal else None
    pm.connectAttr(resultTangentU, node.result.tangentU) if resultTangentU else None
    pm.connectAttr(resultNormalizedTangentU, node.result.normalizedTangentU) if resultNormalizedTangentU else None
    pm.connectAttr(resultTangentV, node.result.tangentV) if resultTangentV else None
    pm.connectAttr(resultNormalizedTangentV, node.result.normalizedTangentV) if resultNormalizedTangentV else None



    return node





########################################################################################################################
def multiplyDivide(name=None, input1=None, input2=None, operation=None, output=None):


    # ...Derive correct numerical value for operation arg if provided arg is a string
    if operation:
        if isinstance(operation, str):
            operation_strings = {0: ["None", "none", "noOperation", "no_operation", "no operation", "0"],
                                 1: ["mult", "Mult", "multiply", "multiplication", "product", "times", "1"],
                                 2: ["div", "Div", "divide", "division", "divide by"],
                                 3: ["power", "exponent", "exp", "exponentiate", "exponentiation"]}

            for key in operation_strings:
                if operation in operation_strings[key]:
                    operation = key
                break


    # ...Create node
    if name:
        node = pm.shadingNode("multiplyDivide", name=name, au=1)
    else:
        node = pm.shadingNode("multiplyDivide", au=1)


    # ...input1
    input1_array = ["input1X", "input1Y", "input1Z"]

    if input1:
        if isinstance(input1, (list, tuple)):
            input1 = tuple(input1) if isinstance(input1, list) else None
            for i in range(3):
                if isinstance(input1[i], (int, float)):
                    pm.setAttr(node + "." + input1_array[i], input1[i])
                else:
                    pm.connectAttr(input1[i], node + "." + input1_array[i])
        else:
            pm.connectAttr(input1, node.input1)

    # ...input2
    input2_array = ["input2X", "input2Y", "input2Z"]

    if input2:
        if isinstance(input2, (list, tuple)):
            input2 = tuple(input2) if not isinstance(list, tuple) else input2
            for i in range(3):
                if isinstance(input2[i], (int, float)):
                    pm.setAttr(node + "." + input2_array[i], input2[i])
                else:
                    pm.connectAttr(input2[i], node + "." + input2_array[i])
        else:
            pm.connectAttr(input2, node.input2)


    # ...operation
    if operation:
        if isinstance(operation, (int, float)):
            pm.setAttr(node.operation, operation)
        else:
            pm.connectAttr(operation, node.operation)


    # ...output
    output_array = ["outputX", "outputY", "outputZ"]

    if output:
        if isinstance(output, (list, tuple)):
            output = tuple(output) if isinstance(output, list) else None
            for i in range(3):
                pm.connectAttr(node + "." + output_array[i], output[i])

        else:
            node.output.connect(output)



    return node





########################################################################################################################
def plusMinusAverage():
    pass





########################################################################################################################
def condition(name=None, firstTerm=0, secondTerm=0, colorIfTrue=None, colorIfFalse=None, operation=0, outColor=None):
    """

        Args:
            name (string):
            firstTerm (numeric):
            secondTerm (numeric):
            colorIfTrue ([numeric, numeric, numeric[):
            colorIfFalse ([numeric, numeric, numeric]):
            operation (int/string):
            outColor ([plug, plug, plug]):
        Return:
            (condition node): The created condition node.
    """

    force_outgoing_connections = 1


    operations_dict = {
        0 : (0, "equal"),
        1 : (1, "not equal", "notEqual", "not_equal"),
        2 : (2, "greater than", "greaterThan", "greater_than", "greater"),
        3 : (3, "greater or equal", "greaterOrEqual", "greater_or_equal", "greater or equal to", "greaterOrEqualTo",
             "greater_or_equal_to", "greater than or equal to"),
        4 : (4, "less than", "lessThan", "less_than", "less"),
        5 : (5, "less than or equal", "lessThanOrEqual", "less_than_or_equal", "less than or equal to",
             "lessThanOrEqualTo", "less_than_or_equal_to"),
    }


    if not colorIfTrue:
        colorIfTrue = [0, 0, 0]
    if not colorIfFalse:
        colorIfFalse = [1, 1, 1]
    if not outColor:
        outColor = [None, None, None]


    color_if_true_attrs = ["colorIfTrue.colorIfTrueR",
                           "colorIfTrue.colorIfTrueG",
                           "colorIfTrue.colorIfTrueB"]
    color_if_false_attrs = ["colorIfFalse.colorIfFalseR",
                            "colorIfFalse.colorIfFalseG",
                            "colorIfFalse.colorIfFalseB"]
    out_color_attrs = ["outColor.outColorR",
                       "outColor.outColorG",
                       "outColor.outColorB"]

    if name:
        node = pm.shadingNode("condition", name=name, au=1)
    else:
        node = pm.shadingNode("condition", au=1)



    if isinstance(firstTerm, (int, float)):
        node.firstTerm.set(firstTerm)
    else:
        pm.connectAttr(firstTerm, node.firstTerm)



    if isinstance(secondTerm, (int, float)):
        node.secondTerm.set(secondTerm)
    else:
        pm.connectAttr(secondTerm, node.secondTerm)



    for key in operations_dict:
        if operation in operations_dict[key]:
            node.operation.set(key)



    for i in range(3):


        if isinstance(colorIfTrue[i], (int, float)):
            pm.setAttr(node + "." + color_if_true_attrs[i], colorIfTrue[i])
        else:
            pm.connectAttr(colorIfTrue[i], node + "." + color_if_true_attrs[i])


        if isinstance(colorIfFalse[i], (int, float)):
            pm.setAttr(node + "." + color_if_false_attrs[i], colorIfFalse[i])
        else:
            pm.connectAttr(colorIfFalse[i], node + "." + color_if_false_attrs[i])


        if outColor[i]:
            if not isinstance(outColor[i], list):
                out_color_list = [outColor[i]]
                for plug in out_color_list:
                    pm.connectAttr( node + "." + out_color_attrs[i], plug, force=force_outgoing_connections)



    return node





########################################################################################################################
def fourByFourMatrix(input=None, output=None, name=None):


    if name:
        node = pm.shadingNode("fourByFourMatrix", name=name, au=1)
    else:
        node = pm.shadingNode("fourByFourMatrix", au=1)

    input_attrs = ["in00", "in01", "in02", "in03",
                   "in10", "in11", "in12", "in13",
                   "in20", "in21", "in22", "in23",
                   "in30", "in31", "in32", "in33"]

    if input:
        for inp, a in zip(input, input_attrs):
            if isinstance(inp, (int, float)):
                pm.setAttr(node + "." + a, inp)
            else:
                pm.connectAttr(inp, node + "." + a)

    if output:
        pm.connectAttr(node + ".output", output)


    return node





########################################################################################################################
def distanceBetween(name=None, point1=None, point2=None, inMatrix1=None, inMatrix2=None, distance=None):

    if name:
        node = pm.shadingNode("distanceBetween", name=name, au=1)
    else:
        node = pm.shadingNode("distanceBetween", au=1)

    if point1:
        pm.connectAttr(point1, node.point1)
    if point2:
        pm.connectAttr(point2, node.point2)

    if inMatrix1:
        pm.connectAttr(inMatrix1, node.inMatrix1)
    if inMatrix2:
        pm.connectAttr(inMatrix2, node.inMatrix2)

    if distance:
        pm.connectAttr(node.distance, distance)


    return node





########################################################################################################################
def multMatrix(name=None, matrixIn=None, matrixSum=None):

    if name:
        node = pm.shadingNode("multMatrix", name=name, au=1)
    else:
        node = pm.shadingNode("multMatrix", au=1)


    if matrixIn:
        if not isinstance(matrixIn, (list, tuple)):
            matrixIn = (matrixIn,)
        for i, v in enumerate(matrixIn):
            pm.connectAttr(v, node.matrixIn[i])


    if matrixSum:
        if not isinstance(matrixSum, (list, tuple)):
            matrixSum = (matrixSum,)

        for v in matrixSum:
            pm.connectAttr(node.matrixSum, v)



    return node





########################################################################################################################
def decomposeMatrix(name=None, inputMatrix=None, outputQuat=None, outputTranslate=None, outputRotate=None,
                    outputScale=None, outputShear=None, force=False):

    if name:
        node = pm.shadingNode("decomposeMatrix", name=name, au=1)
    else:
        node = pm.shadingNode("decomposeMatrix", au=1)


    if inputMatrix:
        pm.connectAttr(inputMatrix, node.inputMatrix)


    # Outputs --------------------------------------------------
    if outputQuat:
        if not isinstance(outputQuat, (list, tuple)):
            outputQuat = (outputQuat,)

        for v in outputQuat:
            pm.connectAttr(node.outputQuat, v, f=force)


    if outputTranslate:
        if not isinstance(outputTranslate, (list, tuple)):
            outputTranslate = (outputTranslate,)

        for v in outputTranslate:
            pm.connectAttr(node.outputTranslate, v, f=force)


    if outputRotate:
        if not isinstance(outputRotate, (list, tuple)):
            outputRotate = (outputRotate,)

        for v in outputRotate:
            pm.connectAttr(node.outputRotate, v, f=force)


    if outputScale:
        if not isinstance(outputScale, (list, tuple)):
            outputScale = (outputScale,)

        for v in outputScale:
            pm.connectAttr(node.outputScale, v, f=force)


    if outputShear:
        if not isinstance(outputShear, (list, tuple)):
            outputShear = (outputShear,)

        for v in outputShear:
            pm.connectAttr(node.outputShear, v, f=force)



    return node





########################################################################################################################
def clamp(name=None, input=(None, None, None), min=(0, 0, 0), max=(1, 1, 1), output=(None, None, None)):


    if name:
        node = pm.shadingNode("clamp", name=name, au=1)
    else:
        node = pm.shadingNode("clamp", au=1)


    if input:
        sub_plugs = ("inputR", "inputG", "inputB")
        for i in range(3):
            if input[i]:
                if isinstance(input[i], (int, float)):
                    pm.setAttr(node + "." + sub_plugs[i], input[i])
                else:
                    pm.connectAttr(input[i], node + "." + sub_plugs[i])


    if min:
        sub_plugs = ("minR", "minG", "minB")
        for i in range(3):
            if min[i]:
                if isinstance(min[i], (int, float)):
                    pm.setAttr(node + "." + sub_plugs[i], min[i])
                else:
                    pm.connectAttr(min[i], node + "." + sub_plugs[i])


    if max:
        sub_plugs = ("maxR", "maxG", "maxB")
        for i in range(3):
            if max[i]:
                if isinstance(max[i], (int, float)):
                    pm.setAttr(node + "." + sub_plugs[i], max[i])
                else:
                    pm.connectAttr(max[i], node + "." + sub_plugs[i])


    if output:
        sub_plugs = ("outputR", "outputG", "outputB")
        for i in range(3):
            if output[i]:
                pm.connectAttr(node + "." + sub_plugs[i], output[i])


    return node





########################################################################################################################
def blendMatrix(name=None, inputMatrix=None, targetMatrix=None, useMatrix=None, weight=None, useScale=None,
                useTranslate=None, useShear=None, useRotate=None, outputMatrix=None):

    if name:
        node = pm.shadingNode("blendMatrix", name=name, au=1)
    else:
        node = pm.shadingNode("blendMatrix", au=1)


    if inputMatrix:
        pm.connectAttr(inputMatrix, node.inputMatrix)


    if targetMatrix:
        if not isinstance(targetMatrix, (list, tuple)):
            targetMatrix = (targetMatrix,)
        [pm.connectAttr(tm, targ.targetMatrix) for tm, targ in zip(targetMatrix, node.target)]


    if useMatrix:
        if not isinstance(useMatrix, (list, tuple)):
            useMatrix = (useMatrix,)
        [pm.connectAttr(um, targ.useMatrix) for um, targ in zip(useMatrix, node.target)]


    if weight:
        if not isinstance(weight, (list, tuple)):
            weight = (weight,)
        [pm.connectAttr(w, targ.weight) for w, targ in zip(weight, node.target)]


    if useScale:
        if not isinstance(useScale, (list, tuple)):
            useScale = (useScale,)
        [pm.connectAttr(us, targ.useScale) for us, targ in zip(useScale, node.target)]


    if useTranslate:
        if not isinstance(useTranslate, (list, tuple)):
            useTranslate = (useTranslate,)
        [pm.connectAttr(ut, targ.useTranslate) for ut, targ in zip(useTranslate, node.target)]


    if useShear:
        if not isinstance(useShear, (list, tuple)):
            useShear = (useShear,)
        [pm.connectAttr(us, targ.useShear) for us, targ in zip(useShear, node.target)]


    if useRotate:
        if not isinstance(useRotate, (list, tuple)):
            useRotate = (useRotate,)
        [pm.connectAttr(ur, targ.useRotate) for ur, targ in zip(useRotate, node.target)]



    if outputMatrix:
        if not isinstance(outputMatrix, (list, tuple)):
            outputMatrix = (outputMatrix,)
        [pm.connectAttr(node.outputMatrix, v) for v in outputMatrix]


    return node
