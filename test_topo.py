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

        h1 = self.addHost('h1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02')
        HS = self.addHost('HS', mac='00:00:00:00:00:10')
        IG = self.addHost('IG', mac='00:00:00:00:00:20')

        sr = self.addSwitch('sr', dpid='0000000000000010',
                                   listenPort=6634)
        s1 = self.addSwitch('s1', dpid='0000000000000001',
                                   listenPort=6634)
        s2 = self.addSwitch('s2', dpid='0000000000000002',
                                   listenPort=6634)
        s3 = self.addSwitch('s3', dpid='0000000000000003',
                                   listenPort=6634)

        bw_fast = 100
        bw_slow = 10
        self.addLink(h1, sr, bw=bw_fast)
        self.addLink(h2, sr, bw=bw_fast)
        self.addLink(HS, s2, bw=bw_fast)
        self.addLink(IG, s3, bw=bw_slow)

        self.addLink(sr, s1, bw=bw_fast)
        self.addLink(s1, s2, bw=bw_fast)
        self.addLink(s2, s3, bw=bw_slow)
        self.addLink(s3, s1, bw=bw_slow)


ryu = RemoteController('c1', ip='127.0.0.1', port=6633)
net = Mininet(topo=MyTopoClass(), switch=OVSSwitch, build=False, link=TCLink)
net.addController(ryu)
net.build()
net.start()

# Explicitly enable OpenFlow 1.3, then run the network
#run("ovs-vsctl set bridge s1 protocols=OpenFlow10")
CLI(net)
net.stop()

