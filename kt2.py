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

        # network 1
        n1h1  = self.addHost('n1h1', mac='00:00:00:00:00:11')
        n1h2  = self.addHost('n1h2', mac='00:00:00:00:00:12')
        n1h3  = self.addHost('n1h3', mac='00:00:00:00:00:13')

        n1s1 = self.addSwitch('n1s1', dpid='0000000000000001',
                                   listenPort=6634)
        n1s2 = self.addSwitch('n1s2', dpid='0000000000000002',
                                   listenPort=6634)
        n1s3 = self.addSwitch('n1s3', dpid='0000000000000003',
                                   listenPort=6634)

        self.addLink(n1h1, n1s1)
        self.addLink(n1h2, n1s2)
        self.addLink(n1h3, n1s3)

        self.addLink(n1s1, n1s2)
        self.addLink(n1s2, n1s3)
        self.addLink(n1s3, n1s1)


        # # network 2
        # n2h1  = self.addHost('n2h1', mac='00:00:00:00:00:21')
        # n2h2  = self.addHost('n2h2', mac='00:00:00:00:00:22')
        # n2h3  = self.addHost('n2h3', mac='00:00:00:00:00:23')

        # n2s1 = self.addSwitch('n2s1', dpid='0000000000000004',
        #                            listenPort=6634)
        # n2s2 = self.addSwitch('n2s2', dpid='0000000000000005',
        #                            listenPort=6634)
        # n2s3 = self.addSwitch('n2s3', dpid='0000000000000006',
        #                            listenPort=6634)

        # self.addLink(n2h1, n2s1)
        # self.addLink(n2h2, n2s2)
        # self.addLink(n2h3, n2s3)

        # self.addLink(n2s1, n2s2)
        # self.addLink(n2s2, n2s3)
        # self.addLink(n2s3, n2s1)


        # # make intermediate connecting switch
        # smid = self.addSwitch('smid', dpid='0000000000000004',
        #                            listenPort=6634)

        

ryu = RemoteController('c1', ip='127.0.0.1', port=6633)
net = Mininet(topo=MyTopoClass(), switch=OVSSwitch, build=False, link=TCLink)
net.addController(ryu)
net.build()
net.start()

# Explicitly enable OpenFlow 1.3, then run the network
#run("ovs-vsctl set bridge s1 protocols=OpenFlow10")
CLI(net)
net.stop()

