import uuid as unique_id
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.temp_directory as tmpdr


def generate_temp_build_script(
        script,
        publish=False,
        save=False,
        work_directory=False,
        comment=None,
        suppress_popups=False,
        standalone=False,
        uuid=None
):
    if uuid is None:
        uuid = str(unique_id.uuid4())
    python_script_path = '%s/%s.py' % (tmpdr.get_temp_directory('launch_scripts'), uuid)
    code_lines = [
        'import os',
        'import sys',
        'import maya.standalone',
        'import batch.utilities.build_and_save as bas',
        'import batch.utilities.project_setup as pup',
        'pup.setup_project_paths()'
    ]

    if standalone:
        code_lines.append('maya.standalone.initialize(name="python")')

    main_line = "bas.build_and_save({script}, publish={publish}, save={save}, work_directory={work_directory}, " \
                "comment={comment}, suppress_popups={suppress_popups}, uuid='{uuid}')"
    code_lines.append(
        main_line.format(
            script=None if not script else "'%s'" % script,
            publish=publish,
            save=save,
            work_directory=work_directory,
            comment=None if not comment else "'%s'" % comment,
            suppress_popups=suppress_popups,
            uuid=uuid
        )
    )

    with open(python_script_path, mode='w') as f:
        f.write('\n'.join(code_lines))

    return python_script_path
