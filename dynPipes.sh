#change to working directory
cd ~/pyretic/pyretic/examples/soft_nannies/

#set the WAN interface
wanport=eth0

# create the two OVS bridges
echo 'Creating the two OVS bridges...'
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
echo 'Adding WAN interface on $wanport to upstream bridge...'
ifconfig $wanport 0
ovs-vsctl add-port brup $wanport 

#add host interfaces to brdn
echo 'Adding hosts...'
ovs-vsctl add-port brdn eth1
ovs-vsctl add-port brdn eth2
#TODO make this dynamic as well

#delete all veths
echo 'Tearing down previously existing peering links between our two bridges...'
ip link del vethDEFdn
for link in `ifconfig -a | grep vethUP | sed -r 's/(vethUP[0-9]+).*/\1/'`; 
do
	ip link del $link;
done

# CREATE DEFAULT PIPE
echo 'Creating the default pipe...'
ip link add vethDEFdn type veth peer name vethDEFup

ifconfig vethDEFup up promisc
ifconfig vethDEFdn up promisc
ovs-vsctl add-port brup vethDEFup
ovs-vsctl add-port brdn vethDEFdn

ovs-vsctl set interface vethDEFdn options:peer=vethDEFup
ovs-vsctl set interface vethDEFup options:peer=vethDEFdn

portDefUp=`ovs-ofctl show brup | grep vethDEFup | sed -r 's/ ([0-9]+).*/\1/'`
portDefDn=`ovs-ofctl show brdn | grep vethDEFdn | sed -r 's/ ([0-9]+).*/\1/'`

#set TC for default pipe
ovs-vsctl set Interface vethDEFup ingress_policing_rate=5000
ovs-vsctl set Interface vethDEFdn ingress_policing_rate=5000
ovs-vsctl set Interface vethDEFdn ingress_policing_burst=5000
ovs-vsctl set Interface vethDEFup ingress_policing_burst=5000


echo 'Writing out default pipe port numbers to default.csv...'
rm default.csv
echo "port_down,port_up" > default.csv
echo $portDefDn,$portDefUp >> default.csv 

#reset port number file
rm portData.csv
touch portData.csv

echo 'About to read tcdata.csv and create rate-controlled pipes...'
echo "id,mac,tc,port_down,port_up,home" > portData.csv 

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

	#write out the port numbers
	portUp=`ovs-ofctl show brup | grep vethUP$index | sed -r 's/ ([0-9]+).*/\1/'`
    portDn=`ovs-ofctl show brdn | grep vethDN$index | sed -r 's/ ([0-9]+).*/\1/'`
    portHome=`ovs-ofctl show brdn | grep eth$index | sed -r 's/ ([0-9]+).*/\1/'`
	echo $index,$macaddr,$tcvalue,$portDn,$portUp,$portHome >> portData.csv	
	echo 'Setting up link for $tcvalue kbps for device $macaddr...'
	
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
echo 'Adding controller to both bridges...'
ovs-vsctl set-controller brdn tcp:0.0.0.0:6633
#ovs-vsctl set-fail-mode brdn secure
ovs-vsctl set-controller brup tcp:0.0.0.0:6633
#ovs-vsctl set-fail-mode brup secure

# get DHCP address
echo 'Running dhclient for upstream bridge...'
dhclient brup

echo 'Set-up has completed. Ready to roll!'
