# -*- coding: utf-8 -*-
# Copyright (c) 2014-20 Richard Hull and contributors
# See LICENSE.rst for details.

from time import sleep
from luma.core.device import device, parallel_device
from luma.core.virtual import character
from luma.oled.device.greyscale import greyscale_device
import luma.core.error
from luma.core.framebuffer import full_frame
from luma.core.bitmap_font import embedded_fonts
import luma.oled.const as const
from luma.oled.device.framebuffer_mixin import __framebuffer_mixin

__all__ = [ "sh1122" ]

class ssh1122_const(const.common): # copying datashit: https://www.displayfuture.com/Display/datasheet/controller/SH1122.pdf
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


class sh1122(greyscale_device):
	def __init__(self, serial_interface=None, **kwargs):
		super().__init__(ssh1122_const, serial_interface, 256, 64, 0, "RGB", full_frame(), nibble_order = 0, **kwargs)

	def command(self, *args):
		return super().command(*args)
	
	def _supported_dimensions(self):
		return [ (256, 64) ] # I don't know about anything other...

	def _init_sequence(self):
		for cmd in (
			self._const.SET_DISP | 0x00,  # off
			# address setting
			self._const.SET_COL_ADR_LSB,
			self._const.SET_COL_ADR_MSB,  # horizontal
			self._const.SET_ROW_ADR, 0,
			# resolution and layout
			self._const.SET_DISP_START_LINE | 0x00,
			self._const.SET_SEG_REMAP,
			self._const.SET_MUX_RATIO,
			self.height - 1,
			self._const.SET_COM_OUT_DIR,  # scan from COM0 to COM[N]
			self._const.SET_DISP_OFFSET,
			0x00,
			0b11010101,
			0b11110000,
			# display
			self._const.SET_CONTRAST,
			0x80,  # median
			self._const.SET_ENTIRE_ON,  # output follows RAM contents
			self._const.SET_NORM_INV,  # not inverted
			self._const.SET_DISP | 0x01,
		):  
			self.command(cmd)

		pass

	def _set_position(self, top, right, bottom, left):
		pass

	def display(self, image):
		"""
		Takes a 1-bit monochrome or 24-bit RGB image and renders it
		to the greyscale OLED display. RGB pixels are converted to 8-bit
		greyscale values using a simplified Luma calculation, based on
		*Y'=0.299R'+0.587G'+0.114B'*.
		:param image: the image to render
		:type image: PIL.Image.Image
		"""

		assert image.mode == self.mode
		assert image.size == self.size

		image = self.preprocess(image)

		for image, bounding_box in self.framebuffer.redraw(image):
			left, top, right, bottom = bounding_box
			width = right - left
			height = bottom - top

			buf = bytearray(width * height >> 1)

			#self.command(self._const.SETCOLLO)
			#self.command(self._const.SETCOLHI)
			#self.command(self._const.SETROW, 20)
			self._populate(buf, image.getdata())
			self.data(buf)


	def cleanup(self):
		print("sh1122::cleanup()")
		self.command(self._const.SET_ENTIRE_OFF) # to be abso-fucking-lutely sure
		super().cleanup() # .. and this should call DISPLAYOFF command
