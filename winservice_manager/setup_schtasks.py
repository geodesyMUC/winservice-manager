"""
Functions to set up scheduled tasks
"""
import argparse
import subprocess
import os
from pathlib import Path

# Local packages
from winservice_manager.utils import is_admin, log


def _get_schtask_name(task: str, service: str) -> str:
    # Returns the formatted schtask name
    # task = a string describing the action (START, STOP, ...)
    return "-".join([task, service])


def create_scheduled_script_task(service_name: str, task_name: str, path: str) -> None:
    """
    Creates scheduled task with the input name,
    running a powershell script at the input path.

    Command: schtasks /create [...]

    Run "schtasks /create /?" for help.

    The created task runs ONEVENT, but with a dummy event.
    """
    task = f"PowerShell.exe -WindowStyle hidden -File {path} {service_name}"
    command = [
        "schtasks.exe",
        "/CREATE",
        "/SC",
        "ONEVENT",
        "/TN",
        f"{task_name}",
        "/TR",
        task,
        "/RL",
        "HIGHEST",
        "/EC",
        "Application",
        "/MO",
        "*[System/EventID=999]",
        "/F",
    ]

    # Add run as username to cmd (if possible)
    user = os.getenv("USERNAME")
    if user:
        command.insert(10, "/RU")
        command.insert(11, user)

    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as proc:
        stdout = proc.communicate()[0].decode()

    # English locale only
    if "SUCCESS" in stdout:
        log(f"Scheduled task '{task_name}' created successfully")
        return

    log(f"Scheduled task '{task_name}' could not be created")
    return


def arg_parser() -> argparse.ArgumentParser:
    """
    Argument parser for this script
    """
    parser = argparse.ArgumentParser(
        description="""
        Sets up scheduled tasks for the input service.
        Must be run with admin privileges.
        """
    )
    parser.add_argument("service_name", type=str, help="name of the service")
    return parser


def main(
    path_start_wservice_script: str = os.path.join(
        Path(__file__).parent, "scripts", "start-service.ps1"
    ),
    path_stop_wservice_script: str = os.path.join(
        Path(__file__).parent, "scripts", "stop-service.ps1"
    ),
) -> None:
    """
    Main function
    """

    # Parse the input arguments
    args = arg_parser().parse_args()

    if not is_admin():
        # Scheduled tasks can ONLY be created as admin
        log("Error: You must run this script as admin!")
        return

    create_scheduled_script_task(
        args.service_name,
        _get_schtask_name("START", args.service_name),
        path_start_wservice_script,
    )
    create_scheduled_script_task(
        args.service_name,
        _get_schtask_name("STOP", args.service_name),
        path_stop_wservice_script,
    )

    log("Script finished")


if __name__ == "__main__":
    main()
