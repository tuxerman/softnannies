#!/usr/bin/python

#Georgia Tech CS6675 Spring 2014 Course Project: SoftNannies 
#Karim Habak
#Robert Lychev
#Sriram Padnamabhan


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI


#CREATE A TOPOLOGY WHERE EVERY HOST COMPETES FOR THE SAME BANDWIDTH
class crazy_switches(Topo):

    def __init__(self, **opts):

        super(crazy_switches, self).__init__(**opts)

        h1 = self.addHost('h1',  cpu=.5/2)
        h2 = self.addHost('h2',  cpu=.5/2)
        h3 = self.addHost('h3',  cpu=.5/2)
        h4 = self.addHost('h4',  cpu=.5/2)
        
        w1 = self.addHost('w1', cpu=.5/2)
        w2 = self.addHost('w2', cpu=.5/2)
        w3 = self.addHost('w3', cpu=.5/2)

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        self.addLink(w1, s2, bw=40)
        self.addLink(w2, s2, bw=50)
        self.addLink(w3, s2, bw=100)
        self.addLink(h1, s1, bw=100)
        self.addLink(h2, s1, bw=100)
        self.addLink(h3, s1, bw=100)
        self.addLink(h4, s1, bw=100)
	self.addLink(s1, s2, bw=30) 


def perfTest():
    topo = crazy_switches()
    net = Mininet(topo=topo, controller=lambda name: RemoteController( 'c0', '127.0.0.1' ),
                  host=CPULimitedHost, link=TCLink)
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    perfTest()
