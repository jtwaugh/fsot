from contenders import contenders
from arc import Arc, Label
from collections import Counter
from fst import FST
from build_fst import fst_from_prohibited_string, fst_intersect
from harmony import filter_for_hard_constraints
import re

ot_inf = 'inf'
ot_max = 'max'
ot_dep = 'dep'
ot_noc = 'noc'
ot_ons = 'ons'
ot_tf = 'tf'
test = 'test'
default = 'def'

# Debug stuff

debug_alphabet = {'A', 'B'}	
debug_ranking = [ ot_dep, ot_max, 'no_aa', 'no_abab' ]

debug_max = FST( {1}, 1, {1}, { Arc(1, 1, Label('A', '', Counter({ot_max : 1}))), Arc(1, 1, Label('B', '', Counter({ot_max : 1}))), Arc(1, 1, Label('A', 'A', Counter())), Arc(1, 1, Label('B', 'B', Counter())), Arc(1, 1, Label('', 'A', Counter())), Arc(1, 1, Label('', 'B', Counter())) }, 1 )
debug_dep = FST( {1}, 1, {1}, { Arc(1, 1, Label('A', '', Counter())), Arc(1, 1, Label('B', '', Counter())), Arc(1, 1, Label('A', 'A', Counter())), Arc(1, 1, Label('B', 'B', Counter())), Arc(1, 1, Label('', 'A', Counter({ot_dep : 1}))), Arc(1, 1, Label('', 'B', Counter({ot_dep : 1}))) }, 1 )
debug_no_aa = fst_from_prohibited_string(debug_alphabet, debug_alphabet, "AA", 'no_aa')
debug_no_abab = fst_from_prohibited_string(debug_alphabet, debug_alphabet, "ABAB", 'no_abab')

fst_debug = fst_intersect(debug_no_aa, fst_intersect(fst_intersect(debug_max, debug_dep), debug_no_abab))

# Kinyarwanda stuff

tone_ranking = [  ot_max, ot_dep, ot_tf, 'pfl', 'ar' ]

tone_input_alphabet = {'H', 'L',  '.', '#', '>', '<', '|'}
tone_output_alphabet = {'H', 'M', 'L', '.', '#', '>', '<', '|'}

# Hardcoded faithfulness - tone height alternations and max and dep
fst_tone_faith = FST( {1}, 1, {1}, { Arc(1, 1, Label('', 'L', Counter({ot_dep : 1}))), Arc(1, 1, Label('', 'M', Counter({ot_dep : 1}))), Arc(1, 1, Label('', 'H', Counter({ot_dep : 1}))), Arc(1, 1, Label('H', '', Counter({ot_max : 1}))),  Arc(1, 1, Label('L', '', Counter({ot_max : 1}))), Arc(1, 1, Label('.', '', Counter({ot_max : 1}))), Arc(1, 1, Label('H', 'L', Counter({ot_tf: 2}))), Arc(1, 1, Label('L', 'H', Counter({ot_tf: 2}))), Arc(1, 1, Label('H', 'M', Counter({ot_tf: 1}))), Arc(1, 1, Label('M', 'H', Counter({ot_tf: 1}))), Arc(1, 1, Label('M', 'L', Counter({ot_tf: 1}))), Arc(1, 1, Label('L', 'M', Counter({ot_tf: 1}))), Arc(1, 1, Label('.', '.', Counter())), Arc(1, 1, Label('L', 'L', Counter())), Arc(1, 1, Label('H', 'H', Counter())), Arc(1, 1, Label('#', '#', Counter())), Arc(1, 1, Label('>', '>', Counter())), Arc(1, 1, Label('<', '<', Counter())), Arc(1, 1, Label('|', '|', Counter())) }, 1 )

fst_phrase_final_lowering1 = fst_from_prohibited_string(tone_input_alphabet, tone_output_alphabet, "H<", 'pfl')
fst_phrase_final_lowering2 = fst_from_prohibited_string(tone_input_alphabet, tone_output_alphabet, "M<", 'pfl')
fst_phrase_final_lowering = fst_intersect(fst_phrase_final_lowering1, fst_phrase_final_lowering2)

fst_anticipatory_raising1 = fst_from_prohibited_string(tone_input_alphabet, tone_output_alphabet, "LH", 'ar')
fst_anticipatory_raising2 = fst_from_prohibited_string(tone_input_alphabet, tone_output_alphabet, "L.H", 'ar')
fst_anticipatory_raising3 = fst_from_prohibited_string(tone_input_alphabet, tone_output_alphabet, "L#H", 'ar')
fst_anticipatory_raising = fst_intersect(fst_intersect(fst_anticipatory_raising1, fst_anticipatory_raising2), fst_anticipatory_raising3)


# Assemble the FST
fst_kinyarwanda = fst_intersect(fst_tone_faith, fst_intersect(fst_anticipatory_raising, fst_phrase_final_lowering))

# Main routine

while True:
	input_form = raw_input("Enter input tonal pattern.\n\n>    ")
	set_contenders = contenders(fst_kinyarwanda, input_form, tone_input_alphabet, tone_ranking)
	print ("Contenders: \n" + set_contenders.__str__())
