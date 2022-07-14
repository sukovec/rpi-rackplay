from evdev import InputDevice
from select import epoll, EPOLLIN
from linuxfd import timerfd

from luma.core.render import canvas

class KBCODE:
	UP = 259
	DOWN = 256
	RIGHT = 260
	LEFT = 261
	EXIT = 257
	ENTER = 258


class MenuControl:
	def __init__(self, drawdev, menu, kbdev = '/dev/input/event0'):
		self.drawdev = drawdev
		self.menupos = 0
		self.menu = menu

		self.epoll = epoll()

		self.init_timer()
		self.init_keyboard(kbdev)

		self.render_current()

	# ======================================
	# INITIALIZATION OF EVENT LISTENERS ETC
	# ======================================

	def init_keyboard(self, kbdev):
		self.kbinput = InputDevice(kbdev)
		self.epoll.register(self.kbinput.fd, EPOLLIN)

	def init_timer(self):
		self.timer = timerfd(rtc = False)
		self.epoll.register(self.timer.fileno(), EPOLLIN)

	# =======================
	# EVENT LOOP and HANDLERS
	# =======================

	def event_loop(self):
		while True:
			events = self.epoll.poll(1)
			for fileno, event in events:
				self.event_loop_pass(fileno, event)

	def event_keyboard(self, event):
		if event.value != 1:
			return

		match event.code:
			case KBCODE.UP:
				print("UP")
			case KBCODE.DOWN:
				print("DOWN")
			case KBCODE.LEFT:
				self.menupos = self.menupos + 1
				self.render_current()

			case KBCODE.RIGHT:
				print("RIGHT")
			case KBCODE.ENTER:
				print("ENTER")
			case KBCODE.EXIT:
				print("EXIT")

	def event_timer(self):
		pass

	def event_other(self, fileno, event):
		pass

	def event_loop_pass(self, fileno, event):
		if fileno == self.kbinput.fd: # keyb event
			for evt in self.kbinput.read():
				self.event_keyboard(evt)
		elif fileno == self.timer.fileno(): # timer event, just check if needs refresh, then 
			self.event_timer()
		else:
			self.event_other(fileno, event)

	# ================
	# DISPLAY ROUTINES
	# ================

	def display_menu_item(self, drawdev, itm):
		with canvas(drawdev) as draw:
			itm.__render__(draw, drawdev.bounding_box)

	def render_current(self):
		self.display_menu_item(self.drawdev, self.menu[self.menupos])


