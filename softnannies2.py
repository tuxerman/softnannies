'''
Georgia Tech CS6675 Spring 2014 Course Project: SoftNannies 
Karim Habak
Robert Lychev
Sriram Padnamabhan
'''


from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *
from pyretic.modules.mac_learner import * 

from collections import namedtuple
from csv import DictReader

import os
import csv

#list of websites/ip addresses that should not be accessed by certain MAC addresses outside a certain range of time
access_policies = "%s/pyretic/pyretic/examples/soft_nannies/access_policies.csv" % os.environ[ 'HOME' ] 

#list of mac addresses and their corresponding forwarding port numbers 
access_configuration= "%s/pyretic/pyretic/examples/soft_nannies/portData.csv" % os.environ[ 'HOME' ] 

#if true, then anyone can joing the network, otherwise only the devices with specific MACs as listed in policy_out.csv can
access_mode = "%s/pyretic/pyretic/examples/soft_nannies/access_mode.csv" % os.environ[ 'HOME' ]

#the port numbers for the defaul pipe for  both switches
access_default = "%s/pyretic/pyretic/examples/soft_nannies/default.csv" % os.environ[ 'HOME' ]

#a tuple for holding network configuration, i.e. forwarding port numbers for each host in the networks
ACCESS_CONFIGURATION = namedtuple('ACCESS_CONFIGURATION', ('mac', 'tc', 'port_down', 'port_up', 'home'))
#a tuple for holding access policies, i.e. which hosts in the network are restricted from accessing which sites
ACCESS_POLICY = namedtuple('ACCESS_POLICY', ('src_mac', 'dst_ip', 't_begin', 't_end'))
#a tuple for holding port numbers of the default pipe
ACCESS_DEFAULT = namedtuple('ACCESS_DEFAULT', ('port_down', 'port_up'))

def PolicyManager(access_c, DeviceID, Max):
    policy = access_c[DeviceID]
    if DeviceID-1 == Max:
        return identity
    return if_(match(srcmac=MAC(policy.mac),switch=down_switch),fwd(int(policy.port_down)),
                if_(match(dstmac=MAC(policy.mac),switch=up_switch),fwd(int(policy.port_up)),
                    if_(match(srcmac=MAC(policy.mac),switch=up_switch),fwd(port_wan),
                        if_(match(dstmac=MAC(policy.mac),switch=down_switch),fwd(int(policy.home)),PolicyManager(access_c, DeviceID+1, Max)))))

def main():

    # GLOBALS #############################
    up_switch = int("0x0000080027b1d7f1",16)
    down_switch = int("0x00000800278507d5",16)
    port_wan = 1

    #default policy does not match anything
    not_allowed = none

    ################# IP BLOCKERS ################

    #read in the access policies and update them
    with open(access_policies, 'r') as p_file:
   	reader = DictReader(p_file, delimiter = ",")
        access_p = {}
        for row in reader:
	    access_p[row['id']] = ACCESS_POLICY(row['src_mac'], row['dst_ip'], row['t_begin'], row['t_end'])
    for policy in access_p.itervalues():
	not_allowed = not_allowed | match(srcmac=MAC(policy.src_mac),dstip=IP(policy.dst_ip)) | match(srcip=IP(policy.dst_ip),dstmac=MAC(policy.src_mac))

    #express allowed packets as the complement of not_allowed
    allowed = ~not_allowed

    ############# PORT FORWARDS #################
    portPolicy = drop
    with open(access_configuration, 'r') as c_file:
	    reader = DictReader(c_file, delimiter = ",")
            access_c = {}
            for row in reader:
	           access_c[row['id']] = ACCESS_CONFIGURATION(row['mac'], row['tc'], row['port_down'], row['port_up'], row['home'])

    portPolicy = PolicyManager(access_c, 1, len(access_c))

    # for policy in access_c.itervalues():
    #     portPolicy = portPolicy +  if_(match(srcmac=MAC(policy.mac),switch=down_switch),fwd(int(policy.port_down)),
	   #  		if_(match(dstmac=MAC(policy.mac),switch=up_switch),fwd(int(policy.port_up)),
	   #  			if_(match(srcmac=MAC(policy.mac),switch=up_switch),fwd(port_wan),
	   #  				if_(match(dstmac=MAC(policy.mac),switch=down_switch),fwd(int(policy.home)),drop))))

	#portPolicy = if_(portPolicy, identity, drop)

    ############# FINAL POLICY ###############

    #send only allowed packets to the double-switch architecture
    return allowed >> portPolicy >> mac_learner()
    #return allowed >> mac_learner()

