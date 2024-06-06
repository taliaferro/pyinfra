"""
Manage ZFS filesystems.
"""

from pyinfra.api import FactBase


class _ZFSResourceBase(FactBase):
    default = dict

    @staticmethod
    def process(output):
        datasets = {}
        for line in output:
            dataset, property, value, source = tuple(line.split("\t"))
            if dataset not in datasets:
                datasets[dataset] = {}
            datasets[dataset][property] = value
        return datasets


class Pools(_ZFSResourceBase):
    command = "zpool get -H all"

class Datasets(_ZFSResourceBase):
    command = "zfs get -H all"

class Filesystems(_ZFSResourceBase):
    command = "zfs get -t filesystem -H all"


class Snapshots(_ZFSResourceBase):
    command = "zfs get -t snapshot -H all"


class Volumes(_ZFSResourceBase):
    command = "zfs get -t volume -H all"
