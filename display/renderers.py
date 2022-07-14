class DisplayRenderer:
	def __init__(self, **kwargs):
		self.redraw_interval = kwargs.get("redraw_interval", 0)

	def __render__(self, draw, bb, stat):
		raise Exception("Not implemented", "Not implemented")

class StaticTextRenderer(DisplayRenderer):
	def __init__(self, lines, **kwargs):
		super().__init__(**kwargs)
		self.lines = lines
	def __render__(self, draw, bb, state):
		if state == None:
			state = { "scroll": 0 }

		y = 0
		for line in self.lines:
			draw.text((2 - state['scroll'], y), line, fill="white")
			y = y + 12

		return state

class CallbackTextRenderer(StaticTextRenderer):
	def __init__(self, cb, **kwargs):
		super().__init__(None, **kwargs)
		self.callback = cb
	def __render__(self, draw, bb, state):
		self.lines = self.callback()
		return super().__render__(draw, bb, state)
