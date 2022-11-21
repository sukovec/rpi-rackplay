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
	DISPLAYON   = 0b10101111
	DISPLAYOOFF = 0b10101110
	ENTIREON    = 0b10100101
	ENTIREOFF   = 0b10100101

	# configuring write address:
	SETCOLHI   = 0b00010000 # last 3 bits = highest 3 bits of the address
	SETCOLLO   = 0b00000000 # last 4 bits = lowest 4 bits of the address
	SETROW	   = 0b01000000 # last 6 bits = row address
	
	SETCONTRAST= 0b10000001 # next "command" shall be actual contrast (whole byte)
	SEGREMAP   = 0b10100000 # last bit rotates display
	SETREVERS  = 0b10100110 # last bit reverses the pixel value

	SETDCDC0   = 0b10101101
	SETDCDC1   = 0b10000000 # last four bits are F2, F1, F0 (switch frequency) and D (enable DC-DC conversion)

	SETSTLINE  = 0b01000000

	SETMUXRATIO= 0b10101000
	COMOUTDIR  = 0b11000000

	DISPOFFSET = 0b11010011


class sh1122(greyscale_device):
	def __init__(self, serial_interface=None, width=256, height=64, rotate=0, mode="RGB", framebuffer=full_frame(), **kwargs):
		print("sh1122::__init__")
		super().__init__(ssh1122_const, serial_interface, width, height, rotate, mode, framebuffer, nibble_order = 0, **kwargs)

	def command(self, *args):
		print("sh1122::command ", list(hex(x) for x in args))
		return super().command(*args)
	
	def _supported_dimensions(self):
		print("sh1122::_supported_dimensions")
		return [ (256, 64) ] # I don't know about anything other...

	def _init_sequence(self):
		print("sh1122::_init_sequence")
		self.command(self._const.DISPLAYON | 0x00);
		self.command(self._const.SETCOLLO)
		self.command(self._const.SETCOLHI)  # horizontal
		self.command(self._const.SETROW, 0)
		# resolution and layout
		self.command(self._const.SETSTLINE | 0x00)
		self.command(self._const.SEGREMAP)
		self.command(self._const.SETMUXRATIO, self.height - 1)
		self.command(self._const.COMOUTDIR)  # scan from COM0 to COM[N]
		self.command(self._const.DISPOFFSET, 0x00)
		self.command(0b11010101, 0b11110000) # WTF?
		# display
		self.command(self._const.SETCONTRAST, 0x80)  # median
		self.command(self._const.ENTIREON)  # output follows RAM contents
		self.command(self._const.SETREVERS)  # not inverted
		self.command(self._const.DISPLAYON)
		pass

	def _set_position(self, top, right, bottom, left):
		print("sh1122::_set_position({}, {}, {}, {})".format(top, right, bottom, left))

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
		print("sh1122::display")

		assert image.mode == self.mode
		assert image.size == self.size

		image = self.preprocess(image)

		for image, bounding_box in self.framebuffer.redraw(image):
			left, top, right, bottom = bounding_box
			width = right - left
			height = bottom - top
			print("  forcycle left={} top={} right={} bottom={}".format(left, top, right, bottom))

			buf = bytearray(width * height >> 1)

			#self.command(self._const.SETCOLLO)
			#self.command(self._const.SETCOLHI)
			#self.command(self._const.SETROW, 20)
			self._populate(buf, image.getdata())

			with open("/home/player/kocky.img", "rb") as f:
				buffer = bytearray(f.read())
				self.data(buffer)

	def cleanup(self):
		print("sh1122::cleanup()")
		self.command(self._const.ENTIREOFF) # to be abso-fucking-lutely sure
		super().cleanup() # .. and this should call DISPLAYOFF command
