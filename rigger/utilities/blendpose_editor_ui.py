# Title: blendpose_editor_ui.py
# Author: Sam Leheny
# Contact: samleheny@live.com


###########################
##### Import Commands #####
import sys
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import pymel.core as pm
import maya.cmds as mc
import maya.OpenMayaUI as omui
from functools import partial
import Snowman3.rigger.utilities.blendpose_utils as bp_utils
BlendposeManager = bp_utils.BlendposeManager
###########################
###########################



def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



class BlendposeEditor(QtWidgets.QDialog):

    WINDOW_TITLE = 'Blendpose Editor'
    VALUE_ROLE = QtCore.Qt.UserRole + 1
    ANIM_CURVE_NODE_TYPES = ('animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU',
                             'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU')
    SLIDER_RANGE_MULT = 10000

    def __init__(self, parent=maya_main_window()):
        super(BlendposeEditor, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if sys.version_info.major >= 3:
            self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        else:
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setMinimumWidth(600)

        self.tree_wdg = None
        self.refresh_btn = None

        self.script_job_ids = {}

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        #self.blendpose_manager = BlendposeManager.populate_manager_from_scene()
        self.blendpose_manager = None

        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.show_context_menu)

        self.refresh_tree_widget()

    def create_actions(self):
        self.create_blendpose_action = QtWidgets.QAction('Blendpose Node', self)
        self.create_target_pose_action = QtWidgets.QAction('Add Target', self)
        self.duplicate_target_pose_action = QtWidgets.QAction('Duplicate Target', self)
        self.add_selected_objs_action = QtWidgets.QAction('Add Selected Objs', self)
        self.remove_selected_objs_action = QtWidgets.QAction('Remove Selected Objs', self)
        self.select_target_objs_action = QtWidgets.QAction('Select Target Objects', self)
        self.select_hook_node_action = QtWidgets.QAction('Select Hook Node', self)
        self.delete_blendpose_action = QtWidgets.QAction('Delete', self)
        self.delete_target_pose_action = QtWidgets.QAction('Delete', self)
        self.mirror_target_pose_action = QtWidgets.QAction('Mirror Target', self)
        self.flip_target_pose_action = QtWidgets.QAction('Flip Target', self)

    def create_widgets(self):
        self.menu_bar = self.build_editor_menu_bar()

        self.tree_wdg = QtWidgets.QTreeWidget()
        self.tree_wdg.setColumnCount(2)
        header = self.tree_wdg.headerItem()
        header.setTextAlignment(0, QtCore.Qt.AlignCenter)
        header.setText(0, 'Name')
        header.setTextAlignment(1, QtCore.Qt.AlignCenter)
        header.setText(1, 'Weight/Drivers')
        header.setTextAlignment(2, QtCore.Qt.AlignCenter)
        header.setText(2, 'Edit')
        self.tree_wdg.header().setStretchLastSection(False)
        self.tree_wdg.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tree_wdg.header().resizeSection(2, 48)

        self.tree_wdg.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_wdg.customContextMenuRequested.connect(self.show_context_menu)

        self.refresh_btn = QtWidgets.QPushButton('Refresh')

    def build_editor_menu_bar(self):
        menu_bar = QtWidgets.QMenuBar()

        create_menu = menu_bar.addMenu('Create')
        create_menu.addAction(self.create_blendpose_action)
        create_menu.addSeparator()
        create_menu.addAction(self.create_target_pose_action)

        edit_menu = menu_bar.addMenu('Edit')
        edit_menu.addAction(self.add_selected_objs_action)
        edit_menu.addAction(self.remove_selected_objs_action)
        edit_menu.addAction(self.select_target_objs_action)
        edit_menu.addSeparator()

        poses_menu = menu_bar.addMenu('Poses')
        poses_menu.addAction(self.duplicate_target_pose_action)
        poses_menu.addSeparator()

        return menu_bar

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        main_layout.setMenuBar(self.menu_bar)

        main_layout.addWidget(self.tree_wdg)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.set_item_changed_connection_enabled(True)
        self.refresh_btn.clicked.connect(self.refresh_tree_widget)
        self.tree_wdg.itemCollapsed.connect(self.toggle_blendpose_collapsed)
        self.tree_wdg.itemExpanded.connect(self.toggle_blendpose_collapsed)

        self.create_blendpose_action.triggered.connect(self.create_blendpose)
        self.create_target_pose_action.triggered.connect(self.create_target_pose)
        self.duplicate_target_pose_action.triggered.connect(self.duplicate_target_pose)
        self.add_selected_objs_action.triggered.connect(self.add_selected_objs_to_blendpose)
        self.remove_selected_objs_action.triggered.connect(self.remove_selected_objs_from_blendpose)
        self.select_target_objs_action.triggered.connect(self.select_target_objs_on_blendpose)
        self.select_hook_node_action.triggered.connect(self.select_hook_node)
        self.delete_blendpose_action.triggered.connect(self.delete_blendpose)
        self.delete_target_pose_action.triggered.connect(self.delete_target_pose)
        self.mirror_target_pose_action.triggered.connect(self.mirror_target_pose)
        self.flip_target_pose_action.triggered.connect(self.flip_target_pose)

    def toggle_blendpose_collapsed(self, item):
        collapsed_status = item.isExpanded()
        self.blendpose_manager.toggle_blendpose_collapsed(item.text(0), collapsed_status)

    def create_blendpose(self):
        self.blendpose_manager.create_blendpose()
        self.refresh_tree_widget()

    def delete_blendpose(self):
        blendpose_name = self.get_current_item_top_item().text(0)
        self.blendpose_manager.delete_blendpose(blendpose_name)
        self.refresh_tree_widget()

    def create_target_pose(self):
        top_item = self.get_current_item_top_item()
        blendpose_name = top_item.text(0)
        self.blendpose_manager.add_target_pose(blendpose_name)
        self.refresh_tree_widget()

    def delete_target_pose(self):
        target_pose_name = self.tree_wdg.currentItem().text(0)
        blendpose_name = self.get_current_item_top_item().text(0)
        self.blendpose_manager.delete_target_pose(target_pose_name, blendpose_name)
        self.refresh_tree_widget()

    def mirror_target_pose(self):
        target_pose_name = self.tree_wdg.currentItem().text(0)
        blendpose_name = self.get_current_item_top_item().text(0)
        self.blendpose_manager.mirror_target_pose(blendpose_name, target_pose_name)

    def flip_target_pose(self):
        target_pose_name = self.tree_wdg.currentItem().text(0)
        blendpose_name = self.get_current_item_top_item().text(0)
        self.blendpose_manager.flip_target_pose(blendpose_name, target_pose_name)

    def add_selected_objs_to_blendpose(self):
        objs = pm.ls(sl=1)
        # validate objs
        if not objs:
            return False
        blendpose_item = self.get_current_item_top_item()
        self.blendpose_manager.add_output_objs(blendpose_item.text(0), *objs)

    def remove_selected_objs_from_blendpose(self):
        objs = pm.ls(sl=1)
        # validate objs
        if not objs:
            return False
        blendpose_item = self.get_current_item_top_item()
        blendpose_key = blendpose_item.text(0)
        self.blendpose_manager.remove_output_objs(blendpose_key, *objs)

    def select_target_objs_on_blendpose(self):
        blendpose_item = self.get_current_item_top_item()
        blendpose_key = blendpose_item.text(0)
        target_objs = self.blendpose_manager.get_all_target_objs(blendpose_key)
        pm.select(target_objs, replace=1)

    def select_hook_node(self):
        blendpose_item = self.get_current_item_top_item()
        blendpose_key = blendpose_item.text(0)
        self.blendpose_manager.select_hook_node(blendpose_key)

    def duplicate_target_pose(self):
        current_item = self.tree_wdg.currentItem()
        if self.is_top_level_item(current_item):
            return False
        target_pose_name = current_item.text(0)
        blendpose_key = current_item.parent().text(0)
        self.blendpose_manager.duplicate_target_pose(target_pose_name, blendpose_key)
        self.refresh_tree_widget()

    def get_current_item_top_item(self):
        current_item = self.tree_wdg.currentItem()
        is_top_item = bool(not current_item.parent())
        if is_top_item:
            top_item = current_item
        else:
            top_item = current_item.parent()
        return top_item

    def process_target_pose_weight(self, value, blendpose_key, blend_target_key):
        if not blend_target_key:
            return
        self.blendpose_manager.update_target_pose_value(value, blendpose_key, blend_target_key)

    def initialize_slider_range(self, blendpose_key, blend_target_attr, slider):
        pose_range = self.blendpose_manager.initialize_slider_range(blendpose_key, blend_target_attr)
        slider.setMinimum(pose_range[0] * self.SLIDER_RANGE_MULT)
        slider.setMaximum(pose_range[1] * self.SLIDER_RANGE_MULT)

    def initialize_spinbox_slider(self, spinbox, slider, blendpose_key, target_pose_key):
        VALUE_TO_SLIDER_MULT = 10000
        self.initialize_slider_range(blendpose_key, target_pose_key, slider)
        current_blend_target_value = self.blendpose_manager.get_target_shape_current_value(
            blendpose_key, target_pose_key)
        spinbox.setValue(current_blend_target_value)
        slider.setValue(current_blend_target_value * VALUE_TO_SLIDER_MULT)

        current_max = slider.maximum() * 0.0001
        current_min = slider.minimum() * 0.0001
        if current_blend_target_value > current_max:
            slider.setMaximum(current_blend_target_value * self.SLIDER_RANGE_MULT * 2)
        if current_blend_target_value < current_min:
            slider.setMinimum(current_blend_target_value * self.SLIDER_RANGE_MULT * 2)

    def add_weight_slider(self, tree_item, blendpose, target_pose_key, processing_function, spinbox_range_mult=1):
        SPINBOX_DECIMAL_PLACES = 3
        SPINBOX_FIELD_WIDTH = 60
        SPINBOX_STEP = 0.001
        SPINBOX_TO_SLIDER_MULT = 0.0001
        SLIDER_TO_SPINBOX_MULT = 10000

        def resize_slider_from_target_pose(target_pose):
            slider.setMinimum(target_pose.slider_range[0] * self.SLIDER_RANGE_MULT)
            slider.setMaximum(target_pose.slider_range[1] * self.SLIDER_RANGE_MULT)

        spinbox = QtWidgets.QDoubleSpinBox()
        spinbox.setKeyboardTracking(False)
        spinbox.setFixedWidth(SPINBOX_FIELD_WIDTH)
        spinbox.setRange(-1 * spinbox_range_mult, 1 * spinbox_range_mult)
        spinbox.setSingleStep(SPINBOX_STEP)
        spinbox.setDecimals(SPINBOX_DECIMAL_PLACES)
        spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        target_pose = blendpose.target_poses[target_pose_key]
        resize_slider_from_target_pose(target_pose)
        slider.setValue(target_pose.current_weight_value * SLIDER_TO_SPINBOX_MULT)
        spinbox.setValue(target_pose.current_weight_value)

        slider_layout = QtWidgets.QHBoxLayout()
        slider_layout.addWidget(spinbox)
        slider_layout.addWidget(slider)
        wdg = QtWidgets.QWidget()
        wdg.setLayout(slider_layout)
        self.tree_wdg.setItemWidget(tree_item, 1, wdg)

        def update_target_pose(float_):
            self.blendpose_manager.update_target_pose_value(float_, blendpose.name, target_pose_key)
            target_pose = self.blendpose_manager.get_target_pose(target_pose_key, blendpose.name)
            resize_slider_from_target_pose(target_pose)

        def apply_slider_to_spinbox(float_):
            update_target_pose(float_ * SPINBOX_TO_SLIDER_MULT)
            converted_float = float_ * SPINBOX_TO_SLIDER_MULT

            spinbox.valueChanged.disconnect(apply_spinbox_to_slider)
            spinbox.setValue(converted_float)
            spinbox.valueChanged.connect(apply_spinbox_to_slider)

            processing_function(converted_float, blendpose.name, target_pose_key)

        def apply_spinbox_to_slider(float_):
            update_target_pose(float_)
            converted_float = float_ * SLIDER_TO_SPINBOX_MULT

            slider.valueChanged.disconnect(apply_slider_to_spinbox)
            slider.setValue(converted_float)
            slider.valueChanged.connect(apply_slider_to_spinbox)

            processing_function(float_, blendpose.name, target_pose_key)

        spinbox.valueChanged.connect(apply_spinbox_to_slider)
        slider.valueChanged.connect(apply_slider_to_spinbox)


    def add_commit_button(self, blendpose_key, tree_item):
        commit_button = QtWidgets.QPushButton('Commit')
        self.tree_wdg.setItemWidget(tree_item, 2, commit_button)

        def new_anim_key_from_transforms():
            self.blendpose_manager.new_anim_key_from_transforms(blendpose_key, tree_item.text(0))

        commit_button.clicked.connect(new_anim_key_from_transforms)


    def refresh_tree_widget(self):
        self.blendpose_manager = BlendposeManager.populate_manager_from_scene()
        self.tree_wdg.clear()
        for pose_name in self.blendpose_manager.blendpose_order:
            node_name = self.blendpose_manager.get_hook_node(pose_name).nodeName()
            self.add_blendpose_to_tree(node_name, pose_name)


    def get_tree_item_count(self, top_items_only=False):
        count = 0
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_wdg)
        while iterator.value():
            if not top_items_only:
                count += 1
            else:
                if bool(not iterator.value().parent()):
                    count += 1
            iterator += 1
        return count


    def add_blendpose_to_tree(self, node_name, blendpose_key):
        blendpose = self.blendpose_manager.blendposes[blendpose_key]
        item = self.create_item(node_name)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.add_tree_children(item, blendpose)
        self.tree_wdg.addTopLevelItem(item)
        item.setExpanded(blendpose.isExpanded)
        self.set_script_job_enabled(blendpose, item)


    def set_script_job_enabled(self, blendpose, item):
        return
        func = partial(self.update_blendpose_name_from_scene, item, blendpose)
        script_job_id = pm.scriptJob(nodeNameChanged=[blendpose.hook_node.nodeName(), func], protected=1,
                                     killWithScene=1)
        self.script_job_ids['node name changed'] = script_job_id


    def add_tree_children(self, item, blendpose):
        if not blendpose.target_poses:
            return None
        for target_key in blendpose.target_pose_order:
            self.add_child_to_tree_item(blendpose, blendpose.target_poses[target_key], item)


    def add_child_to_tree_item(self, blendpose, target_pose, item):
        child_item = self.create_item(target_pose.name)
        child_item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        item.addChild(child_item)
        self.add_weight_slider(child_item, blendpose, target_pose.name, self.process_target_pose_weight,
                               self.SLIDER_RANGE_MULT)
        self.add_commit_button(blendpose.name, child_item)

    def get_hook_node_from_name(self, name):
        hook_nodes = self.get_hook_nodes_in_scene()
        if name not in hook_nodes:
            return False
        scene_node = name
        return scene_node

    def create_item(self, name):
        item = QtWidgets.QTreeWidgetItem([name])
        item.setData(0, self.VALUE_ROLE, name)
        return item

    def edit_item(self, item, column):
        if self.is_top_level_item(item):
            self.edit_top_level_item(item, column)
        else:
            self.edit_child_item(item, column)
        self.refresh_tree_widget()

    def edit_child_item(self, item, column):
        top_level_item = item.parent()
        top_level_item_name = top_level_item.data(column, self.VALUE_ROLE)
        old_item_name = item.data(column, self.VALUE_ROLE)
        new_item_name = self.format_name(item.text(column))
        actual_new_name = self.blendpose_manager.rename_target_pose(
            old_item_name, new_item_name, top_level_item_name)
        self.set_item_changed_connection_enabled(False)
        item.setData(0, self.VALUE_ROLE, actual_new_name)
        self.set_item_changed_connection_enabled(True)

    def edit_top_level_item(self, item, column):
        old_item_name = item.data(column, self.VALUE_ROLE)
        new_item_name = actual_new_name = self.format_name(item.text(column))
        actual_new_name = self.blendpose_manager.rename_blendpose(actual_new_name, old_item_name)
        self.set_item_changed_connection_enabled(False)
        if actual_new_name != new_item_name:
            self.set_item_text(item, actual_new_name)
        item.setData(0, self.VALUE_ROLE, actual_new_name)
        self.set_item_changed_connection_enabled(True)

    def set_item_changed_connection_enabled(self, enabled):
        if enabled:
            self.tree_wdg.itemChanged.connect(self.edit_item)
        else:
            self.tree_wdg.itemChanged.disconnect(self.edit_item)

    def kill_all_script_jobs(self):
        entries_to_remove = []
        for key, id_ in self.script_job_ids.items():
            pm.scriptJob(kill=id_, force=1)
            entries_to_remove.append(key)
        for key in entries_to_remove:
            del self.script_job_ids[key]

    def closeEvent(self, e):
        if isinstance(self, BlendposeEditor):
            super(BlendposeEditor, self).closeEvent(e)
            self.kill_all_script_jobs()

    def show_context_menu(self, point):
        if self.is_top_level_item(self.tree_wdg.currentItem()):
            context_menu = self.build_blendpose_context_menu()
        else:
            context_menu = self.build_target_pose_context_menu()
        context_menu.exec_(self.mapToGlobal(point))

    def build_blendpose_context_menu(self):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.create_target_pose_action)
        context_menu.addSeparator()
        context_menu.addAction(self.add_selected_objs_action)
        context_menu.addAction(self.remove_selected_objs_action)
        context_menu.addAction(self.select_target_objs_action)
        context_menu.addSeparator()
        context_menu.addAction(self.select_hook_node_action)
        context_menu.addSeparator()
        context_menu.addAction(self.delete_blendpose_action)
        return context_menu

    def build_target_pose_context_menu(self):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.duplicate_target_pose_action)
        context_menu.addSeparator()
        context_menu.addAction(self.mirror_target_pose_action)
        context_menu.addAction(self.flip_target_pose_action)
        context_menu.addSeparator()
        context_menu.addAction(self.delete_target_pose_action)
        return context_menu

    def commit_transforms_to_pose(self):
        blendpose_name = self.get_current_item_top_item().text(0)
        self.blendpose_manager.new_anim_key_transforms(blendpose_name, 'TestA')

    # QT needs these functions initialized here, so it can override them in the UI.
    def apply_slider_to_spinbox(self):
        pass

    def apply_spinbox_to_slider(self):
        pass

    @staticmethod
    def is_top_level_item(item):
        return bool(not item.parent())

    @staticmethod
    def update_blendpose_name_from_scene(item, blendpose):
        item.setText(0, blendpose.hook_node.nodeName())

    @staticmethod
    def get_hook_nodes_in_scene():
        blendpose_identifier = 'IsBlendposeNode'
        all_nodes = mc.ls(dependencyNodes=1)
        hook_nodes = []
        for node in all_nodes:
            if mc.attributeQuery(blendpose_identifier, node=node, exists=1):
                hook_nodes.append(node)
        return hook_nodes

    @staticmethod
    def format_name(name):
        for char in [' ', '*', '-']:
            name = name.replace(char, '_')
        return name


if __name__ == '__main__':

    try:
        blendpose_editor.kill_all_script_jobs() # pylint: disable=E0601
        blendpose_editor.close()  # pylint: disable=E0601
        blendpose_editor.deleteLater()  # pylint: disable=E0601
    except Exception:
        pass

    blendpose_editor = BlendposeEditor()
    blendpose_editor.show()
