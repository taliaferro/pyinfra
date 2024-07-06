"""
Manager Docker Containers, Volumes and Networks
"""

from pyinfra import host
from pyinfra.api import operation
from pyinfra.facts.docker import DockerContainers, DockerNetworks, DockerVolumes

from .util.docker import handle_docker


@operation()
def container(
    container,
    image="",
    ports=None,
    networks=None,
    volumes=None,
    env_vars=None,
    pull_always=False,
    present=True,
    force=False,
    start=True,
):
    """
    Manage Docker containers

    + container: name to identify the container
    + image: container image and tag ex: nginx:alpine
    + networks: network list to attach on container
    + ports: port list to expose
    + volumes: volume list to map on container
    + env_vars: environment varible list to inject on container
    + pull_always: force image pull
    + force: remove a contaner with same name and create a new one
    + present: whether the container should be up and running
    + start: start or stop the container

    **Examples:**

    .. code:: python

        # Run a container
        docker.container(
            name="Deploy Nginx container",
            container="nginx",
            image="nginx:alpine",
            ports=["80:80"],
            present=True,
            force=True,
            networks=["proxy", "services"],
            volumes=["nginx_data:/usr/share/nginx/html"],
            pull_always=True,
        )

        # Stop a container
        docker.container(
            name="Stop Nginx container",
            container="nginx",
            start=False,
        )

        # Start a container
        docker.container(
            name="Start Nginx container",
            container="nginx",
            start=True,
        )
    """

    existent_container = [c for c in host.get_fact(DockerContainers) if container in c["Name"]]

    if force:
        if existent_container:
            yield handle_docker(
                resource="container",
                command="remove",
                container=container,
            )

    if present:
        if not existent_container or force:
            yield handle_docker(
                resource="container",
                command="create",
                container=container,
                image=image,
                ports=ports,
                networks=networks,
                volumes=volumes,
                env_vars=env_vars,
                pull_always=pull_always,
                present=present,
                force=force,
                start=start,
            )

    if existent_container and start:
        if existent_container[0]["State"]["Status"] != "running":
            yield handle_docker(
                resource="container",
                command="start",
                container=container,
            )

    if existent_container and not start:
        if existent_container[0]["State"]["Status"] == "running":
            yield handle_docker(
                resource="container",
                command="stop",
                container=container,
            )

    if existent_container and not present:
        yield handle_docker(
            resource="container",
            command="remove",
            container=container,
        )


@operation(is_idempotent=False)
def image(image, present=True):
    """
    Manage Docker images

    + image: Image and tag ex: nginx:alpine
    + present: whether the Docker image should be exist

    **Examples:**

    .. code:: python

        # Pull a Docker image
        docker.image(
            name="Pull nginx image",
            image="nginx:alpine",
            present=True,
        )

        # Remove a Docker image
        docker.image(
            name="Remove nginx image",
            image:"nginx:image",
            present=False,
        )
    """

    if present:
        yield handle_docker(
            resource="image",
            command="pull",
            image=image,
        )

    else:
        yield handle_docker(
            resource="image",
            command="remove",
            image=image,
        )


@operation()
def volume(volume, driver="", labels=None, present=True):
    """
    Manage Docker volumes

    + volume: Volume name
    + driver: Docker volume storage driver
    + labels: Label list to attach in the volume
    + present: whether the Docker volume should exist

    **Examples:**

    .. code:: python

        # Create a Docker volume
        docker.volume(
            name="Create nginx volume",
            volume="nginx_data",
            present=True
        )
    """

    existent_volume = [v for v in host.get_fact(DockerVolumes) if v["Name"] == volume]

    if present:

        if existent_volume:
            host.noop("Volume alredy exist!")
            return

        yield handle_docker(
            resource="volume",
            command="create",
            volume=volume,
            driver=driver,
            labels=labels,
            present=present,
        )

    else:
        if existent_volume is None:
            host.noop("There is no {0} volume!".format(volume))
            return

        yield handle_docker(
            resource="volume",
            command="remove",
            volume=volume,
        )


@operation()
def network(
    network,
    driver="",
    gateway="",
    ip_range="",
    ipam_driver="",
    subnet="",
    scope="",
    opts=None,
    ipam_opts=None,
    labels=None,
    ingress=False,
    attachable=False,
    present=True,
):
    """
    Manage docker networks

    + network_name: Image name
    + driver: Container image and tag ex: nginx:alpine
    + gateway: IPv4 or IPv6 Gateway for the master subnet
    + ip_range: Allocate container ip from a sub-range
    + ipam_driver: IP Address Management Driver
    + subnet: Subnet in CIDR format that represents a network segment
    + scope: Control the network's scope
    + opts: Set driver specific options
    + ipam_opts: Set IPAM driver specific options
    + labels: Label list to attach in the network
    + ingress: Create swarm routing-mesh network
    + attachable: Enable manual container attachment
    + present: whether the Docker network should exist

    **Examples:**

    .. code:: python

        # Create Docker network
        docker.network(
            name="Create nginx network",
            network_name="nginx",
            attachable=True,
            present=True,
        )
    """
    existent_network = [n for n in host.get_fact(DockerNetworks) if n["Name"] == network]

    if present:
        if existent_network:
            host.noop("Alredy exist a network with {0} name!".format(network))
            return

        yield handle_docker(
            resource="network",
            command="create",
            network=network,
            driver=driver,
            gateway=gateway,
            ip_range=ip_range,
            ipam_driver=ipam_driver,
            subnet=subnet,
            scope=scope,
            opts=opts,
            ipam_opts=ipam_opts,
            labels=labels,
            ingress=ingress,
            attachable=attachable,
            present=present,
        )

    else:
        if existent_network is None:
            host.noop("Ther is not network with {0} name!".format(network))
            return

        yield handle_docker(
            resource="network",
            command="create",
            network=network,
        )


@operation(is_idempotent=False)
def prune(
    all=False,
    volume=False,
    filter="",
):
    """
    Execute a docker system prune.

    + all: Remove all unused images not just dangling ones
    + volumes: Prune anonymous volumes
    + filter: Provide filter values (e.g. "label=<key>=<value>" or "until=24h")

    **Examples:**

    .. code:: python

        # Remove dangling images
        docker.prune(
            name="remove dangling images",
        )

        # Remove all images and volumes
        docker.prune(
            name="Remove all images and volumes",
            all=True,
            volumes=True,
        )

        # Remove images older than 90 days
        docker.prune(
            name="Remove unused older than 90 days",
            filter="until=2160h"
        )
    """

    yield handle_docker(
        resource="system",
        command="prune",
        all=all,
        volume=volume,
        filter=filter,
    )
