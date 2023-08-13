# python modules
import os
import random

#if not os.environ.get('PROJECT_CODE'):
#    raise Exception('PROJECT_CODE not set')
import time
import copy
import json
import logging
import subprocess
import functools
import traceback
import datetime

# qt modules
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# iRig modules
import Snowman3.rigger.rig_api.parts as ptls
#import Snowman3.rigger.rig_api.general as pgn
import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_api.part_hierarchy as phi
import Snowman3.utilities.version as ivn
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.system_signals as sig
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut  # this has to be before object_versions in case objects need paths
#import Snowman3.rigger.rig_factory.utilities.shard_utilities as sht
#import Snowman3.rigger.rigging_widgets.launcher.utilities.jobs as jbs
#import Snowman3.rigger.rig_factory.build.tasks.jobs.face_tasks as ftsk
import Snowman3.rigger.rig_factory.utilities.geometry_utilities as gtl
#import Snowman3.rigger.rig_factory.build.tasks.jobs.guide_tasks as gtsk
import Snowman3.rigger.rig_factory.build.tasks.jobs.toggle_tasks as tglt
#import Snowman3.rigger.rig_factory.build.tasks.jobs.low_rig_tasks as lrt
#import Snowman3.rigger.rig_factory.build.tasks.jobs.realtime_tasks as rtt
import Snowman3.rigger.rig_factory.build.tasks.jobs.save_tasks as savtsks
#import Snowman3.rigger.rig_factory.build.tasks.jobs.publish_tasks as ptsk
#import Snowman3.rigger.rig_factory.build.tasks.jobs.test_parts_tasks as tpt
import Snowman3.rigger.rig_factory.utilities.space_switcher_utilities as spu
#import Snowman3.rigger.rig_factory.build.tasks.jobs.finalize_tasks as fintsk
#import Snowman3.rigger.rig_factory.build.tasks.jobs.inversion_rig_tasks as ivt
#import rigging_widgets.launcher.utilities.jobs_utilities as jbsu
#import Snowman3.rigger.rig_factory.build.tasks.jobs.import_rig_data_tasks as irdt
import Snowman3.rigger.rig_factory.build.tasks.jobs.export_rig_data_tasks as erdt
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.initializers as bti
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.task_utilities as tut
#import Snowman3.rigger.rig_factory.build.tasks.task_utilities.legacy_blueprint_utilities as lpu
#from rigging_widgets.launcher.widgets.jobs_widget import JobsWidget
#from rigging_widgets.rig_builder.widgets.notification_label_widget import NotificationLauncher
#from rig_factory.objects.rig_objects.guide_handle import GuideHandle
#from rigging_widgets.sdk_builder.widgets.sdk_widget import SDKWidget
#from rigging_widgets.rig_builder.widgets.fail_widget import FailWidget
#from rigging_widgets.rig_builder.views.part_owner_view import PartOwnerView
#from rigging_widgets.face_builder.widgets.face_widget import FaceWidget
#from rigging_widgets.rig_builder.widgets.toggle_button import ToggleButton
#from rigging_widgets.rig_builder.widgets.new_part_widget import NewPartWidget
#from rigging_widgets.blueprint_builder.blueprint_widget import BlueprintWidget
#from rigging_widgets.rig_builder.widgets.progress_widget import ProgressWidget
#from rigging_widgets.rig_builder.widgets.geometry_widget import GeometryWidget
#from rigging_widgets.rig_builder.widgets.handle_shapes_widget import HandleShapesWidget
#from rigging_widgets.rig_builder.widgets.products_widget import ProductsWidget
#from rigging_widgets.rig_builder.widgets.finalized_widget import FinalizedWidget
#from rigging_widgets.rig_builder.widgets.hierarchy_widget import HierarchyWidget
#from rigging_widgets.rig_builder.widgets.new_container_view import NewContainerView
#from rigging_widgets.rig_builder.widgets.custom_plug_widget import CustomPlugWidget
#from rigging_widgets.rig_builder.widgets.save_widget import SaveWidget, PublishWidget
#from rigging_widgets.build_task_executor.widgets.build_task_widget import BuildTaskWidget
#from rigging_widgets.rig_builder.widgets.finalize_script_widget import FinalizeScriptWidget
#from rigging_widgets.rig_builder.widgets.custom_constraint_widget import CustomConstraintWidget
#from rigging_widgets.rig_builder.widgets.deformation_layers_widget import DeformationLayersWidget
#import rigging_widgets.rig_builder.utilities.editor_utilities as edtu
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as bpu

#if not os.environ.get('PROJECT_CODE'):
#    raise Exception('PROJECT_CODE not set')
DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


