#!/usr/bin/env python

from luma.core.interface.serial import spi
import spidev
import RPi.GPIO as gpio

import time

gpio.setmode(gpio.BCM)

dev = spi(spi = spidev.SpiDev(), gpio = gpio, transfer_size = 4096)

SET_COL_ADR_LSB = 0X0
SET_COL_ADR_MSB = 0X10
SET_DISP_START_LINE = 0X40
SET_CONTRAST = 0X81
SET_SEG_REMAP = 0XA0
SET_ENTIRE_ON = 0XA4
SET_ENTIRE_OFF= 0XA5
SET_NORM_INV = 0XA6
SET_MUX_RATIO = 0XA8
SET_CTRL_DCDC = 0XAD
SET_DISP = 0XAE
SET_ROW_ADR = 0XB0
SET_COM_OUT_DIR = 0XC0
SET_DISP_OFFSET = 0XD3
SET_DISP_CLK_DIV = 0XD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_VSEG_LEVEL = 0XDC
SET_DISCHARGE_LEVEL = 0X30

width = 256
height = 64
pages = height // 2

import random

buffer = bytearray([0x00] * (width * height // 2))
#buffer = bytearray(random.randbytes(width * height // 2))
with open("/home/player/kocky.img", "rb") as f:
	buffer = bytearray(f.read())

for cmd in (
	SET_DISP | 0x00,  # off
	# address setting
	SET_COL_ADR_LSB,
	SET_COL_ADR_MSB,  # horizontal
	SET_ROW_ADR, 0,
	# resolution and layout
	SET_DISP_START_LINE | 0x00,
	SET_SEG_REMAP,
	SET_MUX_RATIO,
	height - 1,
	SET_COM_OUT_DIR,  # scan from COM0 to COM[N]
	SET_DISP_OFFSET,
	0x00,
	0b11010101,
	0b11110000,
	# display
	SET_CONTRAST,
	0x80,  # median
	SET_ENTIRE_ON,  # output follows RAM contents
	SET_NORM_INV,  # not inverted
	SET_DISP | 0x01,
	):  
    dev.command(cmd)


import atexit
def exit_handler():
	dev.command(SET_DISP)
	dev.command(SET_CONTRAST)
	dev.command(0)
	gpio.cleanup()
	print("no?")
atexit.register(exit_handler)


def setpixel(buf, x, y):
	cpix = buf[(y * width + x) // 2]
	if x % 2 == 1:
		buf[(y * width + x) // 2] = cpix & 0xf0 | 0x0f
	else:
		buf[(y * width + x) // 2] = cpix & 0x0f | 0xf0
	#buf[(y * width + x) // 2] = 0xf0 if x % 2 == 0 else 0x0f


num = 0
while True:
	setpixel(buffer, num, 5)
	dev.data(buffer)
	num = num + 1
	time.sleep(1)
	print("x")
	

for i in range(0, 256):
	setpixel(buffer, i, 31)
	setpixel(buffer, i, 0)
	setpixel(buffer, i, 62)
for i in range(0, 64):
	setpixel(buffer, 0, i)
	setpixel(buffer, 127, i)
	setpixel(buffer, 255, i)
for i in range(0, 256):
#	for cmd in ( SET_COL_ADR_LSB + (i & 0xf), SET_COL_ADR_MSB + ((i >> 4) & 0x7), SET_ROW_ADR, 0):
#		dev.command(cmd)
	#time.sleep(0.)
	dev.data(buffer)

time.sleep(1)
