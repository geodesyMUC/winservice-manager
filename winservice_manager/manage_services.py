"""
Manage Windows services by running scheduled tasks
"""
import argparse
import subprocess

# Local imports
from winservice_manager.setup_schtasks import _get_schtask_name
from winservice_manager.utils import log


def cmd_start_service() -> None:
    """
    Wrapper around start_service, parses command line arguments
    """
    args = arg_parser().parse_args()
    start_service(args.service_name)


def cmd_stop_service() -> None:
    """
    Wrapper around stop_service, parses command line arguments
    """
    args = arg_parser().parse_args()
    stop_service(args.service_name)


def start_service(service: str) -> None:
    """
    Starts a service by running the corresponding scheduled task
    """
    run_scheduled_task(_get_schtask_name("START", service))


def stop_service(service: str) -> None:
    """
    Stops a service by running the corresponding scheduled tasks
    """
    run_scheduled_task(_get_schtask_name("STOP", service))


def run_scheduled_task(name: str):
    """Runs the scheduled task with the input name"""
    try:
        res = subprocess.check_output(
            f"schtasks /run /tn {name}", stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as exc:
        # An error occurred, for example service does not exist
        log(exc.output.decode())
        raise exc
    else:
        log(res.decode())
        log("Schtask run successfully")


def arg_parser() -> argparse.ArgumentParser:
    """
    Argument parser for managing services
    """
    parser = argparse.ArgumentParser(
        description="Manage services (start, stop, restart)"
    )
    parser.add_argument("service_name", type=str, help="name of the service")
    return parser
