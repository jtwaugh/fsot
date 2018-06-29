from harmony import otimes
from unionfind import UnionFind
from arc import Label, Arc
from collections import Counter
from fst import FST, dummy_fst

def add_elision_arc(fst, node, in_seg):
	fst.arcs.add(Arc(node, node, Label(in_seg, '', Counter())))

def add_epenthesis_arc(fst, start, end, out_seg):
	fst.arcs.add(Arc(start, end, Label('', out_seg, Counter())))

def add_alternation_arcs(fst, start, end, in_seg, out_seg):
	if in_seg != '_':
		add_epenthesis_arc(fst, start, end, out_seg)
	fst.arcs.add(Arc(start, end, Label(in_seg, out_seg, Counter())))

def violates_hard_constraint(input_string, arc, layer, length):	
	if layer == length:
		return True
	if (arc.label.output == ''):
		if ((arc.label.input == '.') or (arc.label.input == '#') or (arc.label.input == '|') or (arc.label.input == '>') or (arc.label.input == '<')):
			return True

def states_set_product(m, n):
	return [(p, q) for p in m.states for q in n.states]

def states_mega_product(m, n):
	return [(p, q) for p in states_set_product(m, m) for q in states_set_product(n, n)]

def identical_labels_between(fst_1, start_1, end_1, fst_2, start_2, end_2):
	return [(label_1, label_2) for label_1 in fst_1.labels_between(start_1, end_1) for label_2 in fst_2.labels_between(start_2, end_2) if (label_1.input == label_2.input) and (label_1.output == label_2.output)]

def similar_labels_between(fst_1, start_1, end_1, fst_2, start_2, end_2):
	# Return all label pairs with the same output, indexed by which output
	labels_1 = fst_1.labels_between(start_1, end_1)
	labels_2 = fst_2.labels_between(start_2, end_2)
	symbols = set([label_1.output for label_1 in labels_1] + [label_2.output for label_2 in labels_2])
	labels_lists = []
	for symbol in symbols:
		labels_list = [(label_1, label_2) for label_1 in labels_1 for label_2 in labels_2 if (label_1.output == label_2.output) and label_1.output == symbol]
		if labels_list:
			labels_lists.append(labels_list)
	return labels_lists

def product_state(a, b):
	return a.__str__() + "x" + b.__str__()

def layered_state(a, b):
	return a.__str__() + "y" + b.__str__()

def longest_suffix(s, t):
	# Returns the element in t that is the longest proper suffix of s
	return max(filter(lambda x : (s.endswith(x) and s != x), t), key=(lambda x: len(x)))

def fst_from_prohibited_string(input_alphabet, output_alphabet, banned_string, violation_name):
	length = len(banned_string)
	fst = FST(set([""]), "", set(), set(), "")
	# Add arcs
	if length > 1:
		for i in range(1, length):
			fst.states.add(banned_string[0:i])
			add_alternation_arcs(fst, banned_string[0:i-1], banned_string[0:i], '_', banned_string[i-1])
	# Send a penalty arc to the longest valid suffix
	fst.arcs.add(Arc(banned_string[0:-1], longest_suffix(banned_string, fst.states), Label('_', banned_string[-1], Counter({violation_name: 1}))))
	# Add loopback arcs and return
	for state in fst.states:
		for char in input_alphabet:
			add_elision_arc(fst, state, char)
		for char in fst.chars_not_leaving(state, output_alphabet):
			add_alternation_arcs(fst, state, longest_suffix(state + char, fst.states), '_', char)
	return fst

def traverse_states(state_lookup, start):
	# Crude cycle-finding algorithm returning all states accessible from start
	arc_set = state_lookup[start]
	fst_states = set([arc.end for arc in arc_set])
	arc_set = set.union(*[state_lookup[state] for state in fst_states])
	new_states = set([arc.end for arc in arc_set])
	while not new_states.issubset(fst_states):
		fst_states = set.union(fst_states, new_states)
		arc_set = set.union(*[state_lookup[state] for state in fst_states])
		new_states = set([arc.end for arc in arc_set])
	return fst_states

def fst_intersect(m, n):
	arcs = set()
	state_lookup = dict((product_state(p, q), set()) for p, q in states_set_product(m, n))
	start = product_state(m.start, n.start)
	# Compute arcs for each state pair
	for ((x, y), (z, w)) in states_mega_product(m, n):
		labels_lists = similar_labels_between(m, x, y, n, z, w)
		elision_arcs = set()
		for labels_list in labels_lists:
			arcs_by_input = set()
			for (k, l) in labels_list:
				add_arc = False
				seg = ''
				if k.output == '':
					# Faithfulness constraint; cares about input
					if k.input == l.input:
						if k.input not in elision_arcs:
							add_arc = True
							seg = k.input
							elision_arcs.add(seg)
				elif ((k.input == '_') or (k.input == l.input)) and (l.input not in arcs_by_input):
					# Markedness constraint
					add_arc = True
					seg = l.input
					arcs_by_input.add(seg)
				elif (l.input == '_') and (k.input not in arcs_by_input):
					# Markedness constraint
					add_arc = True
					seg = k.input
					arcs_by_input.add(seg)
				if add_arc:
					intersection_arc = Arc(product_state(x, z), product_state(y, w), Label(seg, k.output, otimes(k.violation, l.violation)))
					arcs.add(intersection_arc)
					state_lookup[intersection_arc.start].add(intersection_arc)
	# Figure out the states reachable from the start
	fst_states = traverse_states(state_lookup, start)
	fst = FST(fst_states, start, fst_states, filter((lambda arc : arc.start in fst_states), arcs), 1)
	return fst