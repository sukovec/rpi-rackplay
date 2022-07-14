#!/usr/bin/env python

from smbus import SMBus

bus = SMBus(1)

init = [ 0x8d, 0x14, 0xaf, 0x20, 0x00, 0x21, 0x00, 127, 0x22, 0, 7 ]

bus.write_i2c_block_data(0x3c, 0x80, init)

fb = [0] * 1024
x = 16 & 0x7f
y = 16 & 0x3f

fb[((y & 0xf8) << 4) + x] = 255

send = fb + [ 0x40 ]

for i in range(0, 1025, 16):
    bus.write_i2c_block_data(0x3c, send[i], send[i+1:i+15])
