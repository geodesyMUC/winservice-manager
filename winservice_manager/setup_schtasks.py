"""
Functions to set up scheduled tasks
"""
import argparse
import subprocess
import os

# Local packages
from winservice_manager.utils import is_admin, log


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
        "/RU",
        os.getenv("USERNAME"),
        "/EC",
        "Application",
        "/MO",
        "*[System/EventID=999]",
        "/F",
    ]
    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as proc:
        stdout = proc.communicate()[0].decode()

    # German and english locale
    if ("ERFOLGREICH" in stdout) or ("SUCCESS" in stdout):
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
        os.getcwd(), "scripts", "start-service.ps1"
    ),
    path_stop_wservice_script: str = os.path.join(
        os.getcwd(), "scripts", "stop-service.ps1"
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
        "-".join(["START", args.service_name]),
        path_start_wservice_script,
    )
    create_scheduled_script_task(
        args.service_name,
        "-".join(["STOP", args.service_name]),
        path_stop_wservice_script,
    )

    log("Script finished")


if __name__ == "__main__":
    main()
