# create the tow OVS
ovs-vsctl add-br brdn
ovs-vsctl add-br brup

#remove all the forwarding rules for the switches
ovs-ofctl del-flows brdn
ovs-ofctl del-flows brup

#add a veth pair
ip link add type veth

#add host connections 
#TODO : Add more hosts here as necessary
ovs-vsctl add-port brdn eth1

#adding the WAN interface to the second OVS
#this is our current gateway to the internet. On router, this is the WAN port.
ovs-vsctl add-port brup eth0 
 
######### CREATE LINKS ################
# add a veth pair
ip link add type veth
ovs-vsctl add-port brdn veth0 
ovs-vsctl add port brup veth1
# add peering link between switches
ovs-vsctl set interface veth1 options:peer=veth0
ovs-vsctl set interface veth0 options:peer=veth1

# Up all the interfaces and set them to promiscous mode
ifconfig eth0 up promisc
ifconfig eth1 up promisc
ifconfig veth0 up promisc
ifconfig veth1 up promisc


# Enable Spanning tree for both OVS
s1 ovs-vsctl --no-wait set bridge brdn stp_enable=true
s1 ovs-vsctl --no-wait set bridge brup stp_enable=true

# SET UP TC FOR ports
s1 ovs-vsctl set Interface veth1 ingress_policing_rate=10000
s1 ovs-vsctl set Interface veth0 ingress_policing_rate=10000
s1 ovs-vsctl set Interface veth1 ingress_policing_burst=10000
s1 ovs-vsctl set Interface veth0 ingress_policing_burst=10000

# Add controller addresses to both bridges
ovs-vsctl set-controller brdn tcp:0.0.0.0:6633
ovs-vsctl set-fail-mode brdn secure
ovs-vsctl set-controller brup tcp:0.0.0.0:6633
ovs-vsctl set-fail-mode brup secure


################### SCRAPYARD #############################
# TC CODE: Doesnt work well here
# Rate limiting the bandwidth between the two OVS to 1Mbps both virtual interfaces 
#tc qdisc add dev dnEth root tbf rate 1Mbit latency 1ms burst 10
#tc qdisc add dev upEth root tbf rate 1Mbit latency 1ms burst 10

# MANUAL OVERRIDE: ADD STATIC FLOWS
# s1 ovs-ofctl add-flow brdn in_port=2,actions=output:1 #CAUTION! RUN 's1 ovs-ofctl show brdn' ..
# s1 ovs-ofctl add-flow brup in_port=1,actions=output:2 #CAUTION! .. and check port numbers before proceeding

