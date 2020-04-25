#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Controller for the SDN
'''

import sys

import pox3.lib.packet as pac
from pox3.boot import boot
from pox3.core import core

import pox3.openflow.libopenflow_01 as of

from Blockchain import Blockchain


if __name__ != "__main__":
    LOG = core.getLogger()


class Controller(object):
    '''A controller that can detect attacks or generate data on flows'''
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        self.mac_to_port = {}
        self.blockchain = Blockchain()

    def resend_packet(self, packet_in, out_port):
        '''
        Pass the packet from this switch on to the next port
        :param packet_in: Packet to pass
        :param out_port: Port to pass to
        '''
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def flow_is_allowed(self, flow):
        for b in self.blockchain.chain:
            if b.transactions == flow:
                return True
        return False

    def act_like_switch(self, packet, packet_in):
        '''
        Act like a switch by learning the mappings between the MACs and ports
        :param packet The packet processed at this point
        :param packet_in The packet to pass
        '''
        pl = packet.payload
        if len(packet_in.data) == packet_in.total_len:
            self.mac_to_port[packet.src] = packet_in.in_port
            if isinstance(pl, pac.ipv4):
                if pl.protocol == pac.ipv4.TCP_PROTOCOL:
                    src = pl.srcip
                    dst = pl.dstip
                    flow = f"{src} -> {dst}"
                    tcp_pl = pl.next.payload.decode()
                    if tcp_pl.find("GET") == 0:
                        route = tcp_pl[4:tcp_pl.find("HTTP") - 1]
                        if "data" in route:
                            if not self.flow_is_allowed(flow):
                                LOG.debug("Flow %s is not allowed", flow)
                                return
                        elif "add" in route:
                            if self.blockchain.mine(flow):
                                LOG.debug("Added acceptable flow %s", flow)
                            else:
                                return
            if self.mac_to_port.get(packet.dst):
                self.resend_packet(packet_in, self.mac_to_port[packet.dst])
            else:
                self.resend_packet(packet_in, of.OFPP_ALL)

    def _handle_PacketIn(self, event):
        '''
        Handle a packet in
        :param event Event that triggered this
        '''
        packet = event.parsed
        if not packet.parsed:
            LOG.warning("Ignoring incomplete packet")
        else:
            packet_in = event.ofp
            self.act_like_switch(packet, packet_in)


def launch():
    '''
    Launch this controller
    '''
    def start_switch(event):
        '''
        Start up the switch
        :param event Event that triggered this
        '''
        LOG.debug("Controlling %s with this", (event.connection,))
        Controller(event.connection,)
    core.openflow.addListenerByName("ConnectionUp", start_switch)


if __name__ == '__main__':
    boot(
        (["log.level", "--DEBUG"] if "--debug" in sys.argv else []) +
        ["network_controller"]
    )
