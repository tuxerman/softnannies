"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host
   host --/


Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHostA = self.addHost( 'hl1' )
        leftHostB = self.addHost( 'hl1' )
        rightHost = self.addHost( 'hr1' )
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( leftHostA, leftSwitch )
        self.addLink( leftHostB, leftSwitch )
        self.addLink( leftSwitch, rightSwitch )
        self.addLink( rightSwitch, rightHost )


topos = { 'mytopo': ( lambda: MyTopo() ) }
