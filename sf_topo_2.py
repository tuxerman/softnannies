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


#CREATE A TOPOLOGY WHERE h1 AND h2 GET A FIXED BANDWIDTH ALLOCATION, WHILE H3 AND H4 HAVE TO COMPETE
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
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
   
        self.addLink(w1, s5, bw=100)
        self.addLink(w2, s5, bw=100)
        self.addLink(w3, s5, bw=100)
        self.addLink(h1, s1, bw=100)
        self.addLink(h2, s1, bw=100)
        self.addLink(h3, s1, bw=100)
        self.addLink(h4, s1, bw=100)
	self.addLink(s1, s2, bw=10) 
	self.addLink(s1, s3, bw=10) 
	self.addLink(s1, s4, bw=10) 
	self.addLink(s2, s5, bw=10) 
	self.addLink(s3, s5, bw=10) 
	self.addLink(s4, s5, bw=10) 


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
