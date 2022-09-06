# winservice-manager

The `winservice-manager` project offers tools and scripts to both start and stop Windows services. This is done by creating, and running scheduled tasks to bypass the User Account Control (UAC) prompt. In this way, it is possible to bypass the prompt that requires manual user interaction, and start/stop Windows services in other automated tasks.

## Installation

In order to use the scripts contained in this project, first install it with poetry. You can do this by setting the working directory in the standard terminal or PowerShell to this projects directory, and then run

```console
poetry install
```

## Introduction

To start, restart, and stop Windows services, simple PowerShell commands such as `Start-Service` and `Stop-Service` can be used. However, they require elevated privileges, making it for example difficult to use them in automated scripts. The scripts contained in this project use scheduled tasks to bypass the necessity of having admin privileges each time starting, restarting, or stopping a Windows service.

## Usage

Scripts in this project can be run using commands. You can run the commands implemented by using the poetry shell

```console
poetry shell
```

and then typing your commands

```console
<COMMAND>
```

Or you can run them directly by using

```console
poetry run <COMMAND>
```

Note that in both cases, this must be done from inside the project directory.


### Setting up scheduled tasks

Use the command

```console
create-schtasks <SERVICE NAME>
```

in order to set up the scheduled tasks for the requested service, identified by its name. This command needs to be run only once, but **with elevated privileges**. The tasks created by it can later be managed via the graphical UI of the Task Scheduler.

You can use

```console
create-schtasks -h
```

to learn more about the required input parameters of the command.

Note that the "`*`" wildcard character is appended to the input service name **automatically**.  In this way, it is possible to match multiple services at once by not using a complete service name. As an example, assume the goal is to manage the `Xbl*` services. First, the scheduled tasks are created with

```console
create-schtasks Xbl
```

This command will set up the scheduled tasks that start, or stop, respectively, all services starting with `Xbl`. You can make sure which services would be matched in this example by running the following PowerShell command:

```powershell
Get-Service Xbl*
```

### Starting and stopping services

Once the scheduled tasks for managing the requested Windows service are set up, you can start/stop the service with commands

```console
start-winservice <SERVICE NAME>

stop-winservice <SERVICE NAME>
```

Note that admin privileges are not required for those commands.

If a certain service takes more time until it is eventually running or stopped, you can use the optional `--wait` argument to set a longer waiting time. The default waiting time is 30 seconds.

Get more information about available arguments using

```console
start-winservice -h
```

### Deleting the scheduled tasks

Deleting scheduled tasks that were set up by `create-schtasks` is possible via the Task Scheduler UI. It is not implemented in this package.

## Author

2022, geodesyMUC