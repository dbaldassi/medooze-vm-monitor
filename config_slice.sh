#!/bin/bash

set -e

sed -i s/$(cat config.json | grep medooze.scope | cut -d"\\" -f3)/$(find /sys/fs/cgroup/machine.slice/ -name "*medooze.scope" | cut -d"\\" -f2)/ config.json

cd "$(find /sys/fs/cgroup/machine.slice/ -name "*medooze.scope")"

sudo su -c "chmod 664 memory.max"
sudo su -c "chgrp tobias memory.max"

exit