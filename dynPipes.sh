# set the WAN interface
wanport=eth0

# create the two OVS bridges
ovs-vsctl del-br brdn
ovs-vsctl del-br brup
ovs-vsctl add-br brdn
ovs-vsctl add-br brup

ifconfig brup up promisc
ifconfig brdn up promisc

ovs-vsctl --no-wait set bridge brdn stp_enable=true
ovs-vsctl --no-wait set bridge brup stp_enable=true

#remove all the forwarding rules for the switches
ovs-ofctl del-flows brdn
ovs-ofctl del-flows brup

#adding the WAN interface to the second OVS
ifconfig $wanport 0
ovs-vsctl add-port brup $wanport 
#dhclient brup

#add host interfaces to brdn
ovs-vsctl add-port brdn eth1
#TODO make this dynamic as well

#delete all veths
for link in `ifconfig -a | grep vethUP | sed -r 's/(vethUP[0-9]+).*/\1/'`; 
do
	ip link del $link;
done

#reset port number file
rm portData.csv
touch portData.csv

#read csv file and set up pipes
# number, MAC address, TC value
INPUT=tcdata.csv
OLDIFS=$IFS
IFS=,
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read index macaddr tcvalue
do
	ip link add vethDN$index type veth peer name vethUP$index
	
	#interface up and promisc
	ifconfig vethUP$index up promisc
	ifconfig vethDN$index up promisc
	ovs-vsctl add-port brdn vethDN$index
	ovs-vsctl add-port brup vethUP$index

	#write out the port number
	portUp=`ovs-ofctl show brup | grep vethUP$index | sed -r 's/ ([0-9]+).*/\1/'`
        portDn=`ovs-ofctl show brdn | grep vethDN$index | sed -r 's/ ([0-9]+).*/\1/'`
	echo $index,$macaddr,$tcvalue,$portDn,$portUp >> portData.csv	
	
	# add peering link between switches
	ovs-vsctl set interface vethDN$index options:peer=vethUP$index
	ovs-vsctl set interface vethUP$index options:peer=vethDN$index
	
	#set TC
	ovs-vsctl set Interface vethDN$index ingress_policing_rate=$tcvalue
	ovs-vsctl set Interface vethUP$index ingress_policing_rate=$tcvalue
	ovs-vsctl set Interface vethDN$index ingress_policing_burst=$tcvalue
	ovs-vsctl set Interface vethUP$index ingress_policing_burst=$tcvalue
done < $INPUT
IFS=$OLDIFS

# Add controller addresses to both bridges
ovs-vsctl set-controller brdn tcp:0.0.0.0:6633
#ovs-vsctl set-fail-mode brdn secure
ovs-vsctl set-controller brup tcp:0.0.0.0:6633
#ovs-vsctl set-fail-mode brup secure

# get DHCP address
echo 'Running dhclient'
#dhclient brup
