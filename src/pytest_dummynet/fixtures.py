import pytest
import pytest_dummynet
import logging
import docker


@pytest.fixture(scope="session")
def dummynet():
    """Creates the py.test fixture to make it usable within the unit-tests.
    See the DummyNet class for information"""

    log = logging.getLogger("client")

    shell = pytest_dummynet.Shell(log=log, sudo=False)

    return pytest_dummynet.DummyNet(shell=shell)


@pytest.fixture(scope="session")
def dummynet_docker(docker_image_id):
    """
    Similar to the dummynet fixture, but this one will run all commands in a
    docker container.
    """

    client = docker.from_env()
    log = logging.getLogger("client")
    shell = pytest_dummynet.DockerShell(
        client=client, log=log, image_id=docker_image_id
    )
    return pytest_dummynet.DummyNet(shell=shell)
