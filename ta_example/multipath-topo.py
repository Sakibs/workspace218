#!/usr/bin/python

"""
This example creates a multi-controller network from
semi-scratch; note a topo object could also be used and
would be passed into the Mininet() constructor.
"""

import xml.etree.ElementTree as ET
import re

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import UserSwitch, OVSSwitch, OVSLegacyKernelSwitch, IVSSwitch
from mininet.node import RemoteController
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info, error
from mininet.cli import CLI
from mininet.cli import CLI
from mininet.log import lg
from mininet.node import Node

#################################
def startNAT( root, inetIntf='wlan0', subnet='10.0/8' ):
	"""Start NAT/forwarding between Mininet and external network
	root: node to access iptables from
	inetIntf: interface for internet access
	subnet: Mininet subnet (default 10.0/8)="""

	# Identify the interface connecting to the mininet network
	localIntf =  root.defaultIntf()

	# Flush any currently active rules
	root.cmd( 'iptables -F' )
	root.cmd( 'iptables -t nat -F' )

	# Create default entries for unmatched traffic
	root.cmd( 'iptables -P INPUT ACCEPT' )
	root.cmd( 'iptables -P OUTPUT ACCEPT' )
	root.cmd( 'iptables -P FORWARD DROP' )

	# Configure NAT
	root.cmd( 'iptables -I FORWARD -i', localIntf, '-d', subnet, '-j DROP' )
	root.cmd( 'iptables -A FORWARD -i', localIntf, '-s', subnet, '-j ACCEPT' )
	root.cmd( 'iptables -A FORWARD -i', inetIntf, '-d', subnet, '-j ACCEPT' )
	root.cmd( 'iptables -t nat -A POSTROUTING -o ', inetIntf, '-j MASQUERADE' )

	# Instruct the kernel to perform forwarding
	root.cmd( 'sysctl net.ipv4.ip_forward=1' )

def stopNAT( root ):
	"""Stop NAT/forwarding between Mininet and external network"""
	# Flush any currently active rules
	root.cmd( 'iptables -F' )
	root.cmd( 'iptables -t nat -F' )

	# Instruct the kernel to stop forwarding
	root.cmd( 'sysctl net.ipv4.ip_forward=0' )

def fixNetworkManager( root, intf ):
	"""Prevent network-manager from messing with our interface,
	   by specifying manual configuration in /etc/network/interfaces
	   root: a node in the root namespace (for running commands)
	   intf: interface name"""
	cfile = '/etc/network/interfaces'
	line = '\niface %s inet manual\n' % intf
	config = open( cfile ).read()
	if ( line ) not in config:
		print '*** Adding', line.strip(), 'to', cfile
		with open( cfile, 'a' ) as f:
			f.write( line )
	# Probably need to restart network-manager to be safe -
	# hopefully this won't disconnect you
	#root.cmd( 'service network-manager restart' )

def connectToInternet( net, switch='s1', rootip='10.10.10.254', subnet='10.10.10.0/24'):
	"""Connect the network to the internet
	   switch: switch to connect to root namespace
	   rootip: address for interface in root namespace
	   subnet: Mininet subnet"""
	switch = net.get( switch )
	prefixLen = subnet.split( '/' )[ 1 ]

	# Create a node in root namespace
	root = Node( 'root', inNamespace=False )

	# Prevent network-manager from interfering with our interface
	fixNetworkManager( root, 'root-eth0' )

	# Create link between root NS and switch
	link = net.addLink( root, switch, bw=bandwidth, delay='0.1ms', loss=0.001, use_htb=True)
	link.intf1.setIP( rootip, prefixLen )

	# Start network that now includes link to root namespace
	net.start()

	# Start NAT and establish forwarding
	startNAT( root )

	# Establish routes from end hosts
	for host in net.hosts:
		host.cmd( 'ip route flush root 0/0' )
		host.cmd( 'route add -net', subnet, 'dev', host.defaultIntf() )
		host.cmd( 'route add default gw', rootip )
		host.cmd( '/usr/sbin/sshd -D &' )

	return root

class TopoInternet2(Topo):
	"Single switch connected to n host#s."
	def __init__(self, **opts):
		Topo.__init__(self, **opts)

		for n in range(0,4):
			dpid = ( 0 + 0 ) * 256 + ( n + 1 )
			s.append(self.addSwitch('s%s' % n, dpid='%016x' % dpid))
			h.append(self.addHost('h%s' % n, cpu=.95/len(s), ip='10.10.10.1%s'% n))
			self.addLink(h[n], s[n],  bw=bandwidth, delay='0.1ms', loss=0.001, use_htb=True)			

		# 1000 Mbps, 1ms delay, 1% loss, 1000 packet queue
		self.addLink(s[0], s[1], bw=bandwidth, delay='0.1ms', loss=0.001, use_htb=True)
		self.addLink(s[1], s[2], bw=bandwidth, delay='0.1ms', loss=0.001, use_htb=True)
		self.addLink(s[2], s[3], bw=bandwidth, delay='0.1ms', loss=0.001, use_htb=True)
		self.addLink(s[3], s[0], bw=bandwidth, delay='0.1ms', loss=0.001, use_htb=True)
		

def run():
	"Create network and run simple performance test"
	
	topo = TopoInternet2()
	net = Mininet(topo=topo, controller=RemoteController, switch=OVSSwitch, host=CPULimitedHost, link=TCLink)
	net.addController(name="c1",defaultIP='127.0.0.1' ,port=6633)
	
	rootnode = connectToInternet( net )

	net.start()
	#net.pingAll()
	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel('info')
	bandwidth = 100
	s = list()
	h = list()
	run()
