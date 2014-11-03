from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def setup():
	net = Mininet(controller=Controller)

	info('**** Adding Controller ****')
	net.addController( 'c0' )

	info('**** Setting up Hosts ****')
	h1 = net.addHost('h1', ip=10.0.0.10)
	h2 = net.addHost('h2', ip=10.0.0.20)
	h3 = net.addHost('h3', ip=10.0.0.30)
	h4 = net.addHost('h4', ip=10.0.0.40)

	info('**** Setting up Switches ****')
	s1 = net.addSwitch('s1')
	s2 = net.addSwitch('s2')
	s3 = net.addSwitch('s3')

	info('**** Settings Links ****')
	net.addLink(s1, s2)
	net.addLink(s2, s3)
	net.addLink(h1, s1)
	net.addLink(h2, s1)
	net.addLink(h3, s3)
	net.addLink(h4, s3)

	info('**** Starting Ntwk ****')
	net.start()

	info('**** Running CLI ****')
	CLI( net )

	info('**** Stopping Ntwk ****')
	net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()

