from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller import controller
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_parser
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

class L2Switch(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)
        self.msg_num = 0


    def add_flow(self, datapath, in_port, dst, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port, dl_dst=haddr_to_bin(dst))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)

        self.logger.info("# Added flow")
        datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info("***** GOT FEATURES REQUEST!!!")
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        dpid = datapath.id

        eth_h1 = '00:00:00:00:00:01'
        eth_h2 = '00:00:00:00:00:02'
        eth_HS = '00:00:00:00:00:10'
        eth_IG = '00:00:00:00:00:20'

        # sps h1 is communcicating with HS. If HS sends to h1 use 100 mb link directly to h1

        if dpid == 16:
            # num in ports in switch
            n_ports = 3
            # map destinations to output ports of switch
            mapping = {eth_h1: 1, eth_h2: 2, eth_HS: 3, eth_IG: 3}

            self.setup_flows(datapath, ofp_parser, n_ports, mapping)

        if dpid == 1:
            # num in ports in switch
            n_ports = 3
            # map destinations to output ports of switch
            mapping = {eth_h1: 1, eth_h2: 1, eth_HS: 2, eth_IG: 3}

            self.setup_flows(datapath, ofp_parser, n_ports, mapping)

        if dpid == 2:
            # num in ports in switch
            n_ports = 3
            # map destinations to output ports of switch
            mapping = {eth_h1: 2, eth_h2: 3, eth_HS: 1, eth_IG: 3}

            self.setup_flows(datapath, ofp_parser, n_ports, mapping)

        if dpid == 3:
            # num in ports in switch
            n_ports = 3
            # map destinations to output ports of switch
            mapping = {eth_h1: 3, eth_h2: 3, eth_HS: 2, eth_IG: 1}

            self.setup_flows(datapath, ofp_parser, n_ports, mapping)

        self.logger.info('*****************************')

    def setup_flows(self, datapath, ofp_parser, n_ports, out_map):
        for i in range(1, n_ports+1):
            for dst,out_port in out_map.items():
                action = [ofp_parser.OFPActionOutput(out_port)]
                self.add_flow(datapath, i, dst, action)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        dpid = dp.id
        dst = eth.dst
        src = eth.src

        self.logger.info("===============Message: %d================", self.msg_num)
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)
        self.logger.info("src: %s, in_port: %s", src, msg.in_port)
        self.logger.info("------------------------------------")
        if dst == 'ff:ff:ff:ff:ff:ff':
            self.logger.info("BROADCASTING")
        else:
            self.logger.info(dst)

        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions)

        self.msg_num += 1
        self.logger.info("=======================================")
        dp.send_msg(out)
