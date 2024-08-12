
# This file defines the actual data modification functions.

from utils import *
import random
import string
from attribute_handlers import *
import strict_values
from generic_mutator import *

FLOAT_CHANCE = 0.5 # Probability to return a float from the next function.
#MAX_INTEGER = 1000

MAX_INTEGER = (18446744073709551616) * 10 # Some very large number



def gen_float() -> str: # Return an integer or a float.
	return str(random.randrange(-MAX_INTEGER, MAX_INTEGER)) + "." + str(random.randrange(MAX_INTEGER))

def gen_int() -> str: # Return an integer or a float.
	return str(random.randrange(-MAX_INTEGER, MAX_INTEGER)) # Return integer.


def numeric() -> str: # Return an integer or a float.
	if c(FLOAT_CHANCE): # Return a float.
		return str(random.randrange(-MAX_INTEGER, MAX_INTEGER)) + "." + str(random.randrange(MAX_INTEGER))
	return str(random.randrange(-MAX_INTEGER, MAX_INTEGER)) # Return integer.


MAX_RAND_STRING_LENGTH = 100

alphabet = string.ascii_letters

def rand_string() -> str:
	return "".join([random.choice(alphabet) for _ in range(random.randrange(MAX_RAND_STRING_LENGTH))])

def mut_string(string: str, attribute=None) -> str: # Mutate string.

	if isinstance(string, bytes): # First convert to utf-8
		string = string.decode("utf-8")

	if is_float(string):
		# Mutate number.
		return gen_float() #.encode("utf-8")

	if is_int(string):
		return gen_int()


	# gen_float


	# Now we know that the string doesn't represent any kind of numeric value (either integer or float), so let's go through all of the attributes strings and figure out if there are special handlers for them, if not, then just return a completely random string as a fallback.

	if attribute != None: # The attribute string exists.
		
		# First try to lookup at the strict values thing...
		if attribute in strict_values.strict_values_dict.keys():
			possible_vals = (strict_values.strict_values_dict)[attribute]
			return random.choice(possible_vals)

		# Try to lookup a handler.
		#x = 0
		if attribute in attribute_funcs.keys():

			# attribute_funcs is the handlers.

			attribute_handler = attribute_funcs[attribute]

			return attribute_handler(string) # Call the attribute handler.


	return mutate_generic(string) # Just mutate as a regular string instead...

	#return rand_string() #.encode("utf-8")


