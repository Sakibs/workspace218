from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def setup():
	net = Mininet(controller=RemoteController, switch=OVSSwitch)

	info('**** Adding Remote Controller ****\n')
	net.addController(name='c1', defaultIP='127.0.0.1', port=6633 )

	info('**** Setting up Hosts ****\n')
	h1 = net.addHost('h1', ip='10.0.0.10')
	h2 = net.addHost('h2', ip='10.0.0.20')
	h3 = net.addHost('h3', ip='10.0.0.30')
	h4 = net.addHost('h4', ip='10.0.0.40')

	info('**** Setting up Switches ****\n')
	s1 = net.addSwitch('s1')
	s2 = net.addSwitch('s2')
	s3 = net.addSwitch('s3')
	s4 = net.addSwitch('s4')

	info('**** Settings Links ****\n')
	net.addLink(h1, s1)
	net.addLink(h2, s2)
	net.addLink(h3, s3)
	net.addLink(h4, s4)
	
	net.addLink(s1, s2)
	net.addLink(s2, s3)
	net.addLink(s3, s4)
	net.addLink(s4, s1)

	info('**** Starting Ntwk ****\n')
	net.start()

	info('**** Running CLI ****\n')
	CLI( net )

	info('**** Stopping Ntwk ****\n')
	net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    setup()

