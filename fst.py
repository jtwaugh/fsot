from harmony import succ, oplus, otimes, m_otimes, m_oplus, t_unit, t_ann, h_unbounded
from collections import Counter, deque
from arc import Arc, Label
from unionfind import UnionFind
import re

class FST():

	def __init__(self, _states, _start, _end, _arcs, _input_length):
		self.states = _states
		self.start = _start
		self.end = _end
		self.arcs = _arcs
		self.input_length = _input_length

	def __repr__(self):
		return "FST(" + self.states.__repr__() + ", " + self.start.__repr__() + ", " + self.end.__repr__() + ", " + self.arcs.__repr__() + ", " + self.input_length.__repr__() + ")"

	def to_dot(self):
		dot = "digraph {\n"

		for arc in self.arcs:
			dot += "_" + arc.start.__str__() + " -> " + "_" + arc.end.__str__() + "[label=\"" + arc.label.input.__repr__() + " : " + arc.label.output.__repr__() + " , " + arc.label.violation.__repr__()[8:-1] + "\"];\n"
		dot += "}"

		return dot

	def arcs_leaving(self, node):
		return filter(lambda a : (a.start == node), self.arcs)

	def nodes_from(self, node):
		return [arc.end for arc in self.arcs_leaving(node)]

	def arcs_arriving(self, node):
		return filter(lambda a : (a.end == node), self.arcs)

	def external_arcs_arriving(self, node):
		return filter(lambda a : (a.start != node), self.arcs_arriving(node))

	def arcs_between(self, node_from, node_to):
		return filter(lambda a : a.end == node_to, self.arcs_leaving(node_from))

	def labels_between(self, start, end):
		return set(q.label for q in self.arcs_between(start, end))

	def output_char_leaves(self, char, node):
		return filter(lambda a : a.label.output == char, self.arcs_leaving(node))

	def chars_not_leaving(self, node, sigma):
		return filter(lambda char: len(self.output_char_leaves(char, node)) == 0, sigma)

	def states_by_layer(self):
		queue = deque()
		if self.input_length > 0:
			for i in range(0, self.input_length + 1):
				states_in_layer = filter(lambda state : state.__str__().split("y")[1] == i.__str__(), self.states.copy()) 
				queue.append(states_in_layer)
		else:
			queue.append(self.states.copy())
		return queue


def dummy_fst():
	return FST(set([0]), 0, set(), set(), 0)