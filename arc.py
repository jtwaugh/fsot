class Label():

	def __init__(self, _input, _output, _violation):
		self.input = _input
		self.output = _output
		self.violation = _violation

	def __repr__(self):
		return "Label(" + self.input.__repr__() + ", " + self.output.__repr__() + ", " + self.violation.__repr__() + ")"

class Arc():

	def __init__(self, _start, _end, _label):
		self.start = _start
		self.end = _end
		self.label = _label

	def __repr__(self):
		return "Arc(" + self.start.__repr__() + ", " + self.end.__repr__() + ", " + self.label.__repr__() + ")"
