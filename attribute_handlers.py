
# These are the specific mutators for specific attributes.

from utils import *
from mutators import *
from color import *
import mutators
import strict_values

# numeric


def split_transformations(transformation_string: str) -> list: # Split on stuff.

	cut_indexes = []

	in_brace = False

	for i, char in enumerate(list(transformation_string)):
		if char == " " and not in_brace: # We are not in brackets and we have encountered a space character, therefore split on this index.
			cut_indexes.append(i)
		elif char == "(":
			#assert in_brace == False # We shouldn't find another opening brace when we have already encountered it without a closing brace.
			in_brace = True
		elif char == ")":
			#assert in_brace == True
			in_brace = False

	cut_indexes = [0] + cut_indexes + [1000000]

	# Thank you to https://stackoverflow.com/a/10851479 !!!!
	#print("cut_indexes == "+str(cut_indexes))
	res = [((transformation_string))[cut_indexes[i]+1:cut_indexes[i+1]] for i in range(len(cut_indexes)-1)]
	#print("res == "+str(res))
	#assert res[0][0] == " "
	if res == "": # The result is an empty string, just return empty
		return [""]
	if transformation_string == "":
		return [res[0]]
	res[0] = transformation_string[0] + res[0]

	return res

def gen_one_trans_func(): # Generate one transformation function expression.

	funcs_and_num_of_arguments = {"matrix" : 6, "translate": 2, "scale": 2, "rotate": 3, "skewX": 1, "skewY": 1}

	rand_func = random.choice(list(funcs_and_num_of_arguments.keys()))
	num_args = funcs_and_num_of_arguments[rand_func]

	args = [mutators.numeric() for _ in range(num_args)] # Create argument strings.
	return rand_func + "(" + " ".join(args)+")"





def gen_transformation():

	

	#if not original_transformation: # Create an entirely new transformation.
	#	return

	# numeric creates a random thing.

	amount_of_expressions = random.randrange(1, 5)

	out = []

	for _ in range(amount_of_expressions):
		out.append(gen_one_trans_func())

	return " ".join(out)




def gen_color(original: str): # Generate a random color.
	return color_gen()



def mut_transform(original: str) -> str: # "transform" attribute
	# https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform

	# Select strategy. (Add, remove or modify)

	strat = random.randrange(2)

	match strat:
		case 0:
			# Add
			new_func_expr = gen_one_trans_func() # Generate a new expression
			return original + " " + new_func_expr
		case 1:
			# First split the original one.

			function_statements = split_transformations(original)

			# Remove a random one from them.

			function_statements.pop(random.randrange(len(function_statements)))

			res = " ".join(function_statements) # Join them back together.

			return res
			# Remove
		case 2:
			# Modify (I don't think we even need to implement this one.)
			return
		case _:
			# Invalid
			print("Fuck!")
			assert False


	print("Fail!")
	assert False 


def generate_comma_list():

	max_terms = 5 # Maximum number of subsequent things.

	num_vals = random.randrange(1, max_terms)

	return ",".join([mutators.numeric() for _ in range(num_vals)])



MAX_PATH_TERMS = 10

def path_handler(original: str): # Generate a "path" expression.

	path_alphabet = "MmLlHhVvCcSsQqTtAaZz" # All valid path commands.

	path_terms = random.randrange(1, MAX_PATH_TERMS)

	out = []

	for _ in range(path_terms):

		# First the operator.

		out.append(random.choice(path_alphabet))

		# Then the "arguments" aka the comma separated list of values.

		out.append(generate_comma_list())

	return " ".join(out)



def points_handler(original: str): # Generate a list of points.
	num_points = random.randrange(1, 100)
	out = []
	for _ in range(num_points):
		out.append(str(mutators.gen_int())+","+str(mutators.gen_int()))
	return " ".join(out)



attribute_funcs = {"transform": mut_transform,
					"stroke": gen_color,
					"flood-color": gen_color,
					"lighting-color": gen_color,
					"d": path_handler,
					"points": points_handler}

