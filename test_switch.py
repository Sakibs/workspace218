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

        s1_p_h1 = 1
        s1_p_s2 = 2
        s2_p_h2 = 1
        s2_p_s1 = 2

        self.logger.info(dpid)

        # set actions at switch 1
        if dpid == 1:
            # set output ports when routing to specific destinations
            act_s1_h1 = [ofp_parser.OFPActionOutput(s1_p_h1)]
            act_s1_h2 = [ofp_parser.OFPActionOutput(s1_p_s2)]
            t = self.add_flow(datapath, 1, eth_h1, act_s1_h1)
            self.logger.info(t)
            self.add_flow(datapath, 2, eth_h1, act_s1_h1)
            self.add_flow(datapath, 1, eth_h2, act_s1_h2)
            self.add_flow(datapath, 2, eth_h2, act_s1_h2)
        elif dpid == 1:
            # set output ports when routing to specific destinations
            act_s2_h1 = [ofp_parser.OFPActionOutput(s2_p_s1)]
            act_s2_h2 = [ofp_parser.OFPActionOutput(s2_p_h2)]
            self.add_flow(datapath, 1, eth_h1, act_s2_h1)
            self.add_flow(datapath, 2, eth_h1, act_s2_h1)
            self.add_flow(datapath, 1, eth_h2, act_s2_h2)
            self.add_flow(datapath, 2, eth_h2, act_s2_h2)

        self.logger.info('*****************************')


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
