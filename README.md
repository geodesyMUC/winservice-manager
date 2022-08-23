# winservice-manager

This project offers tools and scripts to manage Windows services.

## Installation

In order to use the scripts contained in this project, first install it with poetry. Change to the project directory, and run

```console
poetry install
```

You can run the poetry commands either by using the poetry shell

```console
poetry shell
```

and then typing the command, or by using

```console
poetry run COMMAND
```

directly from the project directory.


## Introduction

To start, restart, and stop Windows services, simple PowerShell commands such as `Start-Service` and `Stop-Service` can be used. However, they require elevated privileges, making it for example difficult to use them in automated scripts. The scripts contained in this project use scheduled tasks to bypass the necessity of having admin privileges each time starting, restarting, or stopping a Windows service.

## Usage

Use the command

```console
create-schtasks <SERVICE NAME>
```

in order to set up the scheduled tasks for the requested service, identified by its name. This command must be run only once, but **with elevated privileges**. The tasks created can later be managed via the graphical UI of the Task Scheduler.

You can use

```console
create-schtasks -h
```

to learn more about the required input parameters of the command.

Note that the "`*`" wildcard character is appended to the input service name.  In this way, it is possible to match multiple services at once by not using a complete service name.

### Start and stop services

Once the scheduled tasks are set up, you can start/stop the Windows service with the following commands:

```console
start-winservice <SERVICE NAME>

stop-winservice <SERVICE NAME>
```

## Author

2022, geodesyMUC