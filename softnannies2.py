from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *

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
    portPolicy = flood()
    with open(access_configuration, 'r') as c_file:
	    reader = DictReader(c_file, delimiter = ",")
            access_c = {}
            for row in reader:
	        access_c[row['id']] = ACCESS_CONFIGURATION(row['mac'], row['tc'], row['port_down'], row['port_up'], row['home'])

	for policy in access_c.itervalues():
	    portPolicy += 

	    if_(match(srcmac=MAC(policy.mac),switch=down_switch),fwd(int(policy.port_down)),
	    		if_(match(dstmac=MAC(policy.mac),switch=up_switch),fwd(int(policy.port_up)),
	    			if_(match(srcmac=MAC(policy.mac),switch=up_switch),fwd(port_wan),
	    				if_(match(dstmac=MAC(policy.mac),switch=down_switch),fwd(int(policy.home)),portPolicy))))

    ############# FINAL POLICY ###############

    #send only allowed packets to the double-switch architecture
    #return allowed >> portPolicy >> mac_learner()
    return allowed >> mac_learner()

