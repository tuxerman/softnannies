# create the tow OVS
ovs-vsctl add-br brdn
ovs-vsctl add-br brup

#remove all the forwarding rules for the switches
ovs-ofctl del-flows brdn
ovs-ofctl del-flows brup

#adding the WAN interface to the second OVS
ovs-vsctl add-port brup eth0 

#delete all veths
for link in `ifconfig -a | grep vethUP | sed -r 's/(vethUP[0-9]+).*/\1/'`; 
do
	ip link del $link;
done

#read csv file and set up pipes
# number, MAC address, TC value
INPUT=tcdata.csv
OLDIFS=$IFS
IFS=,
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read index macaddr tcvalue
do
	ip link add vethDN$index type veth peer name vethUP$index
	ovs-vsctl add-port brdn vethDN$index
	ovs-vsctl add port brup vethUP$index
	# add peering link between switches
	ovs-vsctl set interface vethDN$index options:peer=vethUP$index
	ovs-vsctl set interface vethUP$index options:peer=vethDN$index
	#interface up and promisc
	ifconfig vethUP$index up promisc
	ifconfig vethDN$index up promisc
	#set TC
	ovs-vsctl set Interface vethDN$index ingress_policing_rate=$tcvalue
	ovs-vsctl set Interface vethUP$index ingress_policing_rate=$tcvalue
	ovs-vsctl set Interface vethDN$index ingress_policing_burst=$tcvalue
	ovs-vsctl set Interface vethUP$index ingress_policing_burst=$tcvalue
done < $INPUT
IFS=$OLDIFS

# Add controller addresses to both bridges
ovs-vsctl set-controller brdn tcp:0.0.0.0:6633
ovs-vsctl set-fail-mode brdn secure
ovs-vsctl set-controller brup tcp:0.0.0.0:6633
ovs-vsctl set-fail-mode brup secure