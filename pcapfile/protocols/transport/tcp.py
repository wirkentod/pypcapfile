"""
TCP transport definition
"""

import binascii
import ctypes
import struct

class TCP(ctypes.Structure):
    """
    Represents a TCP packet
    """

    _fields_ = [('src_port', ctypes.c_ushort),  # source port
                ('dst_port', ctypes.c_ushort),  # destination port
                ('seqnum', ctypes.c_uint),      # sequence number
                ('acknum', ctypes.c_uint),      # acknowledgment number
                ('data_offset', ctypes.c_uint), # data offset in bytes
                ('urg', ctypes.c_bool),         # URG
                ('ack', ctypes.c_bool),         # ACK
                ('psh', ctypes.c_bool),         # PSH
                ('rst', ctypes.c_bool),         # RST
                ('syn', ctypes.c_bool),         # SYN
                ('fin', ctypes.c_bool),         # FIN
                ('win', ctypes.c_ushort),       # window size
                ('sum', ctypes.c_ushort),       # checksum
                ('opt', ctypes.c_char_p),       # options
                ('payload', ctypes.c_char_p)]   # packet payload

    tcp_min_header_size = 20

    def __init__(self, packet, layers=0):
        fields = struct.unpack("!HHIIBBHHH", packet[:self.tcp_min_header_size])
        self.src_port = fields[0]
        self.dst_port = fields[1]
        self.seqnum = fields[2]
        self.acknum = fields[3]
        
        self.data_offset = 4 * (fields[4] >> 4)

        self.urg = fields[5] & 32
        self.ack = fields[5] & 16
        self.psh = fields[5] & 8
        self.rst = fields[5] & 4
        self.syn = fields[5] & 2
        self.fin = fields[5] & 1

        self.win = fields[6]
        self.sum = fields[7]
        urg_offset = 4 * fields[8] # rarely used

        if self.data_offset < 20:
            self.opt = b''
            self.payload = b''
        else:
            self.opt = ctypes.c_char_p(binascii.hexlify(packet[20:self.data_offset]))
            self.payload = ctypes.c_char_p(binascii.hexlify(packet[self.data_offset:]))

    def __str__(self):
        #packet = 'tcp %s packet from port %d to port %d carrying %d bytes'
        str_flags = ''
        if self.syn: str_flags += 'S'
        if self.ack: str_flags += 'A'
        if self.rst: str_flags += 'R'
        if self.fin: str_flags += 'F'
        if self.urg: str_flags += 'U'
        
	if self.urg:
        	flag_urg = 1
        else:
            	flag_urg = 0
	if self.ack:
            	flag_ack = 1
        else:
            	flag_ack = 0
	if self.psh:
            	flag_psh = 1
        else:
            	flag_psh = 0
	if self.rst:
            	flag_rst = 1
        else:
            	flag_rst = 0
        if self.syn:
            	flag_syn = 1
        else:
            	flag_syn = 0
        if self.fin:
            	flag_fin = 1
        else:
            	flag_fin = 0
        
	# src_port, dst_port | seqnum , acknum, data_offset, urg, ack, psh, rst, syn, fin, win, str_flags
	packet = '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s' % (self.src_port, self.dst_port, self.seqnum, self.acknum, self.data_offset, flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin, self.win, str_flags)
        #packet = '%s;%s;%s;%s' % (self.src_port, self.dst_port, flag_syn, flag_fin)
        #packet = packet % (str_flags, self.src_port, self.dst_port, (len(self.payload) / 2))
        return packet

    def __len__(self):
        return max(self.data_offset, self.tcp_min_header_size) + len(self.payload) / 2

