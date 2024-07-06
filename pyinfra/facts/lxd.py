from __future__ import annotations

import json

from pyinfra.api import FactBase


class LxdContainers(FactBase):
    """
    Returns a list of running LXD containers
    """

    command = "lxc list --format json --fast"
    requires_command = "lxc"

    default = list

    def process(self, output):
        assert len(output) == 1
        return json.loads(output[0])
