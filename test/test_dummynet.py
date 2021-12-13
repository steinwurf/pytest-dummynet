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

    with dummynet.host(sudo=False) as shell:

        # Get a list of the current namespaces
        namespaces = shell.netns_list()

        # If these namespaces exist, we will remove them and re-add them.
        # This allows us to reconfigure safely

        if namespace1 in namespaces:
            shell.netns_delete(namespace1)

        if namespace2 in namespaces:
            shell.netns_delete(namespace2)

        demo0 = shell.netns_add(name=namespace1)
        demo1 = shell.netns_add(name=namespace2)

        # Add a link. This will go between the namespaces.
        shell.link_veth_add(p1_name=peer1, p2_name=peer2)

        shell.link_set(namespace=namespace1, interface=peer1)
        shell.link_set(namespace=namespace2, interface=peer2)

        # Bind an IP-address to the two peers in the link.
        demo0.addr_add(ip=ip1 + "/" + port, interface=peer1)
        demo1.addr_add(ip=ip2 + "/" + port, interface=peer2)

        # Activate the interfaces.
        demo0.up(interface=peer1)
        demo1.up(interface=peer2)

        # We will add 20 ms of delay, 1% packet loss, a queue limit of 100 packets
        # and 10 Mbit/s of bandwidth max.
        demo0.tc(interface=peer1, delay=20, loss=1, limit=100, rate=10)
        demo1.tc(interface=peer2, delay=20, loss=1, limit=100, rate=10)

        # Show the tc-configuration of the interfaces.
        demo0.tc_show(interface=peer1)
        demo1.tc_show(interface=peer2)

        # Route the traffic through the given IPs in each of the namespaces
        demo0.route(ip=ip1)
        demo1.route(ip=ip2)

        demo0.nat(ip=ip1, interface=peer1)
        demo1.nat(ip=ip2, interface=peer2)

        # Clean up. Delete the link and the namespaces.
        demo0.link_delete(interface=peer1)

        shell.netns_delete(name=namespace1)
        shell.netns_delete(name=namespace2)
