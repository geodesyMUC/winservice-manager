import os
from winservice_manager.setup_schtasks import create_schtask_cmd


def test_create_schtask_cmd() -> None:
    """
    Test setting up the command for schtask creation
    """
    svc_name = ["dummy-svc1", "dummy-svc2"]
    task_name = "dummy-task"
    script_path = "dummy-script"
    expected_task = (
        f"PowerShell.exe -WindowStyle hidden -File {script_path} {' '.join(svc_name)}"
    )

    cmd = create_schtask_cmd(svc_name, task_name, script_path)

    username = os.getenv("USERNAME")
    # The create_schtask_cmd input is expected at certain positions in the command
    if username:
        # Also test for the username
        assert (cmd[5], cmd[7], cmd[11]) == (task_name, expected_task, username)
    # Test for task name, and task
    assert (cmd[5], cmd[7]) == (task_name, expected_task)
