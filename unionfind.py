class UnionFind():

	def __init__(self, elements):
		self.sets = []
		for e in elements:
			self.sets.append(set([e]))

	def __getitem__(self, obj):
		for e in self.sets:
			if (obj in e):
				return e
		return set([])

	def __repr__(self):
		return self.sets.__repr__()

	def merge(self, a, b):
		# Sanity check
		if len(self.sets) == 0:
			return
		merge_target = self.sets[0]
		# Naive search
		for e in self.sets:
			if (a in e):
				merge_target = e
		for f in self.sets:
			if (b in f) and f != merge_target:
				merge_target |= f
				self.sets.remove(f)