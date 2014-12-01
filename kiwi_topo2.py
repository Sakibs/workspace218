#! /usr/bin/python
"""
Simple MiniNet two host, one switch, example for Kiwi PyCon talk:
(OpenFlow 1.3 only)

host(h1) --- switch(s1) --- host(h2)
|------- switch(s2) ----|

"""

from mininet.net  import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo
from mininet.log  import setLogLevel
from mininet.link import TCLink
from mininet.cli  import CLI
from mininet.util import run

setLogLevel('info')
#setLogLevel('debug')    # For diagnostics

class MyTopoClass(Topo):
    def __init__(self):
        super(MyTopoClass, self).__init__()

        h1  = self.addHost('h1', mac='00:00:00:00:00:01')
        h2  = self.addHost('h2', mac='00:00:00:00:00:02')
        h3  = self.addHost('h3', mac='00:00:00:00:00:03')

        s1 = self.addSwitch('s1', dpid='0000000000000001',
                                   listenPort=6634)
        s2 = self.addSwitch('s2', dpid='0000000000000002',
                                   listenPort=6634)
        s3 = self.addSwitch('s3', dpid='0000000000000003',
                                   listenPort=6634)

        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)

        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s1)


        # h1  = self.addHost('h1', mac='00:00:00:00:00:01')
        # h2  = self.addHost('h2', mac='00:00:00:00:00:02')

        # s1 = self.addSwitch('s1', dpid='0000000000000001',
        #                            listenPort=6634)
        # s2 = self.addSwitch('s2', dpid='0000000000000002',
        #                            listenPort=6634)
        # self.addLink(h1, s1)
        # self.addLink(h1, s2)
        # self.addLink(s1, h2)
        # self.addLink(s2, h2)

ryu = RemoteController('c1', ip='127.0.0.1', port=6633)
net = Mininet(topo=MyTopoClass(), switch=OVSSwitch, build=False, link=TCLink)
net.addController(ryu)
net.build()
net.start()

# Explicitly enable OpenFlow 1.3, then run the network
#run("ovs-vsctl set bridge s1 protocols=OpenFlow10")
CLI(net)
net.stop()

