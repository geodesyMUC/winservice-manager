# winservice-manager

The `winservice-manager` project offers tools to start and stop Windows services. This is done by first setting up, and then running scheduled tasks. In this way, it is possible to bypass the User Account Control (UAC) prompt which would normally require manual user interaction. For more information on this workaround, see [here](https://pentestlab.blog/2017/05/03/uac-bypass-task-scheduler/).

## Installation

In order to use the scripts contained in this project, it is recommended to install them using [poetry](https://python-poetry.org/). If poetry is set up, install this package by running the following command from the project directory:

```console
poetry install
```

## Introduction

To start, restart, and stop Windows services, simple PowerShell commands such as `Start-Service` and `Stop-Service` can be used. However, they require elevated privileges, and granting them requires manual user interaction by clicking away the prompt. This makes it difficult to use them in automated scripts. The scripts contained in this project use scheduled tasks to bypass the necessity of having admin privileges each time starting, or stopping, Windows services. You can run them as simple commands.

Under the hood, the scripts in this project use the same PowerShell commands, executed via the scheduled tasks.

## Usage

Scripts in this project can be run using commands (entry points). You can run the commands implemented by using the poetry shell:

```console
poetry shell
```

and then typing your commands:

```console
<COMMAND>
```

Or you can run them in one go by using:

```console
poetry run <COMMAND>
```

Note that in both cases, the commands must be run from the project directory.


### Creating scheduled tasks

Use the command

```console
create-schtasks <TASK NAME> <SERVICE 1 NAME> <SERVICE 2 NAME> ...
```

in order to set up the required scheduled tasks for the services that are later to be managed. The `<TASK NAME>` is an arbitrary, descriptive name one gives to later run the scheduled task(s). The `<SERVICE NAME>` must match the Windows service name. It is possible to use wildcard characters: `Xbl*` will match all services starting with `Xbl`.

Security advice: Please make sure to only match the services you actually mean to match, and no other services by accident.

The `create-schtasks` command needs to be run only once, but **with elevated privileges!** After a successful run, the scheduled tasks created can be managed in the graphical UI of the Task Scheduler. They are named:

- `START-<TASK NAME>`
- `STOP-<TASK NAME>`

You can use

```console
create-schtasks -h
```

to learn more about the required input parameters of the command.

Example: Assume the goal is to manage the `Xbl*` services. The scheduled tasks are then created by

```console
create-schtasks xblsvc Xbl*
```

with `xblsvc` being a descriptive name that you can choose freely.

This command will set up two scheduled tasks, named `START-xblsvc` and `STOP-xblsvc`. They start, and stop, respectively, all services starting with `Xbl`. You can make sure which services would be matched in this example by running the following PowerShell command:

```powershell
Get-Service Xbl*
```

Note that this command will only work if you are using the english locale.

### Starting and stopping services

Once the scheduled tasks for managing the requested Windows service(s) are set up, you can start/stop those service(s) with the commands

```console
start-winservice <TASK NAME>

stop-winservice <TASK NAME>
```

The `<TASK NAME>` is the descriptive, arbitrary name given to the scheduled tasks when setting up the tasks with the `create-schtasks` command.

Note that **no** admin privileges are required for those commands.

When starting, or stopping, services, the script will wait 30 seconds for all matched services to reach the target status `running`, or `stopped`, respectively. If a certain service takes more time until it is expected to change its status, you can use the optional `--wait` argument to set a longer waiting time.

Example, continuing the `xblsvc` task previously created by `create-schtasks`:

```console
stop-winservice xblsvc
```

Get more information about available arguments using

```console
start-winservice -h
```

or

```console
stop-winservice -h
```

### Deleting the scheduled tasks

Deleting scheduled tasks that were set up by `create-schtasks` is possible, among other ways, via the Task Scheduler UI. It is not implemented in this project.

## Author

2022, geodesyMUC
