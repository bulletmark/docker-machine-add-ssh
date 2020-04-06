#!/usr/bin/python3
'''
Adds docker-machine ssh configuration to your personal ssh
configuration. Normally, you ssh to a docker-machine using command
"docker-machine ssh <mach>" but after running this utility once for the
specified machine, you can then on use ssh in the normal way, e.g. "ssh
<mach>". Other standard programs such as scp, sftp, rsync, and anything
else that relies on them or normal ssh can then also be used to that
docker-machine.
'''
# Author: Mark Blakeney, Apr 2020.

import os
import sys
import argparse
import string
import re
import shutil
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime
from functools import partial
from urllib.parse import urlparse

SSHFILE = Path('~/.ssh/config').expanduser()
MACHDIR = Path('~/.docker/machine/machines').expanduser()
CNFDIR = Path('~/.config').expanduser()

# The template for the new host entry we write
TEMPLATE = '''
Host $host
    # This $host entry added by $progname at $datetime
    Hostname $ipaddr
    IdentityFile $idfile
    User docker
'''

NOSTRICT = '''
    StrictHostKeyChecking no
'''

def getparams_cmd(tpl: dict, host: str) -> None:
    'Run docker-machine to get this hosts parameters'
    try:
        res = subprocess.run(f'docker-machine env {host}'.split(),
                capture_output=True, universal_newlines=True)
    except Exception:
        sys.exit('docker-machine is not installed.')

    if res.returncode != 0:
        sys.exit('docker-machine error:\n' + res.stderr.strip())

    # Extract the host's docker-machine specific template values
    for line in res.stdout.splitlines():
        if 'DOCKER_HOST=' in line:
            tpl['ipaddr'] = urlparse(line.split('"')[1]).hostname
        elif 'DOCKER_CERT_PATH=' in line:
            tpl['idfile'] = line.split('"')[1] + '/id_rsa'

    if 'ipaddr' not in tpl or 'idfile' not in tpl:
        sys.exit('Could not determine DOCKER_HOST and/or DOCKER_CERT_PATH')

def getparams_files(tpl: dict, host: str) -> None:
    'Get parameters directly from docker-machine files'
    conf = MACHDIR / host / 'config.json'
    if not conf.exists():
        sys.exit(f'No docker machine "{host}" exists.')

    with conf.open() as fp:
        data = json.load(fp)

    data = data.get('Driver', {})
    for key, keyval in ('ipaddr', 'IPAddress'), ('idfile', 'SSHKeyPath'):
        tpl[key] = data.get(keyval)
        if not tpl[key]:
            sys.exit(f'{keyval} not available for docker machine {host}.')

def main() -> None:
    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__.strip())
    opt.add_argument('-r', '--replace', action='store_true',
            help='do not fail if host entry already exists, just replace it')
    opt.add_argument('-d', '--delete', action='store_true',
            help='just delete any existing host entry')
    opt.add_argument('-f', '--files', action='store_true',
            help='get parameters directly from files rather than via '
            'docker-machine command')
    opt.add_argument('-B', '--nobackup', action='store_true',
            help='do not create a backup file')
    opt.add_argument('-S', '--nostrict', action='store_true',
            help='disable strict host key check')
    opt.add_argument('name',
            help='docker machine name')

    # Merge in default args from user config file. Then parse the
    # command line.
    cnffile = CNFDIR / (opt.prog + '-flags.conf')
    cnfargs = shlex.split(cnffile.read_text().strip()) \
            if cnffile.exists() else []
    args = opt.parse_args(cnfargs + sys.argv[1:])
    host = args.name

    # Get this host's parameters
    if not args.delete:
        # Set up dict for filling template
        tpl = {'host': host, 'progname': opt.prog, 'datetime':
                datetime.now().isoformat(sep=' ', timespec='seconds')}
        getparams_files(tpl, host) if args.files else getparams_cmd(tpl, host)

    # Iterate over ssh config file to search for existing entry and to find
    # insertion point
    newlines = []
    insert = 0
    found = False
    exists = SSHFILE.exists()
    if exists:
        strip = False
        with SSHFILE.open() as fp:
            for line in fp:
                if re.match(r'^Host\s+' + host + r'\s*$', line):
                    found = True
                    if not args.replace and not args.delete:
                        sys.exit(f'{host} already exists in {SSHFILE}. '
                        '\nManually check and delete it, '
                        'or just replace it using \'-r\'.')
                    strip = True
                else:
                    if re.match(r'^Host\s+', line):
                        insert = len(newlines)
                        strip = False

                    if not strip:
                        newlines.append(line.rstrip())

    if args.delete:
        if not found:
            sys.exit(f'{host} entry not found in {SSHFILE}.')
        action = 'deleted from'
    else:
        # Create the new inserted lines
        template = TEMPLATE.lstrip('\n')
        if args.nostrict:
            template += NOSTRICT.lstrip('\n')

        lines = string.Template(template).substitute(tpl).splitlines()
        if newlines:
            lines.append('')

        newlines = newlines[:insert] + lines + newlines[insert:]
        action = 'replaced in' if found else 'added to'

    # Make a backup file
    if exists and not args.nobackup:
        shutil.copy2(SSHFILE, SSHFILE.with_name(SSHFILE.name + '.save'))

    # Write the new file
    SSHFILE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if newlines:
        with open(SSHFILE, 'w', opener=partial(os.open, mode=0o600)) as fp:
            fp.write('\n'.join(newlines) + '\n')
    else:
        SSHFILE.unlink()

    print(f'{host} entry {action} {SSHFILE}.')

if __name__ == '__main__':
    main()
