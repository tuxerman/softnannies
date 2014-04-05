# create the tow OVS
ovs-vsctl add-br brdn
ovs-vsctl add-br brup

#remove all the forwarding rules for the switches
ovs-ofctl del-flows brdn
ovs-ofctl del-flows brup

#adding the LAN interface to the first OVS
ovs-vsctl add-port brdn eth10
ovs-vsctl add-port brdn eth11

#adding the WAN interface to the second OVS
ovs-vsctl add-port brup WAN

# create a tow virtual interface (the command create two virtual interface veth, This will create veth0 and veth1 )
ovs-vsctl add-port brdn eth12
ovs-vsctl set interface eth12 type=patch
ovs-vsctl set interface eth12 options:peer=port2

ovs-vsctl add-port brdn eth13
ovs-vsctl set interface eth13 type=patch
ovs-vsctl set interface eth13 options:peer=port3

ovs-vsctl add-port brup port2
ovs-vsctl set interface port2 type=patch
ovs-vsctl set interface port2 options:peer=eth12

ovs-vsctl add-port brup port3
ovs-vsctl set interface port3 type=patch
ovs-vsctl set interface port3 options:peer=eth13


ip link add type veth

# make sure all the physical and virtual interface are up and in promisc
ifconfig veth0 up
ifconfig veth1 up
ifconfig eth10 up
ifconfig eth11 up
ifconfig wlan0 up

ifconfig veth0 promisc
ifconfig veth1 promisc
ifconfig eth10 promisc
ifconfig eth11 promisc
ifconfig wlan0 promisc


#adding the virtual interfaces to the two OVS and make sure they are peered
# TODO: What do these do?
ovs-vsctl add-port brdn veth0
ovs-vsctl set interface veth0 options:peer=veth1

ovs-vsctl add-port brup veth1
ovs-vsctl set interface veth1 options:peer=veth0

# Enable Spanning tree for both OVS
ovs-vsctl --no-wait set bridge brdn stp_enable=true
ovs-vsctl --no-wait set bridge brup stp_enable=true


#adding the controller IP address to both virtual switches
#ovs-vsctl set-controller brdn tcp:192.168.142.50:6633
#ovs-vsctl set-fail-mode brdn secure

#ovs-vsctl set-controller brup tcp:192.168.142.50:6633
#ovs-vsctl set-fail-mode brup secure

# Rate limiting the bandwidth between the two OVS to 1Mbps both virtual interfaces 
tc qdisc add dev veth0 root tbf rate 1Mbit latency 1ms burst 10
tc qdisc add dev veth1 root tbf rate 1Mbit latency 1ms burst 10

