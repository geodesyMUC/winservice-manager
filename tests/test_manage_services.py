"""
Test manage_services.py
"""
from typing import List
import pytest
from winservice_manager.manage_services import (
    _parse_service_from_schtasks_vquery,
    _is_task_not_exist_error,
)
from winservice_manager.setup_schtasks import _get_schtask_name


def test_is_task_not_exist_error() -> None:
    """
    Tests if the error message that is returned
    by schtasks query is parsed correctly
    """
    query_res = "ERROR: The system cannot find the file specified.\r\r\n"
    assert _is_task_not_exist_error(query_res) is True


def test_get_schtask_name() -> None:
    """Tests formatted schtasks name assembler"""
    assert _get_schtask_name("STOP", "svc") == "STOP-svc"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            # In the 11th line there's the task to run
            "Test Line\r\n" * 10
            + "Task To Run:  PowerShell.exe -WindowStyle hidden "
            + "-File start-service.ps1 Xbl*\r\n",
            ["Xbl*"],
        ),
        (
            "Test Line\r\n" * 10
            + "Task To Run:  PowerShell.exe -WindowStyle hidden "
            + "-File start-service.ps1 X1 X2*\r\n",
            ["X1", "X2*"],
        ),
    ],
)
def test_parse_service_from_schtasks_vquery(
    test_input: str, expected: List[str]
) -> None:
    """Tests parsing the service name from a verbose schtasks query result"""
    assert _parse_service_from_schtasks_vquery(test_input) == expected
