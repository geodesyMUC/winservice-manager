"""
Functions to set up scheduled tasks
"""
import argparse
import subprocess
import os
import logging
from pathlib import Path
from typing import List

# Local packages
from winservice_manager.utils import (
    is_admin,
    setup_script_logger,
    WinServiceManagerError,
)

logger = logging.getLogger(__name__)


def _get_schtask_name(task: str, service: str) -> str:
    # Returns the formatted schtask name
    # task = a string describing the action (START, STOP, ...)
    return "-".join([task, service])


def create_schtask(
    service_names: List[str], task_name: str, path: str, task_name_prefix: str = ""
) -> None:
    """
    Creates scheduled task to start input service(s) by running
    the PowerShell script at the input location.
    The scheduled task will be named using a prefix, and the input task name.
    """
    command = create_schtask_cmd(
        service_names,
        _get_schtask_name(task_name_prefix, task_name),
        path,
    )
    if not _run_schtask_create_cmd(command):
        logger.error("Scheduled task '%s' could not be created", task_name)
        raise WinServiceManagerError("Could not create scheduled task.")
    logger.info("Scheduled task '%s' created successfully", task_name)


def create_schtask_cmd(
    service_names: List[str], task_name: str, path: str
) -> List[str]:
    """
    Sets up the command to create a scheduled task. The command
    will be returned as a list of strings, which works best for
    subprocess.Popen().

    Command: schtasks /create [...]

    Run "schtasks /create /?" for help.

    The created task runs ONEVENT, but with a dummy event.
    """
    joined_service_names = " ".join(service_names)
    task = f"PowerShell.exe -WindowStyle hidden -File {path} {joined_service_names}"
    command = [
        "schtasks.exe",
        "/CREATE",
        "/SC",
        "ONEVENT",
        "/TN",
        task_name,
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

    # Add run as username to cmd (if username env variable exists)
    user = os.getenv("USERNAME")
    if user:
        command.insert(10, "/RU")
        command.insert(11, user)
    return command


def _run_schtask_create_cmd(command: List[str]) -> bool:
    # Run the command to create a scheduled task
    with subprocess.Popen(command, stdout=subprocess.PIPE) as proc:
        stdout = proc.communicate()[0].decode()

    # Looking for this string only works with english locale!
    # Other locales will not be recognized as successful
    if "SUCCESS" in stdout:
        return True

    # Schtasks could not be created
    logger.debug("Schtasks create command '%s'", " ".join(command))
    return False


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
    parser.add_argument("task_name", type=str, help="identifier for the task")
    parser.add_argument(
        "service_names",
        type=str,
        help="name of service(s) managed by the task",
        nargs="+",
    )
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
    setup_script_logger(__name__)

    # Parse the input arguments
    args = arg_parser().parse_args()
    logger.debug("Creating scheduled tasks for services %s", args.service_names)

    if not is_admin():
        # Scheduled tasks can ONLY be created as admin
        logger.error("You must run this as admin!")
        return

    # Scheduled task to START services
    create_schtask(
        args.service_names, args.task_name, path_start_wservice_script, "START"
    )
    # Scheduled task to STOP services
    create_schtask(
        args.service_names, args.task_name, path_stop_wservice_script, "STOP"
    )
    # Done!
    logger.info("Scheduled tasks created")


if __name__ == "__main__":
    main()
