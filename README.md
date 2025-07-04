## DOCKER-MACHINE ADD SSH
[![PyPi](https://img.shields.io/pypi/v/docker-machine-add-ssh)](https://pypi.org/project/docker-machine-add-ssh/)
[![AUR](https://img.shields.io/aur/version/docker-machine-add-ssh)](https://aur.archlinux.org/packages/docker-machine-add-ssh/)

This is a command line program to allow you to use ordinary
[ssh](https://en.wikipedia.org/wiki/Secure_Shell) commands with [Docker
Machine](https://github.com/docker/machine) rather than use
[`docker-machine ssh`](https://docs.docker.com/machine/reference/ssh/)
or [`docker-machine
scp`](https://docs.docker.com/machine/reference/scp/).

## USAGE

Type `docker-machine-add-ssh -h` to view the usage summary:

```
usage: docker-machine-add-ssh [-h] [-r] [-d] [-f] [-B] [-S] name

Adds docker-machine ssh configuration to your personal ssh configuration.
Normally, you ssh to a docker-machine using command "docker-machine ssh
<mach>" but after running this utility once for the specified machine, you can
then on use ssh in the normal way, e.g. "ssh <mach>". Other standard programs
such as scp, sftp, rsync, and anything else that relies on them or normal ssh
can then also be used to that docker-machine.

positional arguments:
  name            docker machine name

options:
  -h, --help      show this help message and exit
  -r, --replace   do not fail if host entry already exists, just replace it
  -d, --delete    just delete any existing host entry
  -f, --files     get parameters directly from files rather than via docker-
                  machine command
  -B, --nobackup  do not create a backup file
  -S, --nostrict  disable strict host key check

Note you can set default starting options in ~/.config/docker_machine_add_ssh-
flags.conf.
```

## EXAMPLES

```sh
$ tree foodir
foodir
├── a
└── b

# Create a docker machine:
$ docker-machine create vb1
...

# Login to that machine:
$ docker-machine ssh vb1
...
exit

# Copy a directory and it's files to the new machine the docker-machine way:
$ docker-machine scp -r foodir vb1:
b             100$    0     0.0KB/s   00:00
a             100%    0     0.0KB/s   00:00

# Or, use docker-machine rsync mode:
$ docker-machine scp -r -d foodir vb1:
sending incremental file list
foodir/a
              0 100%    0.00kB/s    0:00:00 (xfr#1, to-chk=1/3)
foodir/b
              0 100%    0.00kB/s    0:00:00 (xfr#2, to-chk=0/3)

# Instead, do all this normally, after executing docker-machine-add-ssh:
$ docker-machine-add-ssh vb1
vb1 entry added to /home/mark/.ssh/config.

# Login to that machine normally. Be sure to do this first time to clear
# the host check as seen in this example:
$ ssh vb1
The authenticity of host '192.168.99.100 (192.168.99.100)' can't be established.
ECDSA key fingerprint is SHA256:Gya8jUcRhXlO/IkkTicrbLEPmMV0V5uOALB2Y5kJUCc.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.99.107' (ECDSA) to the list of known hosts.

docker@vb1:~$ exit

# Now you can just use normal scp or rsync:
$ scp -pr foodir vb1:
b             100%    0     0.0KB/s   00:00    
a             100%    0     0.0KB/s   00:00 

$ rsync -av foodir vb1:
sending incremental file list

sent 100 bytes  received 17 bytes  234.00 bytes/sec
total size is 0  speedup is 0.00

# Finished with the machine so delete all trace of it:
$ docker-machine rm vb1
About to remove vb1
WARNING: This action will delete both local reference and remote instance.
Are you sure? (y/n): y
Successfully removed vb1

$ docker-machine-add-ssh -d vb1
vb1 entry deleted from /home/mark/.ssh/config.
```

## DEFAULT OPTIONS

You can add default options to a personal configuration file
`~/.config/docker-machine-add-ssh-flags.conf`. If that file exists then
each line of arguments will be concatenated and automatically prepended
to your `docker-machine-add-ssh` command line options. Comments in the
file (i.e. starting with "#") are ignored.

This allow you to set default preferred starting options to
`docker-machine-add-ssh`. Type `docker-machine-add-ssh -h` to see the
options supported.
E.g. `echo "-r" >~/.config/docker-machine-add-ssh-flags.conf` to make
`docker-machine-add-ssh` always replace existing host entries even if
they already exist.

## INSTALLATION

Python 3.7 or later is required. Ensure
[`docker-machine`](https://docs.docker.com/machine/install-machine) is
installed.

Arch users can install [docker-machine-add-ssh from the
AUR](https://aur.archlinux.org/packages/docker-machine-add-ssh/).

Note [docker-machine-add-ssh is on
PyPI](https://pypi.org/project/docker-machine-add-ssh/) so the easiest
way to install it is to use [`uv tool`][uvtool] (or [`pipx`][pipx] or
[`pipxu`][pipxu]).

```sh
$ uv tool install docker-machine-add-ssh
```

To upgrade:

```sh
$ uv tool upgrade docker-machine-add-ssh
```

To uninstall:

```sh
$ uv tool uninstall docker-machine-add-ssh
```

[pipx]: https://github.com/pypa/pipx
[pipxu]: https://github.com/bulletmark/pipxu
[uvtool]: https://docs.astral.sh/uv/guides/tools/#installing-tools

## LICENSE

Copyright (C) 2020 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.
