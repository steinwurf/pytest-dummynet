import pytest
import pytest_dummynet
import logging


@pytest.fixture(scope="session")
def dummynet(request):
    """Creates the py.test fixture to make it usable within the unit-tests.
    See the DummyNet class for information"""

    log = logging.getLogger("client")

    shell = pytest_dummynet.Shell(log=log, sudo=False)

    return pytest_dummynet.DummyNet(shell=shell)
