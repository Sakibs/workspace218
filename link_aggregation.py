#! /usr/bin/python

from mininet.net  import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo
from mininet.log  import setLogLevel
from mininet.link import TCLink
from mininet.link import Link
from mininet.cli  import CLI
from mininet.util import run
from mininet.term import makeTerm

setLogLevel('info')
#setLogLevel('debug')    # For diagnostics

if '__main__' == __name__:
    net = Mininet(controller=RemoteController)

    c0 = net.addController('c0')

    s1 = net.addSwitch('s1')

    h1 = net.addHost('h1')
    h2 = net.addHost('h2', mac='00:00:00:00:00:22')
    h3 = net.addHost('h3', mac='00:00:00:00:00:23')
    h4 = net.addHost('h4', mac='00:00:00:00:00:24')

    Link(s1, h1)
    Link(s1, h1)
    Link(s1, h2)
    Link(s1, h3)
    Link(s1, h4)

    net.build()
    c0.start()
    s1.start([c0])

    #net.startTerms()

    CLI(net)

    net.stop()
    

# class MyTopoClass(Topo):
#     def __init__(self):
#         super(MyTopoClass, self).__init__()

#         h1  = self.addHost('h1')
#         h2  = self.addHost('h2', mac='00:00:00:00:00:22')
#         h3  = self.addHost('h3', mac='00:00:00:00:00:33')
#         h4  = self.addHost('h4', mac='00:00:00:00:00:44')

#         s1 = self.addSwitch('s1', dpid='0000000000000001',
#                                    listenPort=6634)

#         self.addLink(s1, h1)
#         self.addLink(s1, h1)
#         self.addLink(s1, h2)
#         self.addLink(s1, h3)
#         self.addLink(s1, h4)


# ryu = RemoteController('c1', ip='127.0.0.1', port=6633)
# net = Mininet(topo=MyTopoClass(), switch=OVSSwitch, build=False, link=TCLink)
# net.addController(ryu)
# net.build()
# net.start()

# # Explicitly enable OpenFlow 1.3, then run the network
# #run("ovs-vsctl set bridge s1 protocols=OpenFlow10")
# CLI(net)
# net.stop()

