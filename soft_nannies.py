'''
Georgia Tech CS6675 Spring 2014 Course Project: SoftNannies
Karim Habak
Robert Lychev
Sriram Padnamabhan
'''

from pyretic.lib.corelib import *
from pyretic.lib.std import *

# insert the name of the module and policy you want to import
from pyretic.modules.pyretic_switch import act_like_switch
from collections import namedtuple
from csv import DictReader

import os
import csv

#list of websites/ip addresses that should not be accessed by certain MAC addresses outside a certain range of time
access_policies = "%s/pyretic/pyretic/examples/soft_nannies/access_policies.csv" % os.environ[ 'HOME' ]

#list of mac addresses and their corresponding forwarding port numbers
access_configuration= "%s/pyretic/pyretic/examples/soft_nannies/access_configuration.csv" % os.environ[ 'HOME' ]

#if true, then anyone can joing the network, otherwise only the devices with specific MACs as listed in policy_out.csv can
access_mode = "%s/pyretic/pyretic/examples/soft_nannies/access_mode.csv" % os.environ[ 'HOME' ]

#a tuple for holding network configuration, i.e. forwarding port numbers for each host in the networks
ACCESS_CONFIGURATION = namedtuple('ACCESS_CONFIGURATION', ('mac', 'out_port', 'in_port', 'tc'))
#a tuple for holding access policies, i.e. which hosts in the network are restricted from accessing which sites
ACCESS_POLICY = namedtuple('ACCESS_POLICY', ('src_mac', 'dst_ip', 't_begin', 't_end'))


#create the default switching behavior for the double switch architecture
#@dynamic here means that the function below will create a new dynamic
#policy class with the name "double_trouble"
@dynamic
def double_trouble(self):


    #this will be static;
    #these are ids of the vswitches
    self.down_switch = 1 #int("0x0000080027b1d7f1",16)
    self.up_switch = 2 #int("0x0000080027b7bf8b",16)

    #figure out if all packets should be flooded or dropped initially by default
    with open(access_mode, 'r') as a_mode:
        reader = DictReader(a_mode, delimiter = ",")
        access_m = {}
        for row in reader:
            access_m[row['id']] = row['value']

    if(int(access_m['1']) == 1):
        self.frwrd = flood() #fwd(6633);
    else:
        self.frwrd = drop #very strict policy

    #default query for receiving incoming packets
    self.qry = packets(limit=1,group_by=['srcmac','switch'])

    #set the initial internal policy value
    self.policy = self.frwrd + self.qry


    #update the forwarding configuration from the access configuration policy file
    with open(access_configuration, 'r') as c_file:
        reader = DictReader(c_file, delimiter = ",")
        access_c = {}
        for row in reader:
            access_c[row['id']] = ACCESS_CONFIGURATION(row['mac'], row['out_port'], row['in_port'], row['tc'])
    for policy in access_c.itervalues():
        self.frwrd = if_(match(srcmac=MAC(policy.mac),switch=self.down_switch),fwd(int(policy.out_port)),self.policy)
        self.policy = self.frwrd + self.qry
        self.frwrd = if_(match(dstmac=MAC(policy.mac),switch=self.up_switch),fwd(int(policy.in_port)),self.policy)
        self.policy = self.frwrd + self.qry

    #the following logc was borrowed from the pyretic_switch module
    #the idea is to take each new packet pkt and update the forwarding policy
    #so that subsequent incoming packets on this switch whose dstmac matches pkt's srcmac
    #(accessed like in a dictionary pkt['srcmac']) will be forwarded out  pkt's inport
    #(pyretic packets are located, so this value is accessed just like srcmac,i.e., p['inport'])
    def learn_from_a_packet(pkt):
        #set the forwarding policy
        self.frwrd = if_(match(dstmac=pkt['srcmac'],
                                 switch=pkt['switch']), fwd(pkt['inport']),
                           self.policy)
        #update the overall policy
        self.policy = self.frwrd + self.qry
        #print self.policy

    #learn_from_a_packet is called back every time our query sees a new packet
    self.qry.register_callback(learn_from_a_packet)

    print 'double_trouble is a go\n'



#the main method sets up access control filters and calls
#the double_trouble (double-switch) architecture
def main():

    #default policy does not match anything
    not_allowed = none

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

    print '\n\nSoftNannies have rolled up their sleeves!\n'

    #send only allowed packets to the double-switch architecture
    return allowed >> double_trouble()
