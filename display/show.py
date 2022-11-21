#!/usr/bin/env python

KBDEV='/dev/input/event0'
MPD_SOCKET="/mnt/mpd-state/socket"
MPD_HOST="192.168.0.171"
MPD_PORT=6600
MPD_UNIX = False


VERSION="0.0.0.1"

import spidev
import RPi.GPIO as gpio
from luma.core.interface.serial import spi
from luma.core.render import canvas
from sh1122 import sh1122
#from luma.oled.device import ssd1306
#from luma.emulator.device import asciiblock as thedevice

import socket

from mpd import MPDClient

from menu import MenuControl
from renderers import StaticTextRenderer, CallbackTextRenderer

gpio.setmode(gpio.BCM)
srl = spi(spi = spidev.SpiDev(), gpio = gpio, transfer_size = 4096)
device = sh1122(serial_interface = srl)

#device = ssd1306(serial = i2c(port=1, address=0x3C))
#device = thedevice(256, 64, transform=None, scale=1, mode="1")

with canvas(device) as draw:
	draw.text((30, 10), "initializing", fill="white")

# display initialized and showing "initializing", initialize other subsystems and connections


mpd = MPDClient()
if MPD_UNIX:
	mpd.connect(MPD_SOCKET)
else:
	mpd.connect(MPD_HOST, MPD_PORT)

def screen_network():
	ipa = socket.gethostbyname(socket.gethostname())
	return ( "Network information:", "IP address:", "    " + ipa )

def screen_default():
	stat = mpd.status()
	song = mpd.currentsong()

	error = "error" in stat
	st_repeat = "rep " if stat["repeat"] else "    "
	st_random = "rnd " if stat["random"] else "    "
	st_state = stat["state"] + " | " + st_repeat + st_random

	if song and not error:
		return ( 
			song.get('artist', 'X artist unknown X'),
			song.get('title', 'X title unknown X'),
			'{:02.0f}:{:02d} / {:02.0f}:{:02d}'.format(float(stat['elapsed']) / 60, int(float(stat['elapsed'])) % 60, float(stat['duration']) / 60, int(float(stat['duration'])) % 60), 
			"",
			st_state
			)
	elif error:
		 return ( "!! ERROR !!", error, "", "", st_state )

	else:
		return ( "Playlist empty", "", "", "", st_state )


def current_playlist():
	playlist = mpd.playlistid()
	song = [ '  {} - {}'.format(itm.get('artist', '?'), itm.get('title', '?')) for itm in playlist[0:4] ]

	return [" CURRENT PLAYLIST ", ] + song

screens = ( 
	CallbackTextRenderer(screen_default, redraw_interval = 500), 
	CallbackTextRenderer(screen_network),
	CallbackTextRenderer(current_playlist),
	StaticTextRenderer( ( "Rackpi Player", "Version " + VERSION, "Made by ja, pycho!", "", "<|> sem, <|> tam"))
	)

mc = MenuControl(device, screens, KBDEV)
mc.event_loop()
