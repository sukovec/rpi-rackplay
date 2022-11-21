class DisplayRenderer:
	def __init__(self, **kwargs):
		self.redraw_interval = kwargs.get("redraw_interval", 0)

	def __render__(self, draw, bb, stat):
		raise Exception("Not implemented", "Not implemented")

class StaticTextRenderer(DisplayRenderer):
	''' Just a text displayer

		Usable variables (kwargs) for this renderer:
			disable_scroll: boolean or array indicating which lines should scroll and which no

	'''
	def __init__(self, lines, **kwargs):
		super().__init__(**kwargs)

		self.disable_scroll = kwargs.get('disable_scroll', False)
		self.__original_redraw_interval = self.redraw_interval

		self.lines = lines

	def __render__(self, draw, bb, state):
		if state == None or len(state['scroll']) != len(self.lines):
			state = { 
				'scroll': [ 0 ] * len(self.lines),
				'scrollspeed': [ 2 ] * len(self.lines)
			}

		noscroll = [ self.disable_scroll] * len(self.lines) if type(self.disable_scroll) == bool else self.disable_scroll + [ False ] * (len(self.lines) - len(self.disable_scroll))

		redraw_fast = False
		for idx, line in enumerate(self.lines):
			draw.text((2 - state['scroll'][idx], idx * 12), line, fill="white")
			size = draw.textsize(line)

			# test, if it needs to scroll 
			if size[0] < bb[2] or noscroll[idx]:
				state['scroll'][idx] = 0
				continue

			state['scroll'][idx] = state['scroll'][idx] + state['scrollspeed'][idx]

			if state['scroll'][idx] > size[0] - bb[2] / 1.5 or state['scroll'][idx] < 0:
				state['scrollspeed'][idx] *= -1

			redraw_fast = True

		self.redraw_interval = 1 if redraw_fast else self.__original_redraw_interval

		return state

class CallbackTextRenderer(StaticTextRenderer):
	''' Before displaying text, call a callback

		Usable variables (kwargs) for this renderer:
			redraw_callback: call the callback before every redraw

	'''

	def __init__(self, cb, **kwargs):
		super().__init__(None, **kwargs)

		self.redraw_callback = kwargs.get('redraw_callback', True)

		self.callback = cb

	def __render__(self, draw, bb, state):
		if state == None or self.redraw_callback:
			self.lines = self.callback()

		return super().__render__(draw, bb, state)
		
