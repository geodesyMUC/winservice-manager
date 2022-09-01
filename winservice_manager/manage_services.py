"""
Manage Windows services by running scheduled tasks
"""
import argparse
import subprocess
from typing import List
import fnmatch
import time
import sys
import psutil

# Local imports
from winservice_manager.setup_schtasks import _get_schtask_name
from winservice_manager.utils import log


def check_for_service_status(
    service_name: str, status: str, max_wait: int = 30
) -> bool:
    """
    Waits until all services that match the service name have the target status
    """
    # The following statuses might not make sense to wait for:
    # "start_pending", "pause_pending", "continue_pending", "stop_pending"
    allowed_statuses = [
        "running",
        "paused",
        "stopped",
    ]

    # First check if the target status is allowed
    if status not in allowed_statuses:
        raise ValueError(
            f"Target service status {status} not in allowed values: {allowed_statuses}"
        )
    # Get the services of interest, and return if there aren't any
    services = get_matching_services(service_name)
    if not services:
        log(f"No matching service(s) '{service_name}' found to check", "error")
        return False

    # Initialise the list of services that are ok (have target status)
    services_ok: List[str] = []
    # and remember the number of services we need to monitor
    n_services = len(services)

    t_start = time.time()

    # As long as not ALL services have the target status
    while len(services_ok) < n_services:
        # To prevent an infinite loop if some service doesn't ever
        # reach the target status
        if time.time() > t_start + max_wait:
            log(
                f"Timeout while waiting for {services}"
                + f" to reach target status '{status}'",
                "error",
            )
            return False

        # Find out which services are already ok
        for service in services:
            if get_service_info(service, "status") == status:
                log(f"Service {service} {status}", "ok")
                # Add it to the list of services that are ok
                services_ok.append(service)
                continue

        # Remove ok services from monitor list
        for service_ok in services_ok:
            try:
                services.remove(service_ok)
            except ValueError:
                # Case when service was already removed
                pass

        # Wait 1 second
        time.sleep(1)

        waiting_time = round(t_start + max_wait - time.time())
        if len(services) != 0 and waiting_time % 5 == 0:
            # Only print this every 5s
            # and if there are still services that we are waiting for
            log(
                f"Waiting {round(t_start + max_wait - time.time())}s "
                + f"for {services} to reach '{status}'...",
                "info",
            )
            # Print the status of all services that still are monitored
            for service in services:
                log(f"{service} status {get_service_info(service, 'status')}", "info")

    log(f"All services {status}", "ok")
    return True


def cmd_start_service() -> None:
    """
    Wrapper around start_service, takes service name from command line arguments.

    Exits with exit code 1 if service was not started successfully.
    """
    args = arg_parser().parse_args()
    if not start_service(args.service_name, args.wait, args.quiet):
        sys.exit(1)


def cmd_stop_service() -> None:
    """
    Wrapper around stop_service, takes service name from command line arguments.

    Exits with exit code 1 if service was not stopped successfully.
    """
    args = arg_parser().parse_args()
    if not stop_service(args.service_name, args.wait, args.quiet):
        sys.exit(1)


def get_matching_services(service_name: str) -> List[str]:
    """
    Returns a list of service names that match the input service name
    plus the '*' wildcard character
    """
    matched_services = []
    for service in psutil.win_service_iter():  # type: ignore
        if not fnmatch.fnmatch(service.name(), f"{service_name}*"):
            continue
        # The service matches service name,
        # plus wildcard (Unix filename pattern matching)
        matched_services.append(service.name())

    return matched_services


def get_service_info(service_name: str, key: str) -> str:
    """
    Returns the value for the queried key
    from the Windows service instance
    """
    # Transform the WindowsService to a dict, then get the queried field
    # -> will raise exception if service or key doesn't exist
    return psutil.win_service_get(service_name).as_dict()[key]


def start_service(service: str, max_wait_seconds: int, quiet: bool = True) -> bool:
    """
    Starts a service by running the corresponding scheduled task.

    Returns True if successful, and False if service could not be started.
    """
    log(f"Starting service '{service}*'", "info", quiet)
    run_scheduled_task(_get_schtask_name("START", service))
    return check_for_service_status(service, "running", max_wait_seconds)


def stop_service(service: str, max_wait_seconds: int, quiet: bool = True) -> bool:
    """
    Stops a service by running the corresponding scheduled tasks.

    Returns True if successful, and False if service could not be stopped.
    """
    log(f"Stopping service '{service}*'", "info", quiet)
    run_scheduled_task(_get_schtask_name("STOP", service))
    return check_for_service_status(service, "stopped", max_wait_seconds)


def run_scheduled_task(name: str) -> None:
    """Runs the scheduled task with the input name"""
    try:
        subprocess.check_output(f"schtasks /run /tn {name}", stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        cmd_out = exc.output.decode()
        # Decide depending what's in the cmd output
        if "ERROR: The system cannot find the file specified" in cmd_out:
            # Schtasks does not exist, maybe it just hasn't been set up first
            msg = (
                f"The scheduled task '{name}' that handles the service "
                "must be set up first.\n"
                "                 "  # For correct intendation
                "Please refer to the README, "
                "or check the 'create-schtasks -h' command."
            )
            log(msg, "error")
            # Exit with error code in this case
            sys.exit(1)

        # Some other error, log everything and rethrow the exception
        log(f"{cmd_out}", "error")
        raise exc
    else:
        log("Scheduled task successfully executed", "ok")


def arg_parser() -> argparse.ArgumentParser:
    """
    Argument parser for managing services
    """
    parser = argparse.ArgumentParser(
        description="Manage services (start, stop, restart)"
    )
    parser.add_argument("service_name", type=str, help="name of the service")
    parser.add_argument(
        "-w",
        "--wait",
        type=int,
        help="wait x seconds for the service to be started/stopped",
        default=30,
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="suppress log messages"
    )
    return parser
