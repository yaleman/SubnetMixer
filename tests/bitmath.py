#!/usr/bin/python

from bitstring import BitArray, BitStream

slash24 = BitStream( "11111111111111111111111100000000" )

print slash24
print slash24.bin
"""
##################################################
255.255.255.1/24
True
dumping binary
Address: 	0b11111111111111111111111100000001
Netmask: 	0b11111111111111111111111100000000
Wildcard: 	0b11111111
Netaddrs: 	in development

##################################################
192.168.0.2/25
True
dumping binary
Address: 	0b11000000101010000000000000000010
Netmask: 	0b11111111111111111111111110000000
Wildcard: 	0b1111111
Netaddrs: 	in development

##################################################
0.0.0.0/0
True
dumping binary
Address: 	0b0
Netmask: 	0b0
Wildcard: 	0b11111111111111111111111111111111
Netaddrs: 	in development

##################################################
10.2.3.4/32
True
dumping binary
Address: 	0b1010000000100000001100000100
Netmask: 	0b11111111111111111111111111111111
Wildcard: 	0b0
Netaddrs: 	in development
"""

