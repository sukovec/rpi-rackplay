class DisplayRenderer:
	def __init__(self):
		pass
	def __render__(self, draw, bb, stat):
		pass

class StaticTextRenderer(DisplayRenderer):
	def __init__(self, lines):
		super().__init__()
		self.lines = lines
	def __render__(self, draw, bb):
		y = 0
		for line in self.lines:
			draw.text((2, y), line, fill="white")
			y = y + 12

class CallbackTextRenderer(StaticTextRenderer):
	def __init__(self, cb):
		super().__init__(None)
		self.callback = cb
	def __render__(self, draw, bb):
		self.lines = self.callback()
		super().__render__(draw, bb)
