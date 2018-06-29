from collections import Counter
import itertools
import time
import re

def succ(v, w, ranking):
	for i in range(len(ranking)):
		if (v['inf'] == 0 and w['inf'] > 0):
			return 1
		if (v['inf'] > 0 and w['inf'] == 0):
			return -1
		if (v[ranking[i]] < w[ranking[i]]):
			return 1
		if (v[ranking[i]] > w[ranking[i]]):
			return -1
	return 0

def otimes(v, w):
	if (v['inf'] == 0 and w['inf'] == 0):
		return v + w
	else:
		return Counter({'inf': 1})

def oplus(v, w, ranking):
	if (succ(v, w, ranking) == 1):
		return v
	else:
		return w

def erc(a, b, ranking):
	(aweight, astrset) = a
	(bweight, bstrset) = b
	(a_wins, b_wins) = (0, 0)
	# Sanity check
	if (aweight['inf'] > 0):
		if (bweight['inf'] > 0):
			return (a_wins, b_wins)
		else:
			return (a_wins, 2**(len(ranking)))
	elif (bweight['inf'] > 0):
		return (2**(len(ranking)), b_wins)
	for i in range(len(ranking)):
		if (aweight[ranking[i]] < bweight[ranking[i]]):
			a_wins |= (2**i)
		if (bweight[ranking[i]] < aweight[ranking[i]]):
			b_wins |= (2**i)
	return (a_wins, b_wins)

def consistent(erc_list, ranking):
	if not erc_list:
		return True
	# If there exists any violation that simply beats everything
	if any([all([w & 2**i for (w, l) in erc_list]) for i in range(len(ranking))]):
		return True
	(w_set, l_set) = (0, 0)
	for (w, l) in erc_list:
		w_set |= w
		l_set |= l
	if l_set == 0:
		return True
	if (w_set == 0) or ((~w_set | l_set) == -1):
		return False
	# Evaluate ERC sets - keep e if w(e) \sse l(e_list)
	new_erc_list = [(w, l) for (w, l) in erc_list if (~w | l_set) == -1]
	return consistent(new_erc_list, ranking)

def simply_unbounded(k, klist, ranking):
	(v, w) = k
	for (a, b) in klist:
		# Check if a[r] \geq v[r] in all cases
		bounded = True
 		for r in ranking:
			if v[r] < a[r]:
				bounded = False
		if bounded: 
			return True
	return False

def filter_for_hard_constraints(mylist):
	constraints = re.compile(r'((L|M|H|h){3})|((\.\.)|(>\.)|(\.<)|(#\.)|(\.#)|(#<)|(>#))')
	valid = lambda x : not constraints.search(x)
	return [(v, filter(valid, S)) for (v, S) in mylist]

def h_unbounded(klist, ranking):
	# Filter in a couple passes
	klist = filter((lambda (v, w) : v['inf'] == 0), klist)
	klist = filter(lambda a : simply_unbounded(a, klist, ranking), klist)
	klist = filter_for_hard_constraints(klist)
	return filter((lambda k : consistent([erc(k, k_, ranking) for k_ in klist], ranking)), klist)

def v_to_str(profile):
	if profile['inf'] > 0:
		return "\infty"
	if profile == Counter():
		return "\epsilon"
	# Return an alphabetical string of key-count pairs
	keys = sorted(profile.keys())
	mystring = ""
	for key in keys:
		mystring += key + ":" + profile[key].__str__() + ";"
	return mystring

def str_to_v(mystring):
	# Sanity check
	if (mystring == "\epsilon"):
		return Counter()
	if (mystring == "\infty"):
		return Counter({'inf' : 1})
	kvs = mystring.split(';')
	v = Counter()
	for kv in kvs:
		if (kv != ""):
			k_v = kv.split(':')
			v[k_v[0]] = int(k_v[1])
	return v

def unify_list(klist, ranking):
	# Cast to strings so we can use a set
	strs = set([v_to_str(v) for (v, s) in klist])
	union = []
	# Collect, rebuild the tuples, and return
	for string in strs:
		stringset = set([])
		for (v, s) in klist:
			if(v_to_str(v) == string):
				stringset |= set(s)
		union.append((str_to_v(string), list(stringset)))
	return union

def s_otimes(s1, s2):
	return [t1 + t2 for t1 in s1 for t2 in s2]

def t_ann():
	return [(Counter({'inf' : 1}), [])]

def t_unit():
	return [(Counter([]), [""])]

def t_oplus(a, b, ranking):
	contenders = h_unbounded(unify_list(a + b, ranking), ranking)
	# Sanity check
	if not contenders:
		return t_ann()
	return contenders

def t_otimes(a, b, ranking):
	# Sanity check
	if (not a) or (not b):
		return t_ann()
	contenders = h_unbounded([(otimes(v1, v2), s_otimes(s1, s2)) for (v1, s1) in a for (v2, s2) in b], ranking)
	# Again
	if not contenders:
		return t_ann()
	return contenders	

def m_oplus(m, n, size):
	return [[t_oplus(m[row][column], n[row][column]) for column in range(size)] for row in range(size)]

def m_dot(m, n, row, column, size, ranking):
	m_sum = t_ann()
	for k in range(size):
		m_sum = t_oplus(m_sum, t_otimes(m[row][k], n[k][column], ranking), ranking)
	m_sum = h_unbounded(unify_list(m_sum, ranking), ranking)
	# Sanity check
	if not m_sum:
		m_sum = t_ann()
	return m_sum

def m_rowdot(a, b, size, ranking):
	m_sum = t_ann()
	for k in range(size):
		m_sum = t_oplus(m_sum, t_otimes(a[k], b[k], ranking), ranking)
	return m_sum

def m_otimes(m, n, size, ranking):
	return [[m_dot(m, n, row, column, size, ranking) for column in range(size)] for row in range(size)]	

def m_exponentiate(n, matrix, size, ranking):
	if n == 1:
		return matrix
	# Do this binarily to save cycles
	half = int(n/2)
	other_half = n - n/2
	new_matrix = m_otimes(m_exponentiate(half, matrix, size, ranking), m_exponentiate(half, matrix, size, ranking), size, ranking)
	return new_matrix

def m_equals(m, n, size):
	for row in range(size):
		for column in range(size):
			if m[row][column] != n[row][column]:
				return False
	return True