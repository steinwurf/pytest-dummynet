from subprocess import CalledProcessError
import pytest
import pytest_dummynet

peer1 = "demo0-eth"
peer2 = "demo1-eth"

namespace1 = "demo0"
namespace2 = "demo1"

ip1 = "10.0.0.1"
ip2 = "10.0.0.2"

port = "24"


def test_dummynet_fixture(dummynet):
    # We don't do anything just check that the fixture is available
    pass


def test_run(dummynet):

    namespaces = dummynet.netns_list()

    if namespace1 in namespaces:
        dummynet.netns_delete(namespace1)

    if namespace2 in namespaces:
        dummynet.netns_delete(namespace2)

    demo0 = dummynet.netns_add(name=namespace1)
    demo1 = dummynet.netns_add(name=namespace2)

    dummynet.link_veth_add(p1_name=peer1, p2_name=peer2)

    dummynet.link_set(namespace=namespace1, interface=peer1)
    dummynet.link_set(namespace=namespace2, interface=peer2)

    demo0.addr_add(ip=ip1 + "/" + port, interface=peer1)
    demo1.addr_add(ip=ip2 + "/" + port, interface=peer2)

    demo0.up(interface=peer1)
    demo1.up(interface=peer2)

    demo0.tc(interface=peer1, delay=20, loss=1, limit=100, rate=10)
    demo1.tc(interface=peer2, delay=20, loss=1, limit=100, rate=10)

    demo0.tc_show(interface=peer1)
    demo1.tc_show(interface=peer2)

    demo0.route(ip=ip1)
    demo1.route(ip=ip2)

    demo0.nat(ip=ip1, interface=peer1)
    demo1.nat(ip=ip2, interface=peer2)

    demo0.link_delete(interface=peer1)

    dummynet.netns_delete(name=namespace1)
    dummynet.netns_delete(name=namespace2)
