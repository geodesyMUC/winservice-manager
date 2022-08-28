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


def check_for_service_status(service_name, status: str, max_wait: int = 30) -> bool:
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
        log("No matching service(s) to check")
        return False

    # Initialise the list of services that are ok (have target status)
    services_ok: List[str] = []
    # and remember the number of services we need to monitor
    n_services = len(services)

    # Remember the current time
    t_start = time.time()

    # As long as not ALL services have the target status
    while len(services_ok) < n_services:
        # To prevent an infinite loop if some service doesn't ever
        # reach the target status
        if time.time() > t_start + max_wait:
            log(
                f"Error: Timeout while waiting for {services}"
                + f" to reach target status '{status}'"
            )
            return False

        # Find out which services are already ok
        for service in services:
            if get_service_info(service, "status") == status:
                log(f"Service {service} {status}")
                # Add it to the list of services that are ok
                services_ok.append(service)

        # Remove ok services
        for service_ok in services_ok:
            try:
                services.remove(service_ok)
            except ValueError:
                # Case when service was already removed
                pass

        # Wait 1 second before checking again
        time.sleep(1)

        waiting_time = round(t_start + max_wait - time.time())
        if len(services) != 0 and waiting_time % 5 == 0:
            # Only print this every 5s
            # and if there are still services that we are waiting for
            log(
                f"Waiting {round(t_start + max_wait - time.time())}s for {services} "
                + f"to reach '{status}'..."
            )

    log(f"All services {status}")
    return True


def cmd_start_service() -> None:
    """
    Wrapper around start_service, takes service name from command line arguments.

    Exits with exit code 1 if service was not started successfully.
    """
    args = arg_parser().parse_args()
    if not start_service(args.service_name):
        sys.exit(1)


def cmd_stop_service() -> None:
    """
    Wrapper around stop_service, takes service name from command line arguments.

    Exits with exit code 1 if service was not stopped successfully.
    """
    args = arg_parser().parse_args()
    if not stop_service(args.service_name):
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


def start_service(service: str) -> bool:
    """
    Starts a service by running the corresponding scheduled task.

    Returns True if successful, and False if service could not be started.
    """
    run_scheduled_task(_get_schtask_name("START", service))
    return check_for_service_status(service, "running")


def stop_service(service: str) -> bool:
    """
    Stops a service by running the corresponding scheduled tasks.

    Returns True if successful, and False if service could not be stopped.
    """
    run_scheduled_task(_get_schtask_name("STOP", service))
    return check_for_service_status(service, "stopped")


def run_scheduled_task(name: str) -> None:
    """Runs the scheduled task with the input name"""
    try:
        res = subprocess.check_output(
            f"schtasks /run /tn {name}", stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as exc:
        cmd_out = exc.output.decode()
        # Decide depending what's in the cmd output
        if "ERROR: The system cannot find the file specified" in cmd_out:
            # Schtasks does not exist, maybe it just hasn't been set up first
            msg = (
                f"Error: The scheduled task '{name}' that handles the service "
                "must be set up first.\n"
                "Please refer to the README, "
                "or check the 'create-schtasks -h' command."
            )
            log(msg)
            # Exit with error code in this case
            sys.exit(1)

        # Some other error, log everything and rethrow the exception
        log(cmd_out)
        raise exc
    else:
        log(res.decode())  # TODO remove output here
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
