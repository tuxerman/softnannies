from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink

net = Mininet(topo=Topo, host=CPULimitedHost, link=TCLink)

#create topology - two hosts, two switches, one controller
#nodeController = net.addController()
nodeH1 = net.addHost('H1')
nodeSwitch1 = net.addSwitch('S1')
nodeSwitch2 = net.addSwitch('S2')
nodeH2 = net.addHost('H2')

#create links
net.addLink(nodeH1, nodeSwitch1)
net.addLink(nodeSwitch1, nodeSwitch2)
net.addLink(nodeH2, nodeSwitch2)

#configure IP addresses
nodeH1.setIP('192.168.142.101', 24)
nodeH2.setIP('192.168.142.102', 24)

net.start()
net.pingAll()
CLI(net)
net.stop()