class RigWidget(QFrame):
    busy = False

    def set_controller(self, controller):
        if self.controller:
            sig.root_signals['start_change'].disconnect(self.set_widget_controllers_to_none)
            sig.controller_signals['reset'].disconnect(self.reset_build_tasks)
        self.controller = controller
        if self.controller:
            sig.root_signals['start_change'].connect(self.set_widget_controllers_to_none)
            sig.controller_signals['reset'].connect(self.reset_build_tasks)
        self.reload_widget_state()
        self.update_menubar()

    def __init__(self, *args, **kwargs):
        super(RigWidget, self).__init__(*args, **kwargs)
        self.saved_selection = []
        self.actions_menu = None
        self.dialog = None
        self._stop_build = False
        self._build_tasks = None
        self._build_index = 0
        self._auto_build = True
        self._executing = False
        self._build_started = None
        self._check_for_new_products = True
        self._build_callback = None
        self.build_pool = QThreadPool()
        self.build_pool.setMaxThreadCount(5)
        self.controller = None
        self.magnet_icon = QIcon('%s/magnet.png' % env.images_directory)
        self.setWindowTitle(self.__class__.__name__)
        self.vertical_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.menu_layout = QHBoxLayout()
        self.info_layout = QHBoxLayout()
        self.path_label = QLabel(self)
        self.saved_label = QLabel(self)
        self.main_widget = MainWidget(self)
        self.new_part_widget = NewPartWidget(self)
        self.handle_shapes_widget = HandleShapesWidget(self)
        self.no_controler_view = NoControllerView(self)
        self.progress_widget = ProgressWidget(self)
        self.fail_widget = FailWidget(self)
        self.finalized_widget = FinalizedWidget(self)
        self.new_container_view = NewContainerView(self)
        self.geometry_widget = GeometryWidget(self)
        self.build_task_widget = BuildTaskWidget(self)
        self.products_widget = ProductsWidget(self)
        self.build_widget = QTreeView(self)
        self.face_widget = FaceWidget(self)
        self.geometry_layers_widget = DeformationLayersWidget(self)
        self.custom_plug_widget = CustomPlugWidget(self)
        self.custom_constraint_widget = CustomConstraintWidget(self)
        self.finalize_script_widget = FinalizeScriptWidget(self)
        self.hierarchy_widget = HierarchyWidget(self)
        self.blueprint_widget = BlueprintWidget(self)
        self.sdk_widget = SDKWidget(self)
        self.jobs_widget = JobsWidget(self)
        self.menu_bar = QMenuBar(self)
        self.back_button = QPushButton('Rig', self)
        self.back_button.setIcon(QIcon('%s/back_arrow.png' % env.images_directory))
        self.back_button.setVisible(False)
        path_font = QFont('arial', 12, True)
        self.path_label.setFont(path_font)
        self.path_label.setWordWrap(True)

        self.menu_layout.addWidget(self.menu_bar)
        self.menu_layout.addWidget(self.back_button)
        self.menu_layout.addStretch()

        self.info_layout.addWidget(self.path_label)
        self.info_layout.addStretch()
        self.info_layout.addWidget(self.saved_label)

        # Create a label to indicate the asset the session is launched from
        irig_version = ivn.get_irig_version()
        if not irig_version:
            irig_version = 'DEV'
        entity_label = QLabel('%s %s' % (irig_version, os.environ['ENTITY_NAME']))
        entity_label.setWordWrap(True)
        entity_label.setAlignment(Qt.AlignRight)
        self.menu_layout.addWidget(entity_label)
        self.vertical_layout.addLayout(self.menu_layout)
        self.vertical_layout.addLayout(self.info_layout)
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.new_part_widget)
        self.stacked_layout.addWidget(self.handle_shapes_widget)
        self.stacked_layout.addWidget(self.no_controler_view)
        self.stacked_layout.addWidget(self.progress_widget)
        self.stacked_layout.addWidget(self.fail_widget)
        self.stacked_layout.addWidget(self.new_container_view)
        self.stacked_layout.addWidget(self.geometry_widget)
        self.stacked_layout.addWidget(self.sdk_widget)
        self.stacked_layout.addWidget(self.custom_plug_widget)
        self.stacked_layout.addWidget(QWidget(self))  # this used to be post script widget
        self.stacked_layout.addWidget(self.finalize_script_widget)
        self.stacked_layout.addWidget(self.custom_constraint_widget)
        self.stacked_layout.addWidget(self.hierarchy_widget)
        self.stacked_layout.addWidget(self.blueprint_widget)
        self.stacked_layout.addWidget(self.finalized_widget)
        self.stacked_layout.addWidget(self.jobs_widget)
        self.stacked_layout.addWidget(self.build_task_widget)
        self.stacked_layout.addWidget(self.build_widget)
        self.stacked_layout.addWidget(self.face_widget)
        self.stacked_layout.addWidget(self.products_widget)
        self.stacked_layout.addWidget(self.geometry_layers_widget)
        self.back_button.released.connect(self.reload_widget_state)
        self.stacked_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.new_part_widget.done_signal.connect(self.reload_widget_state)
        self.new_part_widget.create_part_signal.connect(self.create_part)
        self.main_widget.part_view.create_part_signal.connect(self.show_new_part_widget)
        self.main_widget.part_view.critical_error_signal.connect(self.set_failed_state)
        self.face_widget.sculpt_widget.critical_error_signal.connect(self.set_failed_state)
        self.main_widget.create_container_signal.connect(self.create_body)
        self.main_widget.toggle_button.toggled.connect(self.toggle_rig_state_slot)
        self.geometry_widget.finished_signal.connect(self.reload_widget_state)
        self.sdk_widget.finished_signal.connect(self.reload_widget_state)
        self.custom_plug_widget.done_signal.connect(self.reload_widget_state)
        self.finalize_script_widget.done_signal.connect(self.reload_widget_state)
        self.custom_constraint_widget.done_signal.connect(self.reload_widget_state)
        self.new_container_view.blueprint_signal.connect(self.check_then_build_blueprint)
        self.new_container_view.rig_signal.connect(self.check_then_build_blueprint_path)
        self.new_container_view.rig_and_face_signal.connect(
            functools.partial(
                self.check_then_build_blueprint_path,
                build_face=True
            )
        )
        self.new_container_view.guide_signal.connect(self.build_guide_blueprint_path)
        self.build_task_widget.stop_button.released.connect(self.stop_build)
        self.build_task_widget.resume_button.released.connect(self.resume_build)
        sig.gui_signals['saved_time_signal'].connect(self.set_saved_time)
        self.build_task_widget.next_button.released.connect(self.build_task_widget.show_busy_wdget)
        self.build_task_widget.next_button.released.connect(self.execute_next)
        self.build_task_widget.next_button.released.connect(self.frame_current_task)
        self.build_task_widget.next_button.released.connect(self.build_task_widget.close_busy_widget)

        self.build_task_widget.resume_button.setVisible(False)
        self.build_task_widget.next_button.setVisible(False)

        self.blueprint_widget.data_signal.connect(self.rebuild)
        self.finalized_widget.toggle_rig_state_signal.connect(self.toggle_rig_state_slot)
        sig.build_directory_changed.connect(self.set_build_directory)
        self.fail_widget.dont_care_button.released.connect(self.undo_failed_state)
        self.fail_widget.new_scene_button.released.connect(self.new_scene)
        self.build_task_widget._frame = False
        self.build_task_widget._frame_warnings = False
        self.show_new_container_widget()
        self.set_build_directory(env.local_build_directory)
        self.notification_launcher = NotificationLauncher(self)
        sig.gui_signals['info_notification'].connect(self.notification_launcher.info_notification)
        sig.gui_signals['success_notification'].connect(self.notification_launcher.success_notification)
        sig.gui_signals['warning_notification'].connect(self.notification_launcher.warning_notification)
        sig.gui_signals['error_notification'].connect(self.notification_launcher.error_notification)
        sig.gui_signals['party_notification'].connect(self.notification_launcher.party_notification)

    def set_build_checks(self, value):
        self._check_for_new_products = value

    def new_scene(self):
        if self.raise_question('Are you sure you want to discard changes and create a new scene?'):
            self.controller.scene.file(new=True, force=True)

    def set_failed_state(self):
        self.controller.failed_state = True
        self.reload_widget_state()

    def undo_failed_state(self):
        self.controller.failed_state = False
        self.reload_widget_state()

    def new_scene_rebuild(self, *args):
        if self.raise_question('Are you sure you want to clear the maya scene and rebuild the rig from memory?'):
            blueprint = bpu.get_blueprint()
            self.controller.scene.file(new=True, force=True)
            self.rebuild(blueprint)

    def set_build_callback(self, callback):
        if self._build_callback and callback is not None:
            raise Exception('There is already a build callback: %s' % self._build_callback)
        elif callback is None or callable(callback):
            self._build_callback = callback
        else:
            raise Exception('%s is not a valid callback' % callback)

    def show_log(self):
        log_path = self.controller.log_path
        if os.path.exists(log_path):
            notepad_path = 'C:/Program Files/Notepad++/notepad++.exe'
            if os.path.exists(notepad_path):
                if os.path.exists(notepad_path):
                    subprocess.Popen(
                        '"%s" -nosession -multiInst -alwaysOnTop %s' % (notepad_path, log_path))
                else:
                    self.display_message('Notepad++ app not found. Unable to view log.')

    def set_auto_build(self, value):
        self._auto_build = value

    def resume_build(self):
        self._stop_build = False
        self.build()

    def stop_build(self):
        self._stop_build = True

    def update_toggle_button(self, *args, **kwargs):
        if self.controller and isinstance(self.controller.root, obs.Container):
            self.main_widget.toggle_button.set_value(True)
        else:
            self.main_widget.toggle_button.set_value(False)

    def rebuild(self, blueprint):
        controller = self.controller
        if not controller:
            raise Exception('No Controller found.')
        if controller.root:
            if self.raise_question('There seems to be a rig currently loaded. Would you like to delete it ?'):
                ptls.delete_container()
            else:
                return
        controller.reset()
        self.set_root_task(None)
        QApplication.processEvents()
        self.check_then_build_blueprint(blueprint)

    def add_driven_plugs(self, plug_names):
        pass

    def set_widget_controllers_to_none(self, *args):
        self.back_button.setVisible(True)
        self.menu_bar.setVisible(False)
        if self.controller:
            self.controller.disable_ordered_vertex_selection()
        self.hierarchy_widget.set_controller(None)
        self.geometry_widget.set_controller(None)
        self.sdk_widget.set_controller(None)
        self.custom_plug_widget.set_controller(None)
        self.custom_constraint_widget.set_controller(None)
        self.finalize_script_widget.set_controller(None)
        self.finalize_script_widget.set_controller(None)
        self.main_widget.set_controller(None)
        self.new_part_widget.set_controller(None)
        self.finalized_widget.set_controller(None)
        self.blueprint_widget.set_controller(None)
        self.face_widget.set_controller(None)
        self.geometry_layers_widget.set_controller(None)
        QApplication.processEvents()

    def show_jobs_widget(self):
        self.set_widget_controllers_to_none()
        self.back_button.setVisible(True)
        self.stacked_layout.setCurrentIndex(16)

    def reload_widget_state(self, *args):
        if self.controller.failed_state:
            self.show_fail_widget()
        elif self.controller.root:
            if isinstance(self.controller.root, obs.Container) and self.controller.root.has_been_finalized:
                self.show_finalized_widget()
            else:
                self.show_parts_view()
        else:
            self.show_new_container_widget()
        self.update_menubar()
        self.back_button.setVisible(False)

    def show_parts_view(self):
        self.set_widget_controllers_to_none()
        if isinstance(self.controller.root, obs.Container) and self.controller.root.has_been_finalized:
            self.show_finalized_widget()
        self.main_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(0)
        self.update_toggle_button()

    def show_new_container_widget(self):
        self.set_widget_controllers_to_none()
        self.new_container_view.set_build_directory(env.local_build_directory)
        self.stacked_layout.setCurrentIndex(6)
        self.back_button.setVisible(False)

    def show_face_widget(self):
        self.set_widget_controllers_to_none()
        self.menu_bar.setVisible(False)
        if self.controller.face_network and self.controller.face_network.has_been_finalized:
            self.show_finalized_widget()
        else:
            self.stacked_layout.setCurrentIndex(19)
            self.face_widget.set_controller(self.controller)

    def show_products_widget(self):
        self.set_widget_controllers_to_none()
        self.menu_bar.setVisible(False)
        self.stacked_layout.setCurrentIndex(20)

    def show_task_widget(self):
        self.set_widget_controllers_to_none()
        self.menu_bar.setVisible(False)
        self.stacked_layout.setCurrentIndex(17)

    def show_finalized_widget(self):
        self.set_widget_controllers_to_none()
        self.finalized_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(15)

    def show_blueprint_widget(self):
        self.set_widget_controllers_to_none()
        self.blueprint_widget.set_controller(self.controller)
        if self.controller.root:
            blueprint = bpu.get_blueprint()
            self.blueprint_widget.blueprint_view.load_blueprint(blueprint)
        self.blueprint_widget.rebuild_button.setVisible(True)
        self.stacked_layout.setCurrentIndex(14)

    def show_hierarchy_widget(self):
        self.set_widget_controllers_to_none()
        self.hierarchy_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(13)

    def show_geometry_widget(self):
        self.set_widget_controllers_to_none()
        self.stacked_layout.setCurrentIndex(7)
        self.geometry_widget.set_controller(self.controller)
        self.geometry_widget.stacked_layout.setCurrentIndex(0)
        self.geometry_widget.load_model()

    def show_deformation_layers_widget(self):
        self.set_widget_controllers_to_none()
        self.stacked_layout.setCurrentIndex(21)
        self.geometry_layers_widget.set_controller(self.controller)
        self.geometry_layers_widget.load_model()

    def show_sdk_widget(self):
        self.set_widget_controllers_to_none()
        self.sdk_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(8)
        self.sdk_widget.load_model()

    def show_custom_plug_widget_widget(self):
        self.set_widget_controllers_to_none()
        self.custom_plug_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(9)
        self.custom_plug_widget.load_model()

    def show_custom_constraint_widget(self):
        self.set_widget_controllers_to_none()
        self.custom_constraint_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(12)
        self.custom_constraint_widget.load_model()

    def show_finalize_script_widget(self):
        self.set_widget_controllers_to_none()
        self.finalize_script_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(11)
        self.finalize_script_widget.set_controller(self.controller)
        self.finalize_script_widget.load_model()

    def update_menubar(self):
        self.menu_bar.setVisible(True)
        self.build_actions()

    def update_directory_label(self, build_directory):
        self.path_label.setText('')
        if build_directory and build_directory != fut.get_user_build_directory():
            base_directory = '%s/assets/type/%s/%s' % (
                fut.get_base_directory(),
                os.environ['TT_ASSTYPE'],
                os.environ['ENTITY_NAME']
            )
            if build_directory.startswith(base_directory):
                relative_path = os.path.relpath(
                    build_directory,
                    base_directory
                ).replace('\\', '/').replace('..', '')
                self.path_label.setText(relative_path)
            elif build_directory.startswith(base_directory):
                relative_path = os.path.relpath(
                    build_directory,
                    base_directory
                ).replace('\\', '/').replace('..', '')
                self.path_label.setText(relative_path)
            else:
                self.path_label.setText(build_directory.split('/')[-1])

    def update_progress(self, *args, **kwargs):
        message = kwargs.get('message', None)
        value = kwargs.get('value', None)
        maximum = kwargs.get('maximum', None)
        self.stacked_layout.setCurrentIndex(4)
        if message:
            self.progress_widget.label.setText(message.replace('_', ' '))
        if value is not None:
            self.progress_widget.progress_bar.setValue(value)
        if maximum is not None:
            self.progress_widget.progress_bar.setMaximum(maximum)
        QApplication.processEvents()

    def create_part(self, part_owner_name, klass, part_blueprint):
        self.setEnabled(False)
        if not self.controller.root:
            self.raise_warning('Rig Not found')
            return
        if part_owner_name not in self.controller.named_objects:
            self.raise_warning('Owner not found: %s' % part_owner_name)
            return
        part_owner = self.controller.named_objects[part_owner_name]
        try:
            start = time.time()
            if part_blueprint['root_name'] == '':
                part_blueprint['root_name'] = None
                if not isinstance(obs.__dict__[part_blueprint['object_type']], (obs.Main, obs.MainGuide)):
                    if not self.raise_question(
                            'root_name=None for part: %s do you want continue?' % part_blueprint['root_name']
                    ):
                        return

            ptls.create_part(
                part_owner,
                klass,
                **part_blueprint
            )
            self.setEnabled(True)
            logging.getLogger('rig_build').info('Created part in %s seconds' % (time.time() - start))
        except Exception as e:
            self.show_fail_widget()
            logging.getLogger('rig_build').error(traceback.format_exc())
            self.raise_warning('Critical Error while creating part. See log for details...')
            self.setEnabled(True)

    def show_fail_widget(self, *args, **kwargs):
        self.stacked_layout.setCurrentIndex(5)
        phrases = [
            '"YOLO!"',
            '"Don\'t Care!"',
            '"Don\'t tell me what to do"',
            '"What\'s the worst that could happen?"'
        ]
        self.fail_widget.dont_care_button.setText(phrases[random.randint(0, len(phrases) - 1)])

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            str(exception.message)
        )
        self.setEnabled(True)
        traceback.print_exc()
        raise exception

    def raise_question(self, question, title='Question'):
        response = QMessageBox.question(
            self,
            title,
            question,
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No
        )
        return response == QMessageBox.Yes

    def raise_warning(self, message, window_title=None):
        if window_title is None:
            window_title = 'Warning'
        logging.getLogger('rig_build').warning(message)
        message_box = QMessageBox(self)
        message_box.setWindowTitle(window_title)
        message_box.setText(message)
        self.center_dialog(message_box)
        message_box.exec_()

    def center_dialog(self, dialog):
        center = self.geometry().center()
        dialog.move(
            QPoint(
                center.x() - dialog.width(),
                (center.y() - self.geometry().height() * 0.25) - dialog.height()
            )
        )
        grid_layout = dialog.layout()
        qt_msgboxex_icon_label = dialog.findChild(QLabel, "qt_msgboxex_icon_label")
        qt_msgboxex_icon_label.deleteLater()
        qt_msgbox_label = dialog.findChild(QLabel, "qt_msgbox_label")
        qt_msgbox_label.setAlignment(Qt.AlignCenter)
        grid_layout.removeWidget(qt_msgbox_label)
        qt_msgbox_buttonbox = dialog.findChild(QDialogButtonBox, "qt_msgbox_buttonbox")
        grid_layout.removeWidget(qt_msgbox_buttonbox)
        grid_layout.addWidget(qt_msgbox_label, 0, 0, alignment=Qt.AlignCenter)
        grid_layout.addWidget(qt_msgbox_buttonbox, 1, 0, alignment=Qt.AlignCenter)

    def raise_exception(self, exception):
        self.show_fail_widget()
        traceback.print_exc()
        logger = logging.getLogger('rig_build')
        logger.error(traceback.format_exc())
        message_box = QMessageBox(self)
        message_box.setWindowTitle('Error')
        message_box.setText(str(exception.message))
        message_box.exec_()
        self.setEnabled(True)

    def create_body(self, body_type):
        body = self.controller.create_object(body_type, root_name='root')
        self.controller.set_root(body)
        self.controller.dg_dirty()

    def show_new_part_widget(self, klass, part_owner_name):
        if part_owner_name is None:
            if not self.controller.root:
                self.raise_warning('Rig not found')
                return
            part_owner = self.controller.root
        elif part_owner_name in self.controller.named_objects:
            part_owner = self.controller.named_objects[part_owner_name]
        else:
            self.raise_warning('owner not found: %s' % part_owner_name)
            return
        if part_owner.layer != self.controller.current_layer:
            self.raise_warning('You cant create a part under a parent group: %s' % part_owner.name)
            return
        self.set_widget_controllers_to_none()
        self.controller.enable_ordered_vertex_selection()
        self.new_part_widget.set_controller(self.controller)
        self.new_part_widget.set_klass(klass)
        self.new_part_widget.owner_name = part_owner.name
        self.stacked_layout.setCurrentIndex(1)

    def build_actions(self):
        self.menu_bar.clear()
        if self.controller.failed_state:
            return
        root = self.controller.root
        face_network = self.controller.face_network
        file_menu = self.menu_bar.addMenu('File')
        edit_menu = self.menu_bar.addMenu('Edit')
        view_menu = self.menu_bar.addMenu('View')

        # file_menu.addAction('Publish Callback', self.publish_callback)
        settings_menu = self.menu_bar.addMenu('Settings')

        if root:
            file_menu.addAction('New + Rebuild', self.new_scene_rebuild)
            file_menu.addSeparator()
            import_menu = file_menu.addMenu('Import')
            export_menu = file_menu.addMenu('Export')
        view_menu.addAction('Part View', self.reload_widget_state)
        view_menu.addAction('Face View', self.show_face_widget)
        view_menu.addAction('Build View', self.show_task_widget)
        view_menu.addAction('Blueprint View', self.show_blueprint_widget)
        view_menu.addSeparator()
        view_menu.addAction('Hierarchy View', self.show_hierarchy_widget)
        view_menu.addAction('Geometry View', self.show_geometry_widget)
        # view_menu.addAction('Finalize-Script View', self.show_finalize_script_widget)
        view_menu.addAction('Products View', self.activate_products)

        if isinstance(root, obs.Container):
            view_menu.addAction('Custom Plugs View', self.show_custom_plug_widget_widget)
            view_menu.addAction('Custom Constraints View', self.show_custom_constraint_widget)
            view_menu.addAction('Custom SDK View', self.show_sdk_widget)

        view_menu.addSeparator()
        view_menu.addAction('Jobs View', self.show_jobs_widget)
        view_menu.addAction('Show Log', self.show_log)
        view_menu.addSeparator()
        view_menu.addAction('Deformation Layers View', self.show_deformation_layers_widget)

        if root is None:
            file_menu.addAction(
                'Import Rig Blueprint',
                self.import_blueprint
            )
            file_menu.addAction('Set Build Directory', self.browse_for_build_directory)
            file_menu.addAction('Reset Build Directory', self.go_home)
        elif isinstance(root, obs.ContainerGuide):
            import_menu.addAction(
                'Import Rig Blueprint (Merge)',
                self.merge_blueprint
            )
        if isinstance(root, obs.Container):
            if face_network is None:
                import_menu.addAction(
                    'Import Face Network',
                    self.import_face_blueprint
                )
            else:
                import_menu.addAction(
                    'Import Face Network (Merge)',
                    self.import_face_blueprint
                )
        file_menu.addSeparator()
        if root:
            import_menu.addSeparator()

        if root:
            file_menu.addAction('Save', self.save_work_popup)
            file_menu.addSeparator()

            parts_menu = edit_menu.addMenu('Parts')

            export_menu.addAction('Export Rig Blueprint', self.export_blueprint)
            if self.controller.face_network:
                export_menu.addAction('Export Face Network', self.export_face_blueprint)
                export_menu.addAction('Export Face Limits', self.export_face_overshoot_limits)
                import_menu.addAction('Import Face Limits', self.import_face_overshoot_limits)

            if isinstance(root, obs.ContainerGuide):
                plugin_menu = parts_menu.addMenu('Plugins')
                plugin_menu.addAction(
                    'Use Plugins',
                    functools.partial(
                        pgn.set_use_plugins,
                        self.controller,
                        True
                    )
                )
                plugin_menu.addAction(
                    'Use Vanilla Maya',
                    functools.partial(
                        pgn.set_use_plugins,
                        self.controller,
                        False
                    )
                )

            parts_menu.addAction(
                'Snap to Selected Mesh',
                functools.partial(
                    pgn.snap_selected_parts_to_selected_mesh,
                    self.controller
                )
            )

            edit_menu.addAction('Freeze Module Versions', self.freeze_module_versions)

            # Guide State Menus
            if isinstance(root, obs.ContainerGuide):
                edit_menu.addAction('Group Selected', self.group_selected_parts)

                # Import Menu
                export_menu.addSeparator()
                import_menu.addAction('Import ABC Product', self.import_abc_product)
                import_menu.addAction('Import Handle Positions', self.import_handle_positions)
                import_menu.addAction('Import Handle Vertices', self.import_handle_vertices)
                import_menu.addAction('Import Hierarchy', self.import_hierarchy)
                import_menu.addAction('Import Surface Shapes', self.import_surfaces)
                import_menu.addAction('Import Utility Geometry', self.import_utility_geometry)
                import_menu.addAction('Import Low Geometry', self.import_low_geometry)

                # Export Menu
                export_menu.addSeparator()
                export_menu.addAction('Export Handle Positions', self.export_handle_positions)
                export_menu.addAction('Export Handle Vertices', self.export_handle_vertices)
                export_menu.addAction('Export Hierarchy', self.export_hierarchy)
                export_menu.addAction('Export Surface Shapes', self.export_surfaces)
                export_menu.addAction('Export Utility Geometry', self.export_utility_geometry)

                edit_menu.addAction('Assign Closest Vertices (Selected)', self.assign_closest_vertices)
                edit_menu.addAction('Snap to Associated Vertices', self.snap_handles_to_mesh_positons)
                edit_menu.addAction('Transfer Vertices (Selected)', self.transfer_handle_vertices)
                edit_menu.addAction('Remove Vertices (Selected parts)', self.remove_vertex_association)

                mirror_menu = edit_menu.addMenu('Mirror')
                mirror_menu.addAction('Mirror All', self.mirror_all)
                mirror_menu.addAction('Mirror Handle Positions', self.mirror_handle_positions)
                mirror_menu.addAction('Mirror Handle Vertices', self.mirror_handle_vertices)
                mirror_menu.addAction('Mirror Handle Attributes', self.mirror_handle_attributes)
                mirror_menu.addAction('Mirror Slide Values', self.mirror_slide_values)
                edit_menu.addAction('Delete Geometry', self.delete_geometry)
                edit_menu.addAction('Delete Origin Geometry', self.delete_origin_geometry)
                edit_menu.addAction('Delete Utility Geometry', self.delete_utility_geometry)
                edit_menu.addAction('Delete Low Geometry', self.delete_low_geometry)
                edit_menu.addAction('Reset Hierarchy', self.reset_hierarchy)

                parts_menu.addAction(
                    'Assign closest vertices (from selected mesh)',
                    functools.partial(
                        pgn.assign_closest_vertices_to_selected_parts,
                        self.controller
                    )
                )
                parts_menu.addAction(
                    'Assign Nurbs Surface',
                    self.assign_nurbs_surface
                )

                parts_menu.addAction(
                    'Remove Nurbs Surface',
                    self.remove_nurbs_surface_assignments
                )

            # Rig State Menus
            elif isinstance(root, obs.Container):
                if not root.has_been_finalized:

                    # Export Menu (available for both External Rig Data and non-external rig data)
                    export_menu.addSeparator()
                    export_menu.addAction('Export All Handle Shapes', self.export_all_handle_shapes)
                    export_menu.addAction('Export Handle Limits', self.export_handle_limits)
                    export_menu.addAction('Export Input Transforms', self.export_input_transforms)
                    export_menu.addAction('Export Surface Shapes', self.export_surfaces)
                    export_menu.addAction('Export Utility Geometry', self.export_utility_geometry)

                    # Import Menu (available for both External Rig Data and non-external rig data)
                    import_menu.addSeparator()
                    import_menu.addAction('Import Handle Limits', self.import_handle_limits)
                    import_menu.addAction('Import Input Transforms', self.import_input_transforms)
                    import_menu.addAction('Import Surface Shapes', self.import_surfaces)

                    # If External Rig Data is Turned ON
                    if root.use_external_rig_data:
                        # Export Menu
                        export_menu.addSeparator()
                        export_menu.addAction('Export All External Rig Data', self.export_all_rig_data)
                        export_menu.addAction('Export Parts Data', self.export_parts_data)
                        export_menu.addAction('Export skin_clusters', self.export_skin_clusters)

                        # Import Menu
                        import_menu.addSeparator()
                        import_menu.addAction('Import All External Rig Data', self.import_all_rig_data)
                        import_menu.addAction('Import Parts Data', self.import_parts_data)
                        import_menu.addAction('Import skin_clusters', self.import_skin_clusters)
                        for data_key in [
                            'handle_shapes',
                            'handle_colors',
                            'handle_default_colors',
                            'deformer_stack_data',
                            'delta_mush',
                            'shard_skin_cluster_data',
                            'wrap',
                            'cvwrap',
                            'space_switchers',
                            'sdks',
                            'custom_plug_data',
                            'custom_constraint_data',
                            'origin_bs_weights'
                        ]:
                            import_menu.addAction(
                                'Import %s' % data_key,
                                functools.partial(
                                    self.import_container_rig_data,
                                    data_key
                                )
                            )
                            export_menu.addAction(
                                'Export %s' % data_key,
                                functools.partial(
                                    self.export_container_rig_data,
                                    data_key
                                )
                            )

                    # If External Rig Data is Turned OFF
                    else:
                        # Export External Rig Data Menu
                        export_menu.addSeparator()
                        export_menu.addAction('Export Skin Clusters', self.export_skin_clusters)
                        export_menu.addAction('Export Custom SDKs\'s', self.export_custom_sdks)
                        export_menu.addAction('Export Handle Shapes', self.export_handle_shapes)
                        export_menu.addAction('Export Handle Spaces', self.export_handle_spaces)
                        export_menu.addAction('Export Shard Weights', self.export_shard_weights)

                        # Import External Rig Data Menu
                        import_menu.addSeparator()
                        import_menu.addAction('Import Skin Clusters', self.import_skin_clusters)
                        import_menu.addAction('Import Custom SDKs\'s', self.import_custom_sdks)
                        import_menu.addAction('Import Handle Shapes', self.import_handle_shapes)
                        import_menu.addAction('Import Handle Spaces', self.import_handle_spaces)
                        import_menu.addAction('Import Shard Weights', self.import_shard_weights)

                    edit_menu.addAction('Edit Handle Shapes', self.expand_handle_shapes)
                    edit_menu.addAction('Save Vertex Selection', self.save_selection)
                    edit_menu.addAction('Load Vertex Selection', self.load_selection)
                    edit_menu.addAction('Reset Spaces', self.reset_spaces)
                    file_menu.addAction('Finalize', self.finalize)
                    # edit_menu.addAction('Bake Shards', self.bake_shards)
            file_menu.addAction('Mock-Publish', self.mock_publish_rig)
            file_menu.addAction(
                'Finalize Face',
                self.finalize_face_network
            )
            file_menu.addSeparator()
            file_menu.addAction('Publish', self.publish_popup)
            edit_menu.addAction('View as json', self.view_as_json)
        if not root:
            file_menu.addSeparator()
            file_menu.addAction('Publish Realtime (From Product)', self.publish_realtime_product)
            file_menu.addAction('Create Realtime (From Current Directory)', self.create_realtime_current)
            file_menu.addAction('Create Low (From Current Directory)', self.create_low)
            file_menu.addAction('Create Anim Rig (From Current Directory)', self.create_anim_rig_current)
            file_menu.addAction('Create Auto Rig', self.create_auto_rig)
            file_menu.addAction('Publish Auto Rig', self.publish_auto_rig)

        task_action = QAction("Auto Expand Task", self, checkable=True)
        task_action.toggled.connect(self.build_task_widget.set_task_framing)
        settings_menu.addAction(task_action)
        task_action = QAction("Auto Expand Warnings", self, checkable=True)
        task_action.toggled.connect(self.build_task_widget.set_task_warning_framing)
        settings_menu.addAction(task_action)
        task_action = QAction("Check For New Products", self, checkable=True)
        task_action.setChecked(self._check_for_new_products)
        task_action.toggled.connect(self.set_build_checks)
        settings_menu.addAction(task_action)
        auto_build_action = QAction("Auto Start Build", self, checkable=True)
        auto_build_action.setChecked(self._auto_build)
        auto_build_action.toggled.connect(self.set_auto_build)
        settings_menu.addAction(auto_build_action)
        post_task_redraw_action = QAction("Post Task Re-Draw", self, checkable=True)
        post_task_redraw_action.setChecked(self.build_task_widget.post_task_redraw)
        post_task_redraw_action.toggled.connect(self.set_post_task_redraw)
        settings_menu.addAction(post_task_redraw_action)
        settings_menu.addAction('')
        if self.actions_menu:
            self.menu_bar.addMenu(self.actions_menu)
        if self.controller.face_network:
            edit_menu.addSeparator()
            edit_menu.addAction(
                'Mirror FaceNetwork',
                self.mirror_face_network
            )
            edit_menu.addSeparator()

        edit_menu.addAction('Explore build', self.explore_build)

        log_menu = settings_menu.addMenu('Log Level')

        log_menu.addAction(
            'NOTSET',
            functools.partial(
                self.set_log_level,
                logging.NOTSET
            )
        )
        log_menu.addAction(
            'DEBUG',
            functools.partial(
                self.set_log_level,
                logging.DEBUG
            )
        )
        log_menu.addAction(
            'INFO',
            functools.partial(
                self.set_log_level,
                logging.INFO
            )
        )
        log_menu.addAction(
            'WARNING',
            functools.partial(
                self.set_log_level,
                logging.WARNING
            )
        )
        log_menu.addAction(
            'ERROR',
            functools.partial(
                self.set_log_level,
                logging.ERROR
            )
        )
        log_menu.addAction(
            'CRITICAL',
            functools.partial(
                self.set_log_level,
                logging.CRITICAL
            )
        )
        settings_menu.addAction('Set Batch Thread count', self.set_batch_thread_count)

        if isinstance(root, obs.Container):
            if not root.has_been_finalized:
                edit_menu.addSeparator()
                custom_handle_shape_action = QAction("Allow Custom Handle Shapes", self, checkable=True)
                if root.custom_handles:
                    custom_handle_shape_action.setChecked(True)
                custom_handle_shape_action.toggled.connect(self.set_custom_handles)
                edit_menu.addAction(custom_handle_shape_action)

                external_action = QAction("External Rig Data", self, checkable=True)
                external_action.setChecked(root.use_external_rig_data)
                external_action.toggled.connect(self.set_external_rig_data)
                edit_menu.addAction(external_action)
                if self.controller.root.use_external_rig_data:
                    manual_action = QAction("Manual Rig Data", self, checkable=True)
                    manual_action.setChecked(root.use_manual_rig_data)
                    manual_action.toggled.connect(self.set_manual_rig_data)
                    edit_menu.addAction(manual_action)
        # edit_menu.addAction(ptls.clear_session)
        if DEBUG:
            debug_menu = self.menu_bar.addMenu('DEBUG')
            debug_menu.addAction('Build All Parts', self.build_all_parts)
            debug_menu.addAction('Build Inversion Rig', self.build_inversion_rig)

    def build_inversion_rig(self):
        self.build_task_tree(
            ivt.get_inversion_rig_tasks(
                self.get_build_root()
            )
        )

    def set_saved_time(self, save_time):
        self.saved_label.setText('Last Saved: ' + save_time)

    def group_selected_parts(self):
        if self.controller:
            if not isinstance(self.controller.root, obs.ContainerGuide):
                self.raise_warning('You must be in guide state to group parts')
                return
            group_name, ok = QInputDialog.getText(
                self,
                'New Part Group',
                'Enter the group name'
            )
            if ok:
                try:
                    pgn.group_selected_parts(
                        root_name=group_name,
                        side='center'
                    )
                except Exception as e:
                    traceback.print_exc()
                    self.raise_error(e)

    def set_post_task_redraw(self, value):
        self.build_task_widget.post_task_redraw = value

    def export_skin_clusters(self):
        self.build_task_tree(
            erdt.get_export_skin_clusters_tasks(
                self.get_build_root()
            )
        )
        self.notification_launcher.success_notification(text="Exported Skin Clusters Successfully")

    def import_skin_clusters(self):
        self.build_task_tree(
            irdt.get_import_skin_clusters_tasks(
                self.get_build_root()
            )
        )
        self.notification_launcher.success_notification(text="Imported Skin Clusters Successfully")

    def set_batch_thread_count(self):
        value, success = QInputDialog.getInt(
            self,
            'Set Batch Thread Count',
            'Thread Count',
            value=self.jobs_widget.batch_job_pool.maxThreadCount(),
            min=1,
            max=8
        )
        if success:
            self.jobs_widget.batch_job_pool.setMaxThreadCount(value)

    def build_all_parts(self):
        self.build_task_tree(
            tpt.get_test_parts_task(
                self.get_build_root()
            )
        )

    def export_all_rig_data(self):
        if env.local_build_directory != fut.get_user_build_directory():
            if not self.raise_question(
                    'Are you sure you want to export rig_data to:\n%s' % env.local_build_directory
            ):
                return
        self.build_task_tree(
            erdt.get_export_rig_data_tasks(
                self.get_build_root()
            )
        )
        self.notification_launcher.success_notification(text="Exported All External Rig Data Successfully")

    def export_parts_data(self):
        if env.local_build_directory != fut.get_user_build_directory():
            if not self.raise_question(
                    'Are you sure you want to export part rig_data to:\n%s' % env.local_build_directory
            ):
                return
        root_task = erdt.get_export_parts_rig_data_tasks(self.get_build_root())
        if not root_task.children:
            self.notification_launcher.error_notification(text="No Parts found")
            self.clear_task_root()
            return
        self.build_task_tree(root_task)
        self.notification_launcher.success_notification(text="Exported External Rig < Part > Data Successfully")

    def export_container_rig_data(self, rig_data_key):
        rig_data_directory = '%s/rig_data' % env.local_build_directory
        if not os.path.exists(rig_data_directory):
            os.makedirs(rig_data_directory)
        container = self.controller.root
        function = container.data_getters[rig_data_key]
        try:
            data = function()
            with open('%s/%s.json' % (rig_data_directory, rig_data_key), mode='w') as f:
                json.dump(
                    data,
                    f,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            self.notification_launcher.success_notification(
                text="Exported External Rig Data < %s > Successfully" % rig_data_key)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            self.notification_launcher.warning_notification(
                text="Failed to export < %s > data. (See log for details)" % rig_data_key)
            return

    def import_all_rig_data(self):
        self.build_task_tree(
            irdt.get_import_rig_data_tasks(
                self.get_build_root()
            )
        )
        self.notification_launcher.success_notification(text="Imported All External Rig Data Successfully")

    def import_parts_data(self):
        self.build_task_tree(
            irdt.get_import_parts_rig_data_tasks(
                self.get_build_root()
            )
        )
        self.notification_launcher.success_notification(text="Imported External Rig < Part > Data Successfully")

    def import_container_rig_data(self, rig_data_key):
        rig_data_directory = '%s/rig_data' % env.local_build_directory
        container = self.controller.root
        if rig_data_key:
            self.raise_warning('Failed to find setter for "%s" data.' % rig_data_key)
            return
        function = container.data_getters[rig_data_key]
        try:
            with open('%s/%s.json' % (rig_data_directory, rig_data_key), mode='w') as f:
                data = json.load(f)
            self.notification_launcher.success_notification(
                text="Imported External Rig Data < %s > Successfully" % rig_data_key)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            self.notification_launcher.warning_notification(
                text="Failed to import < %s > data. (See log for details)" % rig_data_key)
            return
        function(data)

    def set_external_rig_data(self, value):
        self.controller.root.use_external_rig_data = value
        self.update_menubar()

    def set_manual_rig_data(self, value):
        self.controller.root.use_manual_rig_data = value
        self.update_menubar()

    def activate_products(self):
        rig_blueprint = None
        if self.controller.root:
            rig_blueprint = bpu.get_blueprint()
        elif env.local_build_directory:
            blueprint_path = '%s/rig_blueprint.json' % env.local_build_directory
            if os.path.exists(blueprint_path):
                try:
                    with open(blueprint_path, mode='r') as f:
                        rig_blueprint = json.load(f)
                        rig_blueprint = lpu.update_legacy_blueprint(
                            os.environ['PROJECT_CODE'],
                            os.environ['ENTITY_NAME'],
                            rig_blueprint
                        )
                except Exception as e:
                    self.raise_warning('Unable to parse blueprint: %s' % blueprint_path)
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    return
        else:
            self.raise_warning('Unable to find build_directory/blueprint')
            return
        if not rig_blueprint:
            self.raise_warning('Unable to find blueprint')
            return

        self.products_widget.set_blueprint(rig_blueprint, True)
        self.products_widget.build_callback = functools.partial(
            self.update_blueprint_products,
            rig_blueprint
        )
        self.show_products_widget()
        self.products_widget.update_visibility()
        self.products_widget.update_all(False)
        self.products_widget.skip_button_visibility(False)

    def set_log_level(self, level):
        log = logging.getLogger('rig_build')
        log.setLevel(level)

    def export_build(self):
        file_name, types = QFileDialog.getSaveFileName(
            self,
            'export build',
            env.local_build_directory,
            'Json (*.json)'
        )
        if file_name:
            task_root = self.get_rig_task_root()
            data = task_root.serialize()

            with open(file_name, mode='w') as f:
                try:
                    json.dump(
                        data,
                        f,
                        sort_keys=True,
                        indent=4,
                        separators=(',', ': ')
                    )
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    self.raise_warning('Failed to serialize tasks. See log for details.')
            self.raise_message('Exported build to : %s' % file_name)
        self.reload_widget_state()

    def publish_realtime_product(self):
        if self.controller.root is None or self.raise_question(
                'Have you saved your work?\n Building Realtime rig will clear the current scene..'
        ):
            sig.set_build_directory(fut.get_latest_product_directory())
            self.build_task_tree(
                rtt.get_realtime_tasks(
                    self.get_build_root(),
                    save=True
                )
            )

    def build_to_rig_state(self, rig_blueprint, callback=None):
        root_task = jbs.get_rig_tasks(
            self.get_build_root(
                rig_blueprint=rig_blueprint
            ),
        )
        root_task.name = 'Build To Rig State'
        self.build_task_tree(
            root_task,
            callback=callback,
        )

    def create_auto_rig(self):
        if not os.path.exists(env.local_build_directory):
            os.makedirs(env.local_build_directory)
        self.build_task_tree(
            jbs.get_auto_rig_tasks(
                self.get_build_root(),
                save_action=None
            )
        )

    def publish_auto_rig(self):
        if not os.path.exists(env.local_build_directory):
            os.makedirs(env.local_build_directory)
        self.build_task_tree(
            jbs.get_auto_rig_tasks(
                self.get_build_root(),
                save_action='publish'
            )
        )

    def create_anim_rig_current(self):
        if not env.local_build_directory or not os.path.exists(env.local_build_directory):
            self.raise_warning(
                'The current build directory does not exist: %s' % env.local_build_directory
            )
            return
        if self.controller.root is None or self.raise_question(
                'Have you saved your work?\n Building Realtime rig will clear the current scene..'
        ):
            task_root = jbs.get_anim_rig_tasks(
                self.get_build_root(),
                save=False
            )
            self.build_task_tree(
                task_root
            )

    def create_realtime_current(self):
        if not env.local_build_directory or not os.path.exists(env.local_build_directory):
            self.raise_warning(
                'The current build directory does not exist: %s' % env.local_build_directory
            )
            return
        if self.controller.root is None or self.raise_question(
                'Have you saved your work?\n Building Realtime rig will clear the current scene..'
        ):
            self.build_task_tree(
                rtt.get_realtime_tasks(
                    self.get_build_root(),
                    save=True
                )
            )

    def create_low(self):
        if not env.local_build_directory or not os.path.exists(env.local_build_directory):
            self.raise_warning(
                'The current build directory does not exist: %s' % env.local_build_directory
            )
            return

        if self.controller.root is None or self.raise_question(
                'Have you saved your work?\n Building Low Rig will clear the current scene.'
        ):
            task_root = lrt.get_low_rig_tasks(
                self.get_build_root()
            )
            self.build_task_tree(task_root)

    def assign_nurbs_surface(self):
        logger = logging.getLogger('rig_build')
        try:
            surface_name, parts = pgn.assign_nurbs_surface(self.controller)
            self.raise_warning('Success!: Set Surface data for : %s' % parts)
        except Exception as e:
            logger.error(traceback.format_exc())
            self.raise_exception(Exception('Failed to set surface data.  See script editor for details'))

    def remove_nurbs_surface_assignments(self):
        logger = logging.getLogger('rig_build')
        try:
            parts = pgn.remove_nurbs_surface_assignments(self.controller)
            self.raise_warning('Success!: Removed surfaces for : %s' % parts)
        except Exception as e:
            logger.error(traceback.format_exc())
            self.raise_exception(Exception('Failed to set surface data.  See script editor for details'))

    def mirror_slide_values(self):
        spline_parts = self.controller.root.find_parts(obs.SurfaceSplineGuide, obs.DoubleSurfaceSplineGuide)
        for part in spline_parts:
            for handle in part.spline_handles:
                if handle.side == 'left':
                    handle_tokens = handle.name.split('_')
                    handle_tokens[0] = 'R'
                    predicted_handle_name = '_'.join(handle_tokens)
                    if predicted_handle_name in self.controller.named_objects:
                        right_handle = self.controller.named_objects[predicted_handle_name]
                        if part.side is None:
                            right_handle.plugs['Slide'].set_value(handle.plugs['Slide'].get_value() * -1.0)
                        else:
                            right_handle.plugs['Slide'].set_value(handle.plugs['Slide'].get_value())

    def publish_popup(self):
        if not isinstance(self.controller.root, obs.Container):
            self.raise_warning('You cannot publish in guide state.')
            return
        if not self.controller.root:
            self.raise_warning('Unable to locate rig')
            return
        if self.controller.root.has_been_finalized:
            self.raise_warning('The rig has been finalized you can no longer publish')
            return
        if self.controller.face_network and self.controller.face_network.has_been_finalized:
            self.raise_warning('The face has been finalized you can no longer publish')
            return
        question_lines = [
            'Publishing is a destructive process!',
            'Edits to a published rig cannot be saved',
            'Do you want to continue ?'
        ]
        if self.raise_question(
                '\n'.join(question_lines),
                title='Publish'
        ):
            # Check if there is newer alembic before publishing
            alembic_directory = fut.get_abc_directory().replace('\\', '/')
            get_latest = fut.get_latest_abc()
            if get_latest:
                latest_geometry_file = get_latest.replace('\\', '/')
                for path in self.controller.root.geometry_paths:
                    path = path.replace('\\', '/')
                    if path.startswith(alembic_directory):
                        if path != latest_geometry_file:
                            response = QMessageBox.question(
                                self,
                                'Alembic Check',
                                'There appears to be a newer ABC file.\n\nCurrent:\n%s\n\nNewer:\n%s\n\nDo you wish to continue?' % (
                                    path,
                                    latest_geometry_file
                                ),
                                QMessageBox.StandardButton.Yes,
                                QMessageBox.StandardButton.No
                            )
                            if response == QMessageBox.No:
                                return False
            dialog = PublishWidget(self)
            dialog_rect = dialog.rect()
            offset_position = QPoint(
                dialog_rect.width(),
                dialog_rect.height()
            )
            realtime_checkbox_off = (obs.Environment, obs.Prop, obs.Vehicle)
            if fut.get_show_config_data().get('realtime_checkbox_off') is not None:
                show_rt_box_off = fut.get_show_config_data().get('realtime_checkbox_off')
                get_obs_func = {
                    "Environment": obs.Environment,
                    "Prop": obs.Prop,
                    "Vehicle": obs.Vehicle,
                    "Character": obs.Character,
                    "Biped": obs.Biped,
                    "Quadruped": obs.Quadruped
                }
                result_obs = []
                for x in show_rt_box_off:
                    if x in get_obs_func:
                        result_obs.append(get_obs_func[x])
                    else:
                        self.raise_warning("WARNING: {} is not a valid entry, check show_config.json".format(x))
                realtime_checkbox_off = tuple(result_obs)
            if isinstance(self.controller.root, realtime_checkbox_off):
                dialog.realtime_checkbox.setChecked(False)
            dialog.label.setText('Publish Rig Product')
            dialog.setWindowTitle('Publish Rig Product')
            dialog.move(self.rect().center() - dialog.rect().center() - offset_position)
            dialog.show()
            dialog.raise_()
            dialog.save_signal.connect(self.publish_rig)

    def raise_message(self, message):
        logger = logging.getLogger('rig_build')
        logger.info(message)
        message_box = QMessageBox(self)
        message_box.setModal(False)
        message_box.setWindowTitle('Message')
        message_box.setText(message)
        message_box.show()
        return message_box

    # @Slot()
    # def update_batch_text(self, data):
    #     self.realtime_status_widget.text_edit.append(data)
    #     scroll_position = self.realtime_status_widget.text_edit.verticalScrollBar().maximum()
    #     self.realtime_status_widget.text_edit.verticalScrollBar().setValue(scroll_position)

    def freeze_module_versions(self):
        if self.controller and isinstance(self.controller.root, obs.BaseContainer):
            self.controller.freeze_module_versions()

    #
    # def bake_shards(self):
    #     if self.raise_question(
    #         'Have you saved your work?\nBaking Shards is a destructive process. work may be lost if you havent saved.\nDo you want to continue ?'):
    #         try:
    #             self.controller.bake_shards()
    #             self.show_finalized_widget()
    #         except Exception:
    #             self.raise_exception(Exception('Failed to finalize rig. See script editor for details'))

    def set_custom_handles(self, value):
        self.controller.root.custom_handles = value

    def go_home(self):
        sig.set_build_directory(fut.get_user_build_directory())

    def browse_for_build_directory(self):
        if self.controller.root:
            self.raise_warning(
                'There is already a rig loaded. You can only change the build directory from an Empty Scene'
            )
            return
        build_directory = QFileDialog.getExistingDirectory(
            self,
            'Set Build Directory',
            os.path.dirname(str(env.local_build_directory)),
        )
        if build_directory:
            sig.set_build_directory(build_directory)

    def set_build_directory(self, build_directory):
        self.update_directory_label(build_directory)

    def run_serialization_tests(self):
        data = self.controller.serialize()
        self.controller.reset()
        self.controller.deserialize(data)

    def export_surfaces(self):
        if self.controller and self.controller.root:

            # Get Data
            surface_splines = self.controller.root.find_parts(
                obs.SurfaceSplineGuide,
                obs.DoubleSurfaceSplineGuide,
                obs.SurfaceSpline,
                obs.DoubleSurfaceSpline
            )
            surface_data = dict(
                (x.follicle_surface.name, x.follicle_surface.get_surface_data()) for x in surface_splines if
                x.follicle_surface)

            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Nurbs Surfaces',
                    '%s/nurbs_surfaces.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(
                        file_name,
                        surface_data
                    )
                else:
                    write_data(
                        'nurbs_surfaces.json',
                        surface_data
                    )
                self.notification_launcher.success_notification(
                    text="Exported Nurbs Surfaces Successfully"
                )
            else:
                self.save_json_file(
                    name='nurbs_surfaces.json',
                    data=surface_data,
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Nurbs Surfaces Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_surfaces(self):
        def do_it(surface_data):
            for surface_name in surface_data:
                if surface_name in self.controller.named_objects:
                    surface = self.controller.named_objects[surface_name]
                    surface.set_surface_data(*surface_data[surface_name])

        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/nurbs_surfaces.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/nurbs_surfaces.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Nurbs Surfaces',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        do_it(json.loads(f.read()))
                    self.notification_launcher.success_notification(
                        text="Import Nurbs Surfaces Successfully"
                    )

            else:
                file_name = file_path
                if os.path.exists(file_name):
                    with open(file_name, mode='r') as f:
                        do_it(json.loads(f.read()))
                    self.notification_launcher.success_notification(
                        text="Import Nurbs Surfaces Successfully"
                    )

                else:
                    self.notification_launcher.warning_notification(
                        text=("Nurbs Surfaces File not found: %s" % file_name.split('/')[-1])
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_hierarchy(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Hierarchy',
                    '%s/hierarchy.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(
                        file_name,
                        phi.get_named_hierarchy_data()
                    )
                    self.notification_launcher.success_notification(
                        text="Exported Hierarchy Successfully"
                    )
            else:
                self.save_json_file(
                    name='hierarchy.json',
                    data=phi.get_named_hierarchy_data(),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Hierarchy Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_hierarchy(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/hierarchy.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/hierarchy.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Hierarchy',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        data = json.load(f)
            else:
                data = self.load_json_file('hierarchy.json')

            if data:
                phi.set_named_hierarchy_data(data)
                self.notification_launcher.success_notification(
                    text="Import Hierarchy Successfully"
                )
            else:
                self.notification_launcher.warning_notification(
                    text="Hierarchy File not found: %s" % file_name.split('/')[-1]
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def reset_hierarchy(self):
        if self.controller and self.controller.root:
            self.controller.root.clear_parent_joints()

    def reset_spaces(self):
        if self.controller and self.controller.root:
            self.controller.root.clear_spaces()

    def explore_build(self):
        logging.getLogger('rig_build').info('Exploring Build: %s' % env.local_build_directory)
        os.system('start %s' % env.local_build_directory)

    def save_selection(self):
        self.saved_selection = self.controller.scene.list_selected_vertices()

    def load_selection(self):
        self.controller.scene.select(self.saved_selection, add=True)

    def assign_closest_vertices(self):
        mesh_names = self.controller.get_selected_mesh_names()
        self.controller.assign_closest_vertices(self.controller.root, mesh_names[-1])

    def delete_geometry(self):
        if not self.controller.root.product_paths['abc']:
            logging.getLogger('rig_build').warning('No geometry in the rig to delete')
            return

        geometry_to_delete = []
        for geo in self.controller.root.geometry_group.children:
            if geo.layer == self.controller.current_layer:
                geometry_to_delete.append(geo)
        del geo

        self.controller.schedule_objects_for_deletion(geometry_to_delete)
        del geometry_to_delete
        self.controller.delete_scheduled_objects()
        self.controller.root.product_paths['abc'] = None

    def delete_origin_geometry(self):
        if not self.controller.root.origin_geometry_group.children:
            logging.getLogger('rig_build').warning('No origin geometry in the rig to delete')
            return

        geometry_to_delete = []
        for geo in self.controller.root.origin_geometry_group.children:
            if geo.layer == self.controller.current_layer:
                geometry_to_delete.append(geo)
        del geo
        self.controller.schedule_objects_for_deletion(geometry_to_delete)
        del geometry_to_delete
        self.controller.delete_scheduled_objects()
        self.controller.root.origin_geometry_data = []

    def delete_utility_geometry(self):
        if not self.controller.root.utility_geometry_paths:
            logging.getLogger('rig_build').warning('No utility geometry in the rig to delete')
            return

        geometry_to_delete = []
        for geo in [x for x in self.controller.root.utility_geometry_group.children
                    if x != self.controller.root.origin_geometry_group]:  # Avoid deleting origin_geometry_group
            if geo.layer == self.controller.current_layer:
                geometry_to_delete.append(geo)
        del geo, x

        self.controller.schedule_objects_for_deletion(geometry_to_delete)
        del geometry_to_delete
        self.controller.root.utility_geometry_paths = []
        self.controller.delete_scheduled_objects()

        logging.getLogger('rig_build').info('Utility geometry removed')

    def delete_low_geometry(self):
        if not self.controller.root.low_geometry_paths:
            logging.getLogger('rig_build').warning('No low geometry in the rig to delete')
            return

        geometry_to_delete = []
        for geo in self.controller.root.low_geometry_group.children:
            if geo.layer == self.controller.current_layer:
                geometry_to_delete.append(geo)
        del geo

        self.controller.schedule_objects_for_deletion(geometry_to_delete)
        del geometry_to_delete
        self.controller.delete_scheduled_objects()
        self.controller.root.low_geometry_paths = []

    def import_abc_product(self):
        if self.controller and self.controller.root:
            alembic_directory = fut.get_abc_directory()
            path, types = QFileDialog.getOpenFileName(
                self,
                'Import ABC Product',
                alembic_directory,
                'Alembic/MayaScene (*.ma *.mb *.abc)'
            )
            if os.path.exists(path):
                if not path.startswith(alembic_directory):
                    logging.getLogger('rig_build').warning(
                        'Abc product must be picked from the following location%s' % alembic_directory)
                    self.notification_launcher.error_notification(
                        text=('Abc product must be picked from the following location%s' % alembic_directory)
                    )
                    return
                logging.getLogger('rig_build').info('Importing geometry from : %s' % path)
                gtl.import_abc_product(
                    'abc',
                    path,
                    store_path=True
                )
                self.notification_launcher.success_notification(
                    text="Imported ABC Product Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_utility_geometry(self):
        if self.controller and self.controller.root:
            # New Location
            file_path = fut.get_userdata_build_directory()
            if not os.path.exists(file_path):
                # Old Location
                file_path = env.local_build_directory

            path, types = QFileDialog.getOpenFileName(
                self,
                'Import Utility Geometry',
                file_path,
                'Alembic/MayaScene (*.ma *.mb *.abc)'
            )
            if os.path.exists(path):
                logging.getLogger('rig_build').info('Importing Utility Geometry from : %s' % path)
                gtl.import_container_geometry_path(
                    self.controller.root,
                    path,
                    self.controller.root.utility_geometry_group,
                    'utility_geometry'
                )
                standardised_path = fut.to_relative_path(path, build_dir=file_path)
                self.controller.root.utility_geometry_paths.append(standardised_path)
                self.notification_launcher.success_notification(
                    text="Import Utility Geometry Successfully"
                )
            else:
                logging.getLogger('rig_build').warning('Utility Geometry path provided does not exist: %s' % path)
                self.notification_launcher.warning_notification(
                    text=("Utility Geometry path provided does not exist: %s" % path)
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_low_geometry(self):
        if self.controller and self.controller.root:
            # New Location
            file_path = fut.get_userdata_build_directory()
            if not os.path.exists(file_path):
                # Old Location
                file_path = env.local_build_directory

            path, types = QFileDialog.getOpenFileName(
                self,
                'Import Low Geometry',
                file_path,
                'Alembic/MayaScene (*.ma *.mb *.abc)'
            )
            if os.path.exists(path):
                logging.getLogger('rig_build').info('Importing Low Geometry from : %s' % path)
                gtl.import_container_geometry_path(
                    self.controller.root,
                    path,
                    self.controller.root.low_geometry_group,
                    'low_geometry'
                )
                standardised_path = fut.to_relative_path(path, build_dir=file_path)
                self.controller.root.low_geometry_paths.append(standardised_path)
                self.notification_launcher.success_notification(
                    text="Import Low Geometry Successfully"
                )
            else:
                logging.getLogger('rig_build').warning('Low Geometry path provided does not exist: %s' % path)
                self.notification_launcher.warning_notification(
                    text=("Low Geometry path provided does not exist: %s" % path)
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def delete_root(self):
        if self.controller and self.controller.root:
            self.controller.root.delete()

    def view_as_json(self):
        if self.controller:
            file_name = '%s/data.json' % os.path.expanduser('~')
            write_data(
                file_name,
                self.controller.serialize()
            )
            os.system('start %s' % file_name)

    def export_blueprint(self):
        if self.controller and self.controller.root:

            file_name, types = QFileDialog.getSaveFileName(
                self,
                'Export Rig Blueprint',
                '%s/rig_blueprint.json' % env.local_build_directory,
                'Json (*.json)'
            )
            if file_name:
                write_data(file_name, bpu.get_blueprint())
                self.notification_launcher.success_notification(
                    text="Exported Rig Blueprint Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def frame_current_task(self):
        if self._build_tasks:
            current_task = self._build_tasks[self._build_index]
            self.build_task_widget.frame_task(current_task)

    def setup_paused_state(self, task):
        self.build_task_widget.setup_button_state('stopped')
        self.build_task_widget.frame_task(task)
        self.build_task_widget.close_busy_widget()
        self.controller.scene.refresh(suspend=False)
        self.controller.scene.refresh()

    def setup_failed_state(self, task):
        task.status = 'failed'
        self.build_task_widget.setup_button_state('no_buttons')
        logging.getLogger('rig_build').error(traceback.format_exc())
        self.build_task_widget.close_busy_widget()
        self.build_task_widget.frame_task(task)
        self.build_task_widget.update_view_task(task)
        self._build_tasks = None
        self._build_index = 0
        self.raise_warning(
            '"%s" Errored \n See log for details. ' % task.name,
            window_title='Build Error'
        )
        self.build_task_widget.close_busy_widget()
        self.controller.scene.refresh(suspend=False)
        self.controller.scene.refresh()
        self.set_build_callback(None)
        self.controller.failed_state = True
        raise

    def execute_next(self):
        current_item = self._build_tasks[self._build_index]
        if self._executing:
            next_task_name = 'None'
            if len(self._build_tasks) > self._build_index + 1:
                next_task_name = self._build_tasks[self._build_index + 1].name
            try:
                raise Exception(
                    'Execution for the next task (%s) began before the last task (%s) completed.' % (
                        next_task_name,
                        current_item.name
                    )
                )
            except Exception as e:
                self.setup_failed_state(current_item)
                return
        self._executing = True
        current_item.current = False
        self.build_task_widget.update_view_task(current_item)
        self._build_index += 1
        next_item = self._build_tasks[self._build_index]
        next_item.current = True
        next_item.execute()
        return next_item

    def prepare_for_build(self):
        self.build_task_widget.setup_button_state('building')
        self.build_task_widget.show_busy_wdget()
        edtu.close_all_editors(self.controller)
        self._stop_build = False
        self.controller.scene.refresh(suspend=True)
        QApplication.processEvents()

    def clear_task_root(self):
        self.set_root_task(None)

    def set_root_task(self, task_root):
        self.build_task_widget.setup_button_state('stopped')
        self.build_task_widget.set_root_task(task_root)
        self._stop_build = False
        self._build_index = 0
        if task_root:
            self.show_task_widget()
            self._build_tasks = list(tut.flatten(task_root))
        else:
            self._build_tasks = None
            self.reload_widget_state()

    def build(self):
        self._build_started = time.time()
        self.prepare_for_build()
        while True:
            task = self.execute_next()
            if self._build_tasks is None:
                break
            elif self._stop_build or task.break_point:
                self.setup_paused_state(task)
                break

    def finalize(self):
        if isinstance(self.controller.root, obs.Container) and self.controller.root.has_been_finalized:
            self.raise_warning('The rig has already been finalized')
            return
        if self.controller.face_network and self.controller.face_network.has_been_finalized:
            self.raise_warning('The face has already been finalized')
            return
        if self.raise_question(
                'Have you saved your work?\nFinalizing is a destructive process. work may be lost if you havent saved.\nDo you want to continue ?'
        ):
            self.build_task_tree(
                fintsk.get_finalize_rig_tasks(
                    self.get_build_root(),
                    publish_type='full'  # For geo deletion tags
                )
            )

    def update_model(self, rig_blueprint, remove_vertices=False, callback=None):
        root_task = jbs.get_model_update_tasks(
            self.get_build_root(
                rig_blueprint=rig_blueprint
            ),
            remove_vertices=remove_vertices
        )

        root_task.name = 'Model Update'
        self.build_task_tree(
            root_task,
            callback=callback
        )


    def toggle_rig_state_slot(self, *args):
        """
        Used for widget signal connections
        """
        self.toggle_rig_state()


    def toggle_rig_state(self, callback=None, build_directory=None):
        controller = self.controller
        if not controller or not controller.root:
            self.raise_warning('No rig found')
            return
        build_root = self.get_build_root(retrieve_data=False, build_directory=None)  # Data gets retrieved in the build tasks
        first_task_root = tglt.get_toggle_tasks(build_root)
        callback_root = None
        if isinstance(controller.root, obs.Container) and controller.root.use_external_rig_data:
            if controller.root.use_manual_rig_data:
                question_lines = [
                    'Have you saved your work?',
                    'This blueprint is using external rig data and unsaved rig state work wil be lost.',
                    'would you like to continue?'
                ]
                if not self.raise_question(
                        '\n'.join(question_lines),
                        title='Did you save before togging?'
                ):
                    return
            callback_root = first_task_root
            first_task_root = erdt.get_export_rig_data_tasks(build_root)

        if callback_root:
            self.build_task_tree(
                first_task_root,
                callback=functools.partial(
                    self.build_task_tree,
                    callback_root,
                    callback=callback
                )
            )
        else:
            self.build_task_tree(
                first_task_root,
                callback=callback
            )


    def merge_blueprint(self):
        if not self.controller:
            self.raise_warning('No controller found')
            return
        if not isinstance(self.controller.root, obs.ContainerGuide):
            self.raise_warning('No guide state root found')
            return
        question_lines = [
            'Have you saved your work?',
            'Merging is not reversable. Work may be lost if you havent saved.',
            'would you like to continue?'
        ]
        if not self.raise_question(
                '\n'.join(question_lines)
        ):
            return
        file_name, types = QFileDialog.getOpenFileName(
            self,
            'Merge Blueprint',
            env.local_build_directory,
            'Json (*.json)'
        )
        if file_name:
            with open(file_name, mode='r') as f:
                try:
                    rig_blueprint = json.load(f)
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    self.raise_warning(
                        'Unable to parse json file: %s' % file_name
                    )
                    return
                if 'part_members' not in rig_blueprint:
                    if not self.raise_question(
                            'This blueprint seems to be incorrectly formatted. Would you like to continue'):
                        return

            task_root = gtsk.get_merge_tasks_root(
                self.get_build_root(
                    rig_blueprint=rig_blueprint
                )
            )
            self.build_task_tree(task_root)

    def import_blueprint(self):
        if not self.controller:
            self.raise_warning('No controller found')
            return

        file_name, types = QFileDialog.getOpenFileName(
            self,
            'Import Rig Blueprint',
            env.local_build_directory,
            'Json (*.json)'
        )
        if file_name:
            with open(file_name, mode='r') as f:
                try:
                    blueprint = json.load(f)
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    self.raise_exception(
                        Exception('Unable to parse json file: %s' % file_name)
                    )
                if 'part_members' not in blueprint:
                    if not self.raise_question(
                            'This blueprint seems to be incorrectly formatted. Would you like to continue'):
                        return
                logging.getLogger('rig_build').info('Building blueprint: %s' % file_name)
                self.build_blueprint(blueprint)

    def check_then_build_blueprint_path(self, blueprint_path, build_face=False, callback=None):
        if not isinstance(blueprint_path, basestring):
            self.raise_warning('Invalid path type: %s' % type(blueprint_path))
            return
        if not os.path.exists(blueprint_path):
            self.raise_warning('Blueprint path not found: "%s"' % blueprint_path)
            return
        try:
            with open(blueprint_path, mode='r') as f:
                blueprint = json.load(f)
        except Exception as e:
            self.raise_warning('Unable to parse: %s' % blueprint_path)
            return
        if not isinstance(blueprint, dict):
            self.raise_warning('Invalid blueprint type: %s parsed from: %s' % (type(blueprint), blueprint_path))
            return
        sig.set_build_directory(os.path.dirname(blueprint_path))
        self.check_then_build_blueprint(
            blueprint,
            build_face=build_face,
            callback=callback
        )

    def check_then_build_blueprint(self, blueprint, build_face=False, callback=None):
        if not isinstance(blueprint, dict):
            self.raise_warning('Invalid blueprint type: %s' % type(blueprint))
            return
        blueprint = lpu.update_legacy_blueprint(
            os.environ['PROJECT_CODE'],
            os.environ['ENTITY_NAME'],
            blueprint
        )
        self.products_widget.set_blueprint(blueprint)
        if build_face:
            callback = functools.partial(
                self.import_face_blueprint,
                callback=callback
            )
        if not self._check_for_new_products or self.products_widget.is_up_to_date():
            self.show_products_widget()
            self.products_widget.animate_widget_visibility()
            self.build_blueprint(
                blueprint,
                callback=callback
            )

        else:
            self.products_widget.build_callback = functools.partial(
                self.update_blueprint_products,
                blueprint,
                callback=callback
            )
            self.show_products_widget()
            self.products_widget.update_visibility()
            self.products_widget.update_all(True)
            self.products_widget.skip_button_visibility(True)

    def update_blueprint_products(self, blueprint, product_data, callback=None):
        if self.controller.root:
            question_lines = [
                'Have you saved your work? ',
                'A build error during update can result in loss of work.',
                'Would you like to continue?'
            ]
            if self.raise_question('\n'.join(question_lines)):
                self.controller.schedule_objects_for_deletion(self.controller.root)
                del self.controller.root
                self.controller.delete_scheduled_objects()
                self.controller.scene.delete_unused_nodes()
                self.controller.reset()
                self.set_root_task(None)
                QApplication.processEvents()
            else:
                self.raise_warning('Update aborted.')
                return
        remove_vertices = product_data.pop('remove_vertices', False)
        blueprint['product_paths'].update(product_data)
        if 'guide_blueprint' in blueprint:
            blueprint['guide_blueprint']['product_paths'].update(product_data)
        if not os.path.exists(env.local_build_directory):
            os.makedirs(env.local_build_directory)
        if any(x in product_data for x in ['abc', 'abc_anim']):
            self.update_model(
                blueprint,
                remove_vertices=remove_vertices,
                callback=callback
            )
        else:
            self.build_blueprint(
                blueprint,
                callback=callback
            )

    def toggle_to_guide(self):
        if isinstance(self.controller.root, obs.Container):
            self.toggle_rig_state()

    def build_guide_blueprint_path(self, blueprint):
        self.check_then_build_blueprint_path(
            blueprint,
            callback=self.toggle_to_guide
        )

    def build_blueprint(self, blueprint, callback=None):
        # try:
        #     btup.setup_local_build_directory()
        # except Exception as e:
        #     logging.getLogger('rig_build').error(traceback.format_exc())
        #     self.raise_warning('Failed to setup build directory. See log for details')
        self.build_task_tree(
            self.get_rig_task_root(
                rig_blueprint=blueprint
            ),
            callback=callback
        )

    def get_build_root(self, **kwargs):
        retrieve_data = kwargs.get('retrieve_data', True)
        build_directory = kwargs.pop('build_directory', env.local_build_directory)
        self.update_progress(
            message='Getting Entity Data... ',
            maximum=3
        )
        kwargs.setdefault(
            'task_callback',
            self.build_task_callback
        )
        kwargs.setdefault(
            'children_about_to_be_inserted_callback',
            self.child_tasks_about_to_be_inserted
        )
        kwargs.setdefault(
            'children_inserted_callback',
            self.child_tasks_inserted
        )
        builds = []
        if not os.path.exists(build_directory):
            logging.getLogger('rig_build').critical('Build directory doesnt exist: %s' % build_directory)

        if 'rig_blueprint' not in kwargs:
            if not os.path.exists('%s/rig_blueprint.json' % build_directory):
                if self.controller.root:
                    rig_blueprint = bpu.get_blueprint()
                    kwargs['rig_blueprint'] = rig_blueprint

        try:
            for build in bti.yield_builds(
                    os.getenv('PROJECT_CODE'),
                    os.getenv('ENTITY_NAME'),
                    self.controller,
                    build_directory,
                    **kwargs
            ):
                if not build:
                    raise Exception('build is None')
                if not build.build_directory:
                    logging.getLogger('rig_build').critical('%s has no directory' % build.entity)
                if retrieve_data:
                    if not build.build_directory:
                        self.raise_warning('unable to resolve a build_directory for %s' % build.entity)
                    self.update_progress(message='%s\nLoading rig_blueprint.json...' % build.entity, value=1)
                    build.retrieve_rig_blueprint()
                    self.update_progress(message='%s\nLoading face_blueprint.json...' % build.entity, value=2)
                    build.retrieve_face_blueprint()
                    self.update_progress(message='%s\nLoading callbacks...' % build.entity, value=3)
                build.retrieve_callbacks()
                builds.append(build)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            self.raise_warning(
                'Failed to resolve build root. See log for details',
                window_title='Build resolution failed'
            )
            raise
        self.show_task_widget()
        return builds[0]

    def get_rig_task_root(self, **kwargs):
        if not env.local_build_directory:
            raise Exception('RigWidget.build_directory = None')
        if not os.path.exists(env.local_build_directory):
            os.makedirs(env.local_build_directory)
        logging.getLogger('rig_build').info('Resolving Build Tasks...')
        build_root = self.get_build_root(**kwargs)
        try:
            return bti.get_root_task(build_root)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            self.raise_warning(
                'Failed to resolve task root. See log for details',
                window_title='Task resolution failed'
            )
            raise

    def export_face_blueprint(self):
        if not self.controller.face_network:
            self.raise_warning('No Face Network detected. Unable to export')
            return
        if not self.controller.face_network.face_groups:
            self.raise_warning('No Face Network Groups detected. Unable to export')
            return

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            file_name, types = QFileDialog.getSaveFileName(
                self,
                'Export Face Network Blueprint',
                '%s/face_blueprint.json' % env.local_build_directory,
                'Json (*.json)'
            )
            if file_name:
                self.controller.export_face_blueprint(file_name=file_name)

        else:
            file_name = '%s/face_blueprint.json' % env.local_build_directory
            self.controller.export_face_blueprint(file_name=file_name)

    def import_face_blueprint(self, callback=None):
        if self.controller.root is None:
            self.raise_warning('There is no rig loaded')
            return
        if isinstance(self.controller.root, obs.ContainerGuide):
            self.raise_warning(
                'The rig is in Guide State.  You must toggle to Rig state to import a FaceNetwork'
            )
            return
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            face_blueprint_path, types = QFileDialog.getOpenFileName(
                self,
                'Import Face Network Blueprint',
                '%s/face_blueprint.json' % env.local_build_directory,
                'Json (*.json)'
            )
            if not face_blueprint_path:
                return
        else:
            face_blueprint_path = '%s/face_blueprint.json' % env.local_build_directory
        if self.controller.face_network:
            if not self.raise_question('There is already a face loaded. \nWould you like to merge?'):
                return False
        face_blueprint = None
        if os.path.exists(face_blueprint_path):
            with open(face_blueprint_path, mode='r') as f:
                try:
                    face_blueprint = json.loads(f.read())
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    self.raise_warning('Failed to parse face blueprint: %s' % face_blueprint_path)
                    return
        root_build = self.get_build_root(
            face_blueprint=face_blueprint
        )
        if self.run_face_blueprint_checks(root_build):
            self.build_task_tree(
                ftsk.get_face_tasks(root_build),
                callback=callback if callback else self.show_face_widget
            )
        else:
            self.reload_widget_state()

    def run_face_blueprint_checks(self, root_build):
        builds = tut.flatten(root_build)
        for build in builds:
            if build.face_blueprint:
                if 'groups' not in build.face_blueprint:
                    self.raise_warning(
                        'The blueprint json seems seems to be incorrectly formatted. Would you like to continue?'
                    )
                    return

                plugs = [x['driver_plug'] for x in build.face_blueprint['groups'] if 'driver_plug' in x]
                non_zero_plugs = [x for x in plugs if self.controller.objExists(x) and x is not None and round(
                    self.controller.scene.getAttr(x), 5) != 0.0]
                if non_zero_plugs:
                    print_plugs = [non_zero_plugs[x] for x in range(len(non_zero_plugs)) if x < 5]
                    question_string = 'Non zero driver plug values present\n\n%s\netc... \n\n' \
                                      'Do you want to continue?' % '\n'.join(print_plugs)
                    if not self.raise_question(question_string):
                        return
        return True

    def finalize_face_network(self):
        if not self.controller.face_network:
            self.raise_warning('Unable to locate face network.')
            return
        if self.controller.face_network.has_been_finalized:
            self.raise_warning('The Face has already been finalized')
            return

        question_lines = [
            'Have you saved your work?',
            'Finalizing is a destructive process. work may be lost if you haven\'t saved.',
            'Do you want to continue ?'
        ]
        if self.raise_question(
                '\n'.join(question_lines)
        ):
            self.show_task_widget()
            face_blueprint = self.controller.face_network.get_blueprint()
            task_root = fintsk.get_finalize_face_tasks(
                self.get_build_root(
                    face_blueprint=face_blueprint
                )
            )
            self.build_task_tree(
                task_root,
                callback=self.show_face_widget
            )

    def mirror_face_network(self):
        if not self.controller.face_network:
            raise Exception('FaceNetwork not found')
        face_blueprint = self.controller.face_network.get_blueprint()
        task_root = ftsk.get_mirror_face_tasks(
            self.get_build_root(
                face_blueprint=face_blueprint,
            )
        )
        self.build_task_tree(
            task_root,
            callback=self.show_face_widget
        )

    def child_tasks_inserted(self, parent, children):
        model = self.build_task_widget.view.model()
        descendants = []
        for child in children:
            descendants.extend(list(tut.flatten(child)))
        for task in reversed(descendants):
            self._build_tasks.insert(
                self._build_index + 1,
                task
            )
            self.build_task_widget.index_map[task.id] = model.createIndex(task.parent.children.index(task), 0, task)
        model.endInsertRows()

    def child_tasks_about_to_be_inserted(self, parent, child_count):
        model = self.build_task_widget.view.model()
        parent_index = self.build_task_widget.index_map[parent.id]
        model.beginInsertRows(
            parent_index,
            len(parent.children),
            len(parent.children) + child_count
        )

    def reset_build_tasks(self):
        self._build_index = 0
        self._build_tasks = None
        self._executing = False
        self.build_task_widget.set_root_task(None)
        self.controller.scene.refresh(suspend=False)
        self.controller.scene.refresh()
        self.set_build_callback(None)
        self.reload_widget_state()

    def build_task_callback(self, task):
        """
        Gets called once for each competed build task
        """
        if self._build_tasks is None:
            raise Exception('Rig._build_index is None')
        self._executing = False
        self.build_task_widget.update_view_task(task)
        if task.status == 'failed':
            self.setup_failed_state(task)
        if task == self._build_tasks[-1]:  # last task in build.
            self.build_task_widget.close_busy_widget()
            self.build_task_widget.setup_button_state('no_buttons')
            current_callback = self._build_callback
            self._build_index = 0
            self._build_tasks = None
            self.set_build_callback(None)
            root_task = self.build_task_widget.view.model().root
            self.controller.scene.refresh(suspend=False)
            self.controller.scene.refresh()

            if current_callback is None:
                warning_tasks = [x for x in tut.flatten(root_task) if x.status == 'warning']
                if warning_tasks:
                    time_string = '?'
                    if self._build_started:
                        time_string = str(datetime.timedelta(seconds=time.time() - self._build_started))

                    question_lines = [
                        '%s complete!' % root_task.name,
                        'time: %s' % time_string,
                        'Some warnings were raised during the build.',
                        'Would you like to review?'
                    ]
                    if self.raise_question(
                            '\n'.join(question_lines)
                    ):
                        self.build_task_widget.select_tasks(warning_tasks)
                        for warning_task in reversed(warning_tasks):
                            self.build_task_widget.frame_task(warning_task)
                            QApplication.processEvents()
                            return
                current_callback = self.reload_widget_state
            current_callback()


    def build_task_tree(self, task_root, callback=None):
        if task_root is None:
            raise Exception('Task tree root is None')
        if not task_root.children:
            self.reload_widget_state()
            raise Exception('Task tree root "%s" has no children' % task_root.name)
        self.set_build_callback(callback)
        self.set_root_task(task_root)
        self.show_task_widget()
        if self._auto_build:
            self.build()
        else:
            self.build_task_widget.setup_button_state('stopped')


    def save_work_popup(self):
        if self.dialog:
            self.dialog.close()
        self.dialog = SaveWidget(self)
        dialog_rect = self.dialog.rect()
        offset_position = QPoint(
            dialog_rect.width(),
            dialog_rect.height()
        )
        self.dialog.move(self.rect().center() - self.dialog.rect().center() - offset_position)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.save_signal.connect(self.save_work)

    def save_work(self, data):
        if not self.controller.root:
            self.raise_warning('Unable to locate rig')
            return
        if isinstance(self.controller.root, obs.Container) and self.controller.root.has_been_finalized:
            self.raise_warning('The rig has been finalized you can no longer save')
            return
        if self.controller.face_network and self.controller.face_network.has_been_finalized:
            self.raise_warning('The face has been finalized you can no longer save')
            return
        self.build_task_tree(
            savtsks.get_save_tasks(
                self.get_build_root(retrieve_data=False),
                comment=data['comment']
            )
        )

    def mock_publish_rig(self):
        if not self.controller.root:
            self.raise_warning('Unable to locate rig')
            return
        if not isinstance(self.controller.root, obs.Container):
            self.raise_warning('You can only publish in rig state.')
            return
        if self.controller.root.has_been_finalized:
            self.raise_warning('The rig has been finalized you can no longer publish')
            return
        if self.controller.face_network and self.controller.face_network.has_been_finalized:
            self.raise_warning('The face has been finalized you can no longer publish')
            return
        message_lines = [
            'Have you saved your work?',
            'Mock-Publishing is a destructive process. work may be lost if you havent saved.',
            'Do you want to continue ?'
        ]
        if self.raise_question(
                '\n'.join(message_lines),
                title='Mock Publish'
        ):
            self.build_task_tree(
                ptsk.get_mock_publish_tasks(
                    self.get_build_root(),
                    comment='Mock Publish'
                )
            )

    def publish_rig(self, data):
        if not self.controller.root:
            self.raise_warning('Unable to locate rig')
            return
        if not isinstance(self.controller.root, obs.Container):
            self.raise_warning('You can only publish in rig state.')
            return
        if self.controller.root.has_been_finalized:
            self.raise_warning('The rig has been finalized you can no longer publish')
            return
        if self.controller.face_network and self.controller.face_network.has_been_finalized:
            self.raise_warning('The face has been finalized you can no longer publish')
            return
        self.build_task_tree(
            ptsk.get_publish_tasks(
                self.get_build_root(),
                comment=data['comment'],
                notify_chat=data['publish_message_in_chat'],
                version_up_if_clashing=True  # User initialised, so try avoiding a clash error
            ),
            callback=functools.partial(
                self.publish_callback,
                build_realtime_rig=data.get('build_realtime_rig', True),
                build_anim_rig=data.get('build_anim_rig', True),
                publish_descendants=data.get('publish_descendants', True),
                queue_dependants=data.get('queue_dependants', True),
                comment=data['comment']
            )
        )

    def publish_callback(
            self,
            build_realtime_rig=True,
            build_anim_rig=True,
            publish_descendants=True,
            queue_dependants=False,
            comment=None
    ):
        self.reload_widget_state()
        batch_jobs, invalid_jobs = jbsu.get_publish_jobs(
            build_realtime_rig=build_realtime_rig,
            build_anim_rig=build_anim_rig,
            publish_descendants=publish_descendants,
            comment='BATCH: %s' % comment,
            queue_dependants=queue_dependants
        )

        if batch_jobs:
            self.jobs_widget.launch_jobs(*batch_jobs)
            self.show_jobs_widget()

        self.raise_warning(
            'Success!\n%s version %s\nRig has been published!' % (
                os.environ['ENTITY_NAME'],
                fut.get_current_work_versions()[0]
            ),
            window_title='Publish Complete'
        )

        if invalid_jobs:
            self.raise_warning(
                'Warning: Unable to resolve build directories for\n\n%s' % '\n'.join(invalid_jobs),
                window_title='Invalid Batch Jobs'
            )

    def export_input_transforms(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Input Transforms',
                    '%s/input_transforms.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(file_name, self.controller.get_input_transforms(self.controller.root))
                    self.notification_launcher.success_notification(
                        text="Exported Input Transforms Successfully"
                    )
            else:
                self.save_json_file(
                    name='input_transforms.json',
                    data=self.controller.get_input_transforms(self.controller.root),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Input Transforms Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_input_transforms(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/input_transforms.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/input_transforms.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Input Transforms',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    try:
                        with open(file_name, mode='r') as f:
                            self.controller.set_input_transforms(
                                self.controller.root,
                                json.loads(f.read())
                            )
                            self.notification_launcher.success_notification(
                                text="Imported Input Transforms Successfully"
                            )
                    except Exception as e:
                        logging.getLogger('rig_build').error(traceback.format_exc())
                        self.notification_launcher.warning_notification(
                            text="Unable to parse json data. (See log for details)"
                        )
            else:
                data = self.load_json_file('input_transforms.json')
                if data:
                    self.controller.set_input_transforms(
                        self.controller.root,
                        data
                    )
                    self.notification_launcher.success_notification(
                        text="Imported Input Transforms Successfully"
                    )
                else:
                    self.notification_launcher.warning_notification(
                        text="Input Transforms File Not Found"
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_face_overshoot_limits(self):
        if not self.controller.face_network:
            self.raise_warning('No Face Network detected. Unable to export multipliers')
            return
        if not self.controller.face_network.face_groups:
            self.raise_warning('No Face Network Groups detected. Unable toe export multipliers')
            return
        # Build the user_data folder if it doesn't exist
        if not os.path.exists(fut.get_userdata_build_directory()):
            os.makedirs(fut.get_userdata_build_directory())

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            file_name, types = QFileDialog.getSaveFileName(
                self,
                'Export Face Overshoot Multipliers',
                '%s/face_overshoot_multipliers.json' % fut.get_userdata_build_directory(),
                'Json (*.json)'
            )
        else:
            file_name = '%s/face_overshoot_multipliers.json' % fut.get_userdata_build_directory()
        if file_name:
            write_data(file_name, self.controller.face_network.get_overshoot_multiply_values())
            self.raise_warning(
                'Exported Face Overshoot Multipliers to:\n%s' % file_name.split('/')[-1],
                window_title='Export Successful!'
            )

    def import_face_overshoot_limits(self):
        if not self.controller.face_network:
            self.raise_warning('No Face Network detected. Unable to export face limit multipliers')
            return
        if not self.controller.face_network.face_groups:
            self.raise_warning('No Face Network Groups detected. Unable to export face limit multipliers')
            return

        # Old Location
        file_path = '%s/face_overshoot_multipliers.json' % env.local_build_directory
        if not os.path.exists(file_path):
            # New Location
            file_path = '%s/face_overshoot_multipliers.json' % fut.get_userdata_build_directory()

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            file_name, types = QFileDialog.getOpenFileName(
                self,
                'Import Face Overshoot Multipliers',
                file_path,
                'Json (*.json)'
            )
        else:
            file_name = file_path
            if not os.path.exists(file_name):
                self.raise_warning('File not found: %s' % file_name.split('/')[-1])
                return

        if file_name:
            try:
                with open(file_name, mode='r') as f:
                    data = json.load(f)
            except Exception as e:
                logging.getLogger('rig_build').error(traceback.format_exc())
                self.raise_warning('Unable to parse json: %s' % file_name)
                return

            try:
                self.controller.face_network.set_overshoot_multiply_values(data)
                self.raise_warning(
                    'Imported  Face Overshoot Multipliers from:\n%s' % file_name.split('/')[-1],
                    window_title='Success!'
                )
            except Exception as e:
                logging.getLogger('rig_build').error(traceback.format_exc())
                self.raise_warning('Unable to set overshoot multipliers. (See log for details)')
                return

    def export_handle_limits(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Limits',
                    '%s/handle_limits.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(
                        file_name,
                        self.controller.root.get_handle_limits()
                    )
                    self.notification_launcher.success_notification(
                        text="Exported Handle Limits Successfully"
                    )
            else:
                self.save_json_file(
                    name='handle_limits.json',
                    data=self.controller.root.get_handle_limits(),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Handle Limits Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_utility_geometry(self):
        if self.controller and self.controller.root:
            controller = self.controller

            # New Location
            userdata_directory = '%s/' % fut.get_userdata_build_directory()
            if not os.path.exists(userdata_directory):
                # Old Location
                userdata_directory = '%s/' % env.local_build_directory

            # Double check if path exists, build the folder if it doesn't exist
            if not os.path.exists(userdata_directory):
                os.makedirs(userdata_directory)

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                userdata_directory = '%s/' % QFileDialog.getExistingDirectory(
                    None,
                    "Export Utility Geometry to Selected Directory",
                    userdata_directory,
                    QFileDialog.ShowDirsOnly
                )

            util_geometry = self.controller.scene.ls('*Util_Geo', '*util_Geo')
            if bool(util_geometry):
                for geo in util_geometry:
                    root = self.controller.scene.listRelatives(geo, fullPath=True)
                    if root[0].find(
                            '|' + str(self.controller.root.geometry_group)) == -1:  # So it doesn't grab modelling ones.
                        try:
                            root = root[0].replace('|' + geo + 'Shape', '')
                            command = "-frameRange -uvWrite -writeUVSets -dataFormat ogawa -root %s -file %s%s.abc" % (
                            root, userdata_directory, geo)
                            self.controller.scene.AbcExport(command)
                            logging.getLogger('rig_build').info('Utility Geometry Exported < {} >'.format(geo))
                        except Exception as e:
                            logging.getLogger('rig_build').error(traceback.format_exc())
                            self.notification_launcher.error_notification(
                                text="Unable to Export Utility Geometry. (See log for details)"
                            )
                            return
                    else:
                        logging.getLogger('rig_build').info(geo + 'is in Geometry_Grp.')
                self.notification_launcher.success_notification(
                    text="Exported Utility Geometry Successfully"
                )
            else:
                self.notification_launcher.warning_notification(
                    text="No Utility Geometry found. Please make sure your mesh ends with '_Util_Geo'"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_handle_limits(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/handle_limits.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/handle_limits.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Limits',
                    file_path,
                    'Json (*.json)'
                )
            else:
                file_name = file_path
                if not os.path.exists(file_name):
                    self.notification_launcher.warning_notification(
                        text='File not found: %s' % file_name.split('/')[-1]
                    )
                    return
            if file_name:
                try:
                    with open(file_name, mode='r') as f:
                        data = json.load(f)
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    self.notification_launcher.warning_notification(
                        text="Unable to parse json data. (See log for details)"
                    )
                    return
                if data:
                    try:
                        self.controller.root.set_handle_limits(data)
                        self.notification_launcher.success_notification(
                            text="Imported Handle Limits Successfully"
                        )
                    except Exception as e:
                        logging.getLogger('rig_build').error(traceback.format_exc())
                        self.notification_launcher.warning_notification(
                            text="Unable to set limits data. (See log for details)"
                        )
                        return
                else:
                    self.notification_launcher.warning_notification(
                        text="Handle Limits Data not found"
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_shard_weights(self):
        if self.controller and self.controller.root:
            controller = self.controller

            skins_directory = '%s/shard_weights' % fut.get_userdata_build_directory()
            # Build the user_data/shard_weights folder if it doesn't exist
            if not os.path.exists(skins_directory):
                os.makedirs(skins_directory)

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                skins_directory = QFileDialog.getExistingDirectory(
                    None,
                    "Export Shard Weights to Directory",
                    '%s/shard_weights.json' % skins_directory,
                    QFileDialog.ShowDirsOnly
                )
            shards = sht.get_shard_mesh_nodes(*controller.root.get_parts())

            if not shards:
                self.notification_launcher.error_notification(
                    text="No Shards were found in the rig"
                )

                return

            if skins_directory:
                for shard in shards:
                    shard_name = shard.name
                    skin_cluster = controller.scene.find_skin_cluster(shard_name)
                    if skin_cluster:
                        self.save_json_file(
                            name='shard_weights/%s.json' % shard_name,
                            data=controller.scene.get_skin_data(skin_cluster),
                            location='user_data'
                        )
                        self.notification_launcher.success_notification(
                            text="Exported Shard Weights Successfully"
                        )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_shard_weights(self):
        if self.controller and self.controller.root:
            controller = self.controller
            # Old Location
            skins_directory = '%s/shard_weights' % env.local_build_directory
            if not os.path.exists(skins_directory):
                # New Location
                skins_directory = '%s/shard_weights' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            # skins_directory = '%s/shard_weights' % fut.get_userdata_build_directory()
            if modifiers == Qt.ShiftModifier:
                skins_directory = QFileDialog.getExistingDirectory(
                    None,
                    "Import Shard Weights from Selected Directory",
                    skins_directory,
                    QFileDialog.ShowDirsOnly
                )
                if not skins_directory:
                    return
            shards = sht.get_shard_mesh_nodes(*controller.root.get_parts())

            if not shards:
                self.raise_warning('No Shards found')
                return
            else:
                for shard in shards:
                    skin_m_object = controller.scene.find_skin_cluster(shard.name)
                    if skin_m_object:
                        controller.scene.skinCluster(
                            controller.scene.get_selection_string(skin_m_object),
                            e=True,
                            ub=True
                        )
            if skins_directory:
                for shard in shards:
                    skin_path = '%s/%s.json' % (skins_directory, shard.name)
                    with open(skin_path, mode='r') as f:
                        controller.scene.create_from_skin_data(json.loads(f.read()))
                        logging.getLogger('rig_build').info('Imported shard weight from: %s' % skin_path)
        else:
            self.notification_launcher.error_notification(
                text="No Rig is loaded"
            )

    def export_handle_spaces(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Spaces',
                    '%s/handle_spaces.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(file_name, self.controller.root.get_space_switcher_data())
                    self.notification_launcher.success_notification(
                        text="Exported Handle Spaces Successfully"
                    )
            else:
                self.save_json_file(
                    name='handle_spaces.json',
                    data=self.controller.root.get_space_switcher_data(),
                    location='user_build'
                )
                self.notification_launcher.success_notification(
                    text="Exported Handle Spaces Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_handle_spaces(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/handle_spaces.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/handle_spaces.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Spaces',
                    file_path,
                    'Json (*.json)'
                )
            else:
                file_name = file_path
                if not os.path.exists(file_name):
                    self.raise_warning('File not found: %s' % file_name.split('/')[-1])
                    return

            if file_name:
                if not os.path.exists(file_name):
                    self.raise_warning('File not found: %s' % file_name)
                    return
                with open(file_name, mode='r') as f:
                    try:
                        data = json.loads(f.read())
                    except Exception as e:
                        logging.getLogger('rig_build').error(traceback.format_exc())
                        self.notification_launcher.warning_notification(
                            text=('Unable to parse json data:\n%s' % os.path.basename(file_name))
                        )
                        return
                    try:
                        spu.set_space_switcher_data(data)
                    except Exception as e:
                        logging.getLogger('rig_build').error(traceback.format_exc())
                        self.notification_launcher.error_notification(
                            text="Failed to set space switcher data. (See log for details)"
                        )
                        return
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_handle_shapes(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Shapes',
                    '%s/handle_shapes.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(file_name, self.controller.get_handle_shapes(self.controller.root, local=True))
                    self.notification_launcher.success_notification(
                        text="Exported Handle Shapes Successfully"
                    )
            else:
                self.save_json_file(
                    name='handle_shapes.json',
                    data=self.controller.get_handle_shapes(self.controller.root, local=True),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Handle Shapes Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_handle_shapes(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/handle_shapes.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/handle_shapes.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Shapes',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.set_handle_shapes(
                            self.controller.root,
                            json.loads(f.read())
                        )
                    self.notification_launcher.success_notification(
                        text="Imported Handle Shapes Successfully"
                    )
            else:
                data = self.load_json_file('handle_shapes.json')
                if data:
                    self.controller.set_handle_shapes(
                        self.controller.root,
                        data
                    )
                    self.notification_launcher.success_notification(
                        text="Imported Handle Shapes Successfully"
                    )
                else:
                    self.notification_launcher.warning_notification(
                        text="Handle Shapes file not found"
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_all_handle_shapes(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export All Handle Shapes',
                    '%s/handle_shapes.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(file_name, self.controller.get_handle_shapes(self.controller.root, local=False))
                    self.notification_launcher.success_notification(
                        text="Exported All Handle Shapes successfully"
                    )
                else:
                    self.notification_launcher.warning_notification(
                        text="File Name was not set"
                    )
            else:
                self.save_json_file(
                    name='handle_shapes.json',
                    data=self.controller.get_handle_shapes(self.controller.root, local=False),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported All Handle Shapes successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def expand_handle_shapes(self):
        if self.controller and self.controller.root:
            self.set_widget_controllers_to_none()  # Turn off views because expanded handle shapes not part fo main rig
            self.handle_shapes_widget.cancel_button.setVisible(False)
            self.back_button.setVisible(False)
            self.handle_shapes_widget.finished_callback = self.collapse_handle_shapes
            self.handle_shapes_widget.canceled_callback = self.collapse_handle_shapes
            self.controller.root.expand_handle_shapes()
            self.stacked_layout.setCurrentIndex(2)

    def collapse_handle_shapes(self):
        self.handle_shapes_widget.cancel_button.setVisible(True)
        if self.controller and self.controller.root:
            self.controller.root.collapse_handle_shapes()
        self.reload_widget_state()

    def snap_handles_to_mesh_positons(self):
        if self.controller and self.controller.root:
            self.controller.root.snap_handles_to_mesh_positons()

    def mirror_all(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_all([self.controller.root], side='right')
        else:
            self.controller.mirror_all([self.controller.root])

    def mirror_handle_positions(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # run mirror twice as some guides have constraints and are moved to random places when their drivers move
            self.controller.mirror_handle_positions([self.controller.root], side='right')
            self.controller.mirror_handle_positions([self.controller.root], side='right')
        else:
            # run mirror twice as some guides have constraints and are moved to random places when their drivers move
            self.controller.mirror_handle_positions([self.controller.root])
            self.controller.mirror_handle_positions([self.controller.root])

    def mirror_handle_vertices(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_handle_vertices([self.controller.root], side='right')
        else:
            self.controller.mirror_handle_vertices([self.controller.root])

    def mirror_handle_attributes(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_handle_attributes([self.controller.root], side='right')
        else:
            self.controller.mirror_handle_attributes([self.controller.root])

    def transfer_handle_vertices(self):
        self.controller.transfer_handle_vertices_to_selected_mesh(self.controller.root)

    def export_handle_vertices(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Vertices',
                    '%s/handle_vertices.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(file_name, self.controller.root.get_handle_mesh_positions())
                    self.notification_launcher.success_notification(
                        text="Exported Handle Vertices Successfully"
                    )
            else:
                self.save_json_file(
                    name='handle_vertices.json',
                    data=self.controller.root.get_handle_mesh_positions(),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Handle Vertices Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_handle_vertices(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/handle_vertices.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/handle_vertices.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Vertices',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.set_handle_mesh_positions(json.loads(f.read()))
                    self.notification_launcher.success_notification(
                        text="Imported Handle Vertices Successfully"
                    )
            else:
                data = self.load_json_file('handle_vertices.json')
                if data is not None:
                    self.controller.root.set_handle_mesh_positions(data)
                    self.notification_launcher.success_notification(
                        text="Imported Handle Vertices Successfully"
                    )
                else:
                    self.notification_launcher.warning_notification(
                        text="Handle Vertices File not found"
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_custom_sdks(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Custom SDK\'s',
                    '%s/custom_sdks.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(
                        file_name,
                        self.controller.root.get_sdk_data()
                    )
                    self.notification_launcher.success_notification(
                        text="Exported Custom SDKs Successfully"
                    )
            else:
                self.save_json_file(
                    name='custom_sdks.json',
                    data=self.controller.root.get_sdk_data(),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Custom SDKs Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_custom_sdks(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/custom_sdks.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/custom_sdks.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Custom SDK\'s',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.set_sdk_data(
                            json.loads(f.read())
                        )
                    self.notification_launcher.success_notification(
                        text="Imported Custom SDKs Successfully"
                    )
            else:
                data = self.load_json_file('custom_sdks.json')
                if data:
                    self.controller.root.set_sdk_data(data)
                    self.notification_launcher.success_notification(
                        text="Imported Custom SDKs Successfully"
                    )
                else:
                    self.notification_launcher.warning_notification(
                        text="Custom SDKs file not found"
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def export_handle_positions(self):
        if self.controller and self.controller.root:
            # Build the user_data folder if it doesn't exist
            if not os.path.exists(fut.get_userdata_build_directory()):
                os.makedirs(fut.get_userdata_build_directory())

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Positions',
                    '%s/handle_positions.json' % fut.get_userdata_build_directory(),
                    'Json (*.json)'
                )
                if file_name:
                    write_data(
                        file_name,
                        self.controller.root.get_handle_positions()
                    )
                    self.notification_launcher.success_notification(
                        text="Exported Handle Positions Successfully"
                    )
            else:
                self.save_json_file(
                    name='handle_positions.json',
                    data=self.controller.root.get_handle_positions(),
                    location='user_data'
                )
                self.notification_launcher.success_notification(
                    text="Exported Handle Positions Successfully"
                )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def import_handle_positions(self):
        if self.controller and self.controller.root:
            # Old Location
            file_path = '%s/handle_positions.json' % env.local_build_directory
            if not os.path.exists(file_path):
                # New Location
                file_path = '%s/handle_positions.json' % fut.get_userdata_build_directory()

            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Positions',
                    file_path,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.set_handle_positions(
                            json.loads(f.read())
                        )
                    self.notification_launcher.success_notification(
                        text="Imported Handle Positions Successfully"
                    )
            else:
                data = self.load_json_file('handle_positions.json')
                if data:
                    self.controller.root.set_handle_positions(data)
                    self.notification_launcher.success_notification(
                        text="Imported Handle Positions Successfully"
                    )
                else:
                    self.notification_launcher.warning_notification(
                        text="Handle Positions File not found"
                    )
        else:
            self.notification_launcher.error_notification(
                text="No Rig found"
            )

    def save_json_file(self, name, data, location):
        logger = logging.getLogger('rig_build')

        # Selection the locatin where to put the file
        # If goes to build folder, else to build/user_data folder
        if location.lower() == 'build':
            data_path = '%s/%s' % (env.local_build_directory, name)
        else:
            data_path = '%s/%s' % (fut.get_userdata_build_directory(), name)

        data_directory = os.path.dirname(data_path)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        write_data(data_path, data)
        logger.info('Saved to : %s' % data_path)
        # self.raise_warning(
        #     'Saved %s To:\n%s' % (name.title(), data_path.split('/')[-1]),
        #     window_title='Success!'
        # )

    def load_json_file(self, name):
        logger = logging.getLogger('rig_build')
        data_path = '%s/%s' % (fut.get_userdata_build_directory(), name)
        if not os.path.exists(data_path):
            data_path = '%s/%s' % (env.local_build_directory, name)
        logger.info('loading from : %s' % data_path)
        if os.path.exists(data_path):
            with open(data_path, mode='r') as f:
                return json.loads(f.read())
        # self.raise_warning(
        #     'Loaded %s from:\n%s' % (name.title(), data_path.split('/')[-1]),
        #     window_title='Success!'
        # )

    def remove_vertex_association(self):
        controller = self.controller
        selection = controller.scene.ls(sl=True)

        for item in selection:
            object = self.controller.named_objects[item]
            if isinstance(object, GuideHandle):
                object.vertices = []
            else:
                handles = object.get_handles()
                for handle in handles:
                    handle.vertices = []


class MainWidget(QWidget):
    create_container_signal = Signal(obs.BaseObject)

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)
        self.controller = None
        self.title_label = QLabel(self)
        self.vertical_layout = QVBoxLayout(self)
        self.title_layout = QHBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.part_view = PartOwnerView(self)
        self.toggle_button = ToggleButton(self)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.toggle_button)
        self.vertical_layout.addLayout(self.title_layout)
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.part_view)
        self.vertical_layout.setSpacing(4)
        self.stacked_layout.setContentsMargins(4, 0, 0, 0)
        title_font = QFont('arial', 12, True)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)

        # Signals
        self.part_view.items_selected_signal.connect(self.select_items)

    def get_irig_version(self):
        if self.irig_combo_box.currentIndex() == 0:  # BETA
            return self.get_latest_irig('G:/Rigging/.rigging/testing/iRig')
        elif self.irig_combo_box.currentIndex() == 1:  # STABLE
            return self.get_latest_irig('//pipeline/packages/iRig')
        elif self.irig_combo_box.currentIndex() == 2:  # LOCAL DEV
            return None
        elif self.irig_combo_box.currentIndex() > 2:
            return self.irig_combo_box.currentText()

    def set_controller(self, controller):
        self.controller = controller
        self.part_view.set_controller(self.controller)
        self.update_widgets()

    def update_widgets(self):
        if self.controller:
            self.setEnabled(True)
            self.toggle_button.setVisible(False)
            self.stacked_layout.setCurrentIndex(1)
            if self.controller:
                self.stacked_layout.setCurrentIndex(0)
                self.toggle_button.setVisible(True)

    def select_items(self, items):
        if self.controller:
            self.controller.scene.select(
                [x.get_selection_string() for x in items if isinstance(x, obs.DependNode)]
            )


class NoControllerView(QWidget):

    def __init__(self, *args, **kwargs):
        super(NoControllerView, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.message_label = QLabel('No Controller Found.', self)
        message_font = QFont('', 13, True)
        message_font.setWeight(50)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        self.vertical_layout.addSpacing(80)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.message_label)
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))


def get_subclasses(*object_types):
    subclasses = []
    for object_type in object_types:
        subclasses.extend(object_type.__subclasses__())
        for sub_class in copy.copy(subclasses):
            subclasses.extend(get_subclasses(sub_class))
    return subclasses


def getMayaWindow():
    for obj in QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')