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
from mininet.cli  import CLI
from mininet.util import run

setLogLevel('info')
#setLogLevel('debug')    # For diagnostics

class MyTopoClass(Topo):
    def __init__(self):
        super(MyTopoClass, self).__init__()
        #leftHost  = self.addHost('h1', ip='172.31.1.1/24')
        leftHost  = self.addHost('h1')
        rightHost  = self.addHost('h2')
        #rightHost = self.addHost('h2', ip='172.31.1.2/24')
        oneSwitch = self.addSwitch('s1', dpid='0000000000000099',
                                   listenPort=6634)
        twoSwitch = self.addSwitch('s2', dpid='0000000000000100',
                                   listenPort=6634)
        self.addLink(leftHost,  oneSwitch)
        self.addLink(leftHost,  twoSwitch)
        self.addLink(oneSwitch, rightHost)
        self.addLink(twoSwitch, rightHost)

ryu = RemoteController('c1', ip='127.0.0.1', port=6633)
net = Mininet(topo=MyTopoClass(), switch=OVSSwitch, build=False)
net.addController(ryu)
net.build()
net.start()

# Explicitly enable OpenFlow 1.3, then run the network
#run("ovs-vsctl set bridge s1 protocols=OpenFlow10")
CLI(net)
net.stop()