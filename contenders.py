from harmony import succ, oplus, otimes, m_otimes, m_oplus, t_unit, t_ann, h_unbounded, unify_list, m_exponentiate
from fst import FST
import time

def char_adjacency_matrix(fst, input_segment, state_array):
	size = len(state_array)
	matrix = []
	counter = 0
	# Build the matrix
	for i in state_array:
		matrix.append([])
		for j in state_array:
			vec = []
			for arc in fst.arcs_between(i, j):
				# Keep only unique entries
				# Check first for the specific character and then for the catchall
				if (arc.label.input == input_segment) and not (arc.label.violation in vec):
					t = (arc.label.violation, [arc.label.output])
					vec.append(t)
				elif (arc.label.input == '_') and not (arc.label.violation in vec):
					t = (arc.label.violation, [arc.label.output])
					vec.append(t)
			# If we can't move, assign infinity as the weight
			if len(vec) == 0:
				vec = t_ann()
			matrix[counter].append(vec)
		counter += 1
	return matrix

def transition_matrix(fst, state_array, ranking):
	lambda_matrix = char_adjacency_matrix(fst, '', state_array)	
	# Not moving is free
	for i in range(len(state_array)):
		lambda_matrix[i][i] = t_unit()
	return m_exponentiate(len(state_array), lambda_matrix, len(state_array), ranking)

def string_adjacency_matrix(fst, state_array, input_string, input_alphabet, ranking):
	lambda_matrix = transition_matrix(fst, state_array, ranking)
	# Index matrices by symbols
	symbol_matrix = dict([(input_segment, m_otimes(char_adjacency_matrix(fst, input_segment, state_array), lambda_matrix, len(state_array), ranking)) for input_segment in input_alphabet])
	# Multiply them and return
	input_matrix = lambda_matrix
	for symbol in input_string[0:]:
		input_matrix = m_otimes(input_matrix, symbol_matrix[symbol], len(state_array), ranking)
	return input_matrix

def contenders(fst, input_string, input_alphabet, ranking):
	state_array = []
	end_columns = []
	start_rows = []
	# Cache terminal states
	k = 0
	for i in fst.states:
		state_array.append(i)
		if i in fst.end:
			end_columns.append(k)
		if i == fst.start:
			start_rows.append(k)
		k += 1
	# Build the matrix
	M = string_adjacency_matrix(fst, state_array, input_string, input_alphabet, ranking)
	# Fetch contenders from the cells
	contenders = []
	for j in end_columns:
		for i in start_rows:
			contenders += M[i][j]
	# Unify, RCD again, and return
	contenders = unify_list(contenders, ranking)
	return h_unbounded(contenders, ranking)