import logging
import os
import traceback
import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectDictProperty
import Snowman3.rigger.rig_factory.common_modules as com

DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


class Plug(BaseObject):

    create_data = DataProperty( name='create_data' )
    create_kwargs = DataProperty( name='create_kwargs' )
    user_defined = DataProperty( name='user_defined' )
    array_plug = ObjectProperty( name='array_plug' )
    elements = ObjectDictProperty( name='elements' )
    default_value = DataProperty( name='default_value' )
    child_plugs = ObjectDictProperty( name='child_plugs' )
    index = DataProperty( name='index' )
    m_plug = None
    child_plug_names = {}
    __is_array__ = False


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        kwargs = super().pre_process_kwargs(**kwargs)
        kwargs['namespace'] = None  # namespace will be taken from node
        return kwargs


    @classmethod
    def create(cls, **kwargs):
        parent = kwargs.get('parent', None)
        root_name = kwargs.get('root_name', None)
        root_name_short = root_name
        if not parent:
            raise Exception(
                'You must provide a "parent" keyword argument to create a %s' % Plug.__name__
            )
        elif not isinstance(parent, Plug):
            if not root_name:
                raise Exception(
                    'You must provide a "root_name" keyword argument to create a %s' % Plug.__name__
                )
        index = kwargs.get('index', None)
        controller = com.controller_utils.get_controller()
        m_plug = None
        is_array = False


        '''
        if controller.scene.mock:
            if isinstance(parent, com.objects.DependNode):
                kwargs['name'] = '%s.%s' % (parent.name, root_name)
            elif isinstance(parent, Plug):
                kwargs['name'] = '%s.%s[%s]' % (parent.name, root_name, index)
            else:
                raise Exception('Invalid parent type for plug: %s' % type(parent))
        else:
        '''
        # Get m_plug first in order to have accurate name
        if kwargs.get('user_defined', False):
            create_kwargs = kwargs.get('create_kwargs', {})
            m_plug = controller.scene.create_plug(
                parent.m_object,
                root_name,
                **create_kwargs
            )
        else:
            if isinstance(parent, Plug):
                if index is None:
                    raise Exception(
                        'You must provide a "index" keyword argument to create an element or child plug'
                    )
                m_plug = controller.scene.initialize_plug( parent.m_plug, index )
                if parent.m_plug.isCompound:
                    plug_name = m_plug.partialName(False, False, False, False, False, True)  # useLongNames=True)
                    kwargs['root_name'] = "%s.%s" % (parent.root_name, plug_name)
                else:
                    kwargs['root_name'] = "%s[%s]" % (parent.root_name, index)
            else:
                print(parent.__dict__)
                m_plug = controller.scene.initialize_plug( parent.m_object, root_name )
                root_name_long = m_plug.partialName(False, False, False, False, False, True)  # useLongNames=True)
                kwargs['root_name'] = root_name_long  # Use long name for root name
                root_name_short = m_plug.partialName()
        is_array = m_plug.isArray  # is_array = m_plug.isArray
        plug_name = str(m_plug.name())
        kwargs['name'] = plug_name  # Gives proper full name for compound children etc


        this = super().create(**kwargs)
        if len(this.name.split(':')) > 2:
            raise Exception('Double namespaces not supported: %s' % this.name)
        this.m_plug = m_plug
        this.parent = parent
        this.__is_array__ = is_array
        if this.array_plug:
            if DEBUG:
                if this.index is None:
                    raise Exception('index for array plug "%s" is "None" (use integer)' % this.name)
                if this.index in this.array_plug.elements:
                    raise Exception('An index plug at %s already exists under %s' % (this.index, this.array_plug.name))
            this.array_plug.elements[this.index] = this
        elif isinstance(this.parent, Plug):
            if DEBUG:
                if this.index is None:
                    raise Exception('index for child plug "%s" is None (use integer)' % this.name)
                if this.index in this.parent.child_plugs:
                    raise Exception('A child plug at %s already exists under %s' % (this.index, this.parent.name))
            this.parent.child_plugs[this.index] = this
        else:
            this.parent.existing_plugs[this.root_name] = this  # Should be long name
            this.parent.existing_plugs[root_name_short] = this
        return this

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.m_plug = None
        self.child_plug_names = {}  # Dict of ints

    def __getitem__(self, item):
        """ Allow indexing or accessing compound plug children by name key """
        if self.is_array():
            return self.element(item)
        return self.child(item)

    def is_array(self):
        if self.controller.scene.mock:
            return bool(self.elements)
        return self.__is_array__

    def get_next_avaliable_index(self):  # << Fix this typo
        return self.controller.scene.get_next_avaliable_plug_index(self.m_plug)


    def get_node(self):
        parent = self.parent
        while isinstance(parent, Plug):
            parent = parent.parent
        return parent

    def get_short_name(self, *args):
        if self.m_plug:
            return self.m_plug.partialName()
        elif args:
            return args[0]

    def get_long_name(self, *args):
        if self.m_plug:
            return self.m_plug.partialName(False, False, False, False, False, True)  # useLongNames=True
        elif args:
            return args[0]

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s.%s' % (
            self.get_node().get_selection_string(),
            self.root_name
        )

    def create_depend_node(self, node_type):
        node = self.get_node()

        # Use key to get text either side of segment_name
        key = 'XXX-'  # Not used in final name. Dash to ensure string doesn't already exist, A to pass .isupper() check
        name_pattern = com.objects.DependNode.get_predicted_name(
            namespace=node.controller.namespace,
            root_name=node.root_name,
            node_type=node_type,
            segment_name=key,
            differentiation_name=node.differentiation_name,
            functionality_name=node.functionality_name,
            side=node.side
        )
        name_pre, name_post = name_pattern.rsplit(key, 1)

        # Get first valid index
        for segment_id in rig_factory.index_list:  # A, B, C, D... Aa, Ab..
            segment_name = segment_id.title()
            assembled_name = name_pre + segment_name + name_post
            if assembled_name not in node.controller.named_objects:
                break
        else:
            raise Exception("Reached max supported char indices!")

        return node.create_child(
            com.objects.DependNode,
            node_type=node_type,
            segment_name=segment_name
        )

    def __mul__(self, input):
        return self.multiply(input)

    def __add__(self, input):
        return self.add(input)

    def __mod__(self, values):
        return self.remap(*values)

    def reverse(self):
        rev = self.create_depend_node('reverse')
        self.connect_to(rev.plugs['inputX'])
        return rev.plugs['outputX']

    def multiply(self, input):
        multiply_node = self.create_depend_node('multDoubleLinear')
        self.connect_to(multiply_node.plugs['input1'])
        if isinstance(input, (int, float)):
            multiply_node.plugs['input2'].set_value(input)
        elif isinstance(input, Plug):
           input.connect_to(multiply_node.plugs['input2'])
        else:
            raise Exception('Invalid type "%s"' % type(input))
        return multiply_node.plugs['output']

    def divide(self, input):
        divide_node = self.create_depend_node('multiplyDivide')
        divide_node.plugs['operation'].set_value(2)
        self.connect_to(divide_node.plugs['input1X'])
        if isinstance(input, (int, float)):
            divide_node.plugs['input2X'].set_value(input)
        elif isinstance(input, Plug):
           input.connect_to(divide_node.plugs['input2X'])
        else:
            raise Exception('Invalid type "%s"' % type(input))
        return divide_node.plugs['outputX']

    def square_root(self):
        multiply_node = self.create_depend_node('multiplyDivide')
        self.connect_to(multiply_node.plugs['input1X'])
        multiply_node.plugs['input2X'].set_value(0.5)
        multiply_node.plugs['operation'].set_value(3)
        return multiply_node.plugs['outputX']

    def subtract(self, input):
        subtract_node = self.create_depend_node('plusMinusAverage')
        subtract_node.plugs['operation'].set_value(2)
        self.connect_to(subtract_node.plugs['input1D'].element(0))
        if isinstance(input, (int, float)):
            subtract_node.plugs['input1D'].element(1).set_value(input)
        elif isinstance(input, Plug):
            input.connect_to(subtract_node.plugs['input1D'].element(1))
        else:
            raise Exception('Invalid type "%s"' % type(input))
        return subtract_node.plugs['output1D']

    def add(self, input):
        add_node = self.create_depend_node('addDoubleLinear')
        self.connect_to(add_node.plugs['input1'])
        if isinstance(input, (int, float)):
            add_node.plugs['input2'].set_value(input)
        elif isinstance(input, Plug):
            input.connect_to(add_node.plugs['input2'])
        else:
            raise Exception('Invalid type "%s"' % type(input))
        return add_node.plugs['output']

    def remap(self, *values):
        remap_node = self.create_depend_node('remapValue')
        for i in range(len(values)):
            in_value, out_value = values[i]
            remap_node.plugs['value'].element(i).child(0).set_value(in_value)
            remap_node.plugs['value'].element(i).child(1).set_value(out_value)
            remap_node.plugs['value'].element(i).child(2).set_value(1)
        self.connect_to(
            remap_node.plugs['inputValue']
        )
        return remap_node.plugs['outValue']

    def blend_weighted(self, *others):
        blend_weighted_node = self.create_depend_node('blendWeighted')
        self.connect_to(blend_weighted_node.plugs['input'].element(0))
        blend_weighted_node.plugs['weight'].element(0).set_value(1.0)
        for i, other in enumerate(others, start=1):
            other.connect_to(blend_weighted_node.plugs['input'].element(i))
            blend_weighted_node.plugs['weight'].element(i).set_value(1.0)
        return blend_weighted_node.plugs['output']

    def clamp(self, min, max):
        clamp_node = self.create_depend_node('clamp')
        self.connect_to(clamp_node.plugs['inputR'])
        clamp_node.plugs['minR'].set_value(min)
        clamp_node.plugs['maxR'].set_value(max)
        return clamp_node.plugs['outputR']

    def set_range(self, in_min=0, in_max=1, out_min=0, out_max=1):
        range_node = self.create_depend_node('setRange')
        self.connect_to(range_node.plugs['valueX'])
        range_node.plugs['oldMinX'].set_value(in_min)
        range_node.plugs['oldMaxX'].set_value(in_max)
        range_node.plugs['minX'].set_value(out_min)
        range_node.plugs['maxX'].set_value(out_max)
        return range_node.plugs['outValueX']

    def get_incoming_plugs(self):
        for plug_name in self.controller.scene.listConnections(self.name, s=True, d=False, plugs=True):
            raise Exception('Not Implemeted')

    def is_element(self):
        return isinstance(self.array_plug, Plug)

    def set_value(self, value):
        self.controller.set_plug_value(self, value)

    def get_value(self, *args):
        return self.controller.get_plug_value(self, *args)

    def get_data(self):
        """
        This could use MPlug
        """
        scene = self.controller.scene
        node = self.get_node().name
        attribute = self.root_name
        plug_name = '%s.%s' % (node, attribute)
        attribute_type = scene.getAttr(plug_name, type=True)
        data = dict(
            node=node,
            name=attribute,
            long_name=scene.attributeQuery(attribute, node=node, longName=True),
            current_value=scene.getAttr(plug_name),
            locked=scene.getAttr(plug_name, lock=True),
            channelbox=scene.getAttr(plug_name, channelBox=True),
            keyable=scene.getAttr(plug_name, keyable=True),
            type=attribute_type
        )
        if self.m_plug.isDynamic():
            data['dv'] = scene.addAttr(plug_name, q=True, dv=True)
        if attribute_type == 'enum':
            data['listEnum'] = scene.attributeQuery(attribute, node=node, listEnum=True)[0]
        if scene.attributeQuery(attribute, node=node, minExists=True):
            data['min'] = scene.attributeQuery(attribute, node=node, min=True)[0]
        if scene.attributeQuery(attribute, node=node, maxExists=True):
            data['max'] = scene.attributeQuery(attribute, node=node, max=True)[0]
        return data

    def set_channel_box(self, value):
        if self.m_plug:
            self.m_plug.isChannelBox = value  # return self.m_plug.setChannelBox(value)
            return self.m_plug.isChannelBox

    def element(self, index):
        if not isinstance(index, int):
            raise Exception('plug elements can only be retrieved by index integer, not "%s"' % type(index))
        if index in self.elements:
            return self.elements[index]
        return self.create_child(
            Plug,
            index=index,
            array_plug=self
        )

    def child(self, key):
        if isinstance(key, int):
            # Get or initialise plug by index
            initialised_plug = self.child_plugs.get(key, None)
            if initialised_plug is not None:
                return initialised_plug
            return self.create_child(
                Plug,
                index=key
            )

        if not isinstance(key, str):
            raise Exception('Plug children can only be retrieved by index integer or str, not "%s"' % type(key))

        # Get or initialise (compound only) plug by name
        plug_index = self.child_plug_names.get(key, None)
        if plug_index is not None:
            return self.child_plugs[plug_index]

        if not self.m_plug:
            # Mock mode
            next_id_guess = len(self.child_plug_names)
            self.child_plug_names[key] = next_id_guess
            return self.child(next_id_guess)

        # Check for valid sub-plug name (eg. 'scaleX' or 'sx') by initialising children until finding a matching one
        for i in range(self.controller.scene.get_plug_compound_children_count(self)):
            # Initialise child plug and cache long and short names
            child_plug = self.child(i)
            child_plug_name = child_plug.get_long_name()
            child_plug_name_short = child_plug.get_short_name()
            self.child_plug_names[child_plug_name] = i
            self.child_plug_names[child_plug_name_short] = i

            if key in (child_plug_name, child_plug_name_short):
                return child_plug

        raise Exception('Plug "%s" has no child named "%s"' % (self.root_name, key))

    def connect_to(self, plug):
        try:
            self.controller.scene.connect_plugs(
                self.m_plug,
                plug.m_plug
            )
        except Exception:
            logging.getLogger('rig_build').error(traceback.format_exc())
            raise Exception('Failed to connect %s to %s\nCheck the script editor for a stack-trace.' % (self, plug))

    def disconnect_from(self, plug):
        self.controller.scene.disconnect_plugs(
            self.m_plug,
            plug.m_plug
        )

    def set_keyable(self, value):
        self.controller.scene.set_plug_keyable(self, value)  # maya setAttr doesn't like the __getitem__ method...

    def set_locked(self, value):
        self.controller.scene.set_plug_locked(self, value)

    def set_hidden(self, value):
        self.controller.scene.set_plug_hidden(self, value)

    def get_keyable(self, value):
        return self.controller.scene.get_plug_keyable(self, value)

    def get_locked(self):
        return self.controller.scene.get_plug_locked(self)

    def get_hidden(self):
        return self.controller.scene.get_plug_hidden(self)

    def is_connected(self):
        connected = self.controller.scene.listConnections(
            self.name,
            s=True,
            d=False
        )
        if connected:
            return True

    def update_name(self):
        """ Update name if node name changed """
        self.name = str(self.m_plug.name()) if self.m_plug else repr(self)  # mock mode
        for childPlug in self.child_plugs.values():
            childPlug.update_name()

    def rename(self, name):
        self.controller.scene.renameAttr(self.m_plug.name(), name)
        self.update_name()

    def teardown(self):
        super().teardown()
