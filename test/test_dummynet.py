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


def test_run(dummynet, mocker):

    mocked_class = mocker.patch("pytest_dummynet.host_shell.HostShell")
    mocked_shell = mocker.Mock()

    mocked_shell.run.side_effect = [
        "",
        "",
        "",
        "demo1\ndemo0\n",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]

    mocked_class.return_value = mocked_shell
    with dummynet.host(sudo=False) as shell:
        mocked_class.assert_called_once_with(log=mocker.ANY, sudo=False)

        # Get a list of the current namespaces
        namespaces = shell.netns_list()
        assert namespaces == []

        # create two namespaces
        demo0 = shell.netns_add(name=namespace1)
        demo1 = shell.netns_add(name=namespace2)

        # Get a list of the current namespaces
        namespaces = shell.netns_list()

        assert namespace1 in namespaces
        assert namespace2 in namespaces

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
    print(mocked_shell.run.mock_calls)
    mocked_shell.run.assert_has_calls(
        [
            mocker.call(cmd="ip netns list", cwd=None),
            mocker.call(cmd=f"ip netns add {namespace1}", cwd=None),
            mocker.call(cmd=f"ip netns add {namespace2}", cwd=None),
            mocker.call(cmd="ip netns list", cwd=None),
            mocker.call(
                cmd=f"ip link add {peer1} type veth peer name {peer2}", cwd=None
            ),
            mocker.call(cmd=f"ip link set {peer1} netns {namespace1}", cwd=None),
            mocker.call(cmd=f"ip link set {peer2} netns {namespace2}", cwd=None),
            mocker.call(
                cmd=f"ip netns exec {namespace1} ip addr add {ip1}/{port} dev {peer1}",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} ip addr add {ip2}/{port} dev {peer2}",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} ip link set dev {peer1} up", cwd=None
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} ip link set dev {peer2} up", cwd=None
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} tc qdisc show dev {peer1}", cwd=None
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} tc qdisc add dev {peer1} root netem delay 20ms loss 1% rate 10Mbit limit 100",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} tc qdisc show dev {peer2}", cwd=None
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} tc qdisc add dev {peer2} root netem delay 20ms loss 1% rate 10Mbit limit 100",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} tc qdisc show dev {peer1}", cwd=None
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} tc qdisc show dev {peer2}", cwd=None
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} ip route add default via {ip1}",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} ip route add default via {ip2}",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} iptables -t nat -A POSTROUTING -s {ip1} -o {peer1} -j MASQUERADE",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace2} iptables -t nat -A POSTROUTING -s {ip2} -o {peer2} -j MASQUERADE",
                cwd=None,
            ),
            mocker.call(
                cmd=f"ip netns exec {namespace1} ip link delete {peer1}", cwd=None
            ),
            mocker.call(cmd=f"ip netns delete {namespace1}", cwd=None),
            mocker.call(cmd=f"ip netns delete {namespace2}", cwd=None),
        ]
    )
