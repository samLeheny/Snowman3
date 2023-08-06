from Snowman3.utilities.PySignal import Signal


build_directory_changed = Signal()

part_owner_signals = dict(  # PartView
    start_set=Signal(),  # Before New Part
    start_remove=Signal(),  # Before Delete Part
    start_move=Signal(),  # Before Change Part Owner
    end_set=Signal(),  # After New Part
    end_remove=Signal(),  # After Delete Part
    end_move=Signal(),  # After Change Part Owner
)

part_hierarchy_signals = dict(  # Hierarchy View
    start_set=Signal(),  # Before New Part
    start_remove=Signal(),  # Before Delete Part
    start_move=Signal(),  # Before Change Hierarchy Parent
    end_set=Signal(),  # After New Part
    end_remove=Signal(),  # After Delete Part
    end_move=Signal(),  # After Change Hierarchy Parent
)

root_signals = dict(  # Hierarchy View
    start_change=Signal(),  # Before New/Delete Root
    end_change=Signal(),  # After New/Delete Root,
)

controller_signals = dict(  # Hierarchy View
    critical_error=Signal(),  # System breaking error
    reset=Signal()
)

maya_callback_signals = dict(
    pre_file_new_or_opened=Signal(),  # Hooks into mayas new scene callback
    selection_changed=Signal()  # Hooks into mayas selectionChanged callback
)

gui_signals = dict(
    reload_rig_builder=Signal(),  # Informs high level guis that the rig has changed in some way
    saved_time_signal=Signal(),  # Update gui with saved time
    info_notification=Signal(),  # Triggers Notification Widget to give a visual info (blue) message on the gui
    success_notification=Signal(),  # Triggers Notification Widget to give a visual success (green) message on the gui
    warning_notification=Signal(),  # Triggers Notification Widget to give a visual warning (orange) message on the gui
    error_notification=Signal(),  # Triggers Notification Widget to give a visual error (red) message on the gui
    party_notification=Signal()   # Triggers Notification Widget to give a visual party (pink) message on the gui
)
face_network_signals = dict(
    network_about_to_change=Signal(),
    network_finished_change=Signal(),
    group_start_ownership=Signal(),
    group_end_ownership=Signal(),
    group_start_disown=Signal(),
    group_end_disown=Signal(),
    corrective_start_ownership=Signal(),
    corrective_end_ownership=Signal(),
    corrective_start_disown=Signal(),
    corrective_end_disown=Signal(),
    item_changed=Signal()
)


def set_build_directory(current_build_directory):
    import Snowman3.rigger.rig_factory.environment as env  # Move env.current_build_directory to a separate module...
    env.local_build_directory = current_build_directory
    build_directory_changed.emit(current_build_directory)
