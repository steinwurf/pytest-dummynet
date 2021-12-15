import pytest
import pytest_dummynet
import logging
import docker


@pytest.fixture(scope="session")
def dummynet():
    """Creates the py.test fixture to make it usable within the unit-tests.
    See the DummyNet class for information"""

    log = logging.getLogger("dummynet")
    return pytest_dummynet.DummyNetFactory(log)
