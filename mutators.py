
# This file defines the actual data modification functions.

from utils import *
import random
import string

FLOAT_CHANCE = 0.5 # Probability to return a float from the next function.
MAX_INTEGER = 100000000000000


def numeric() -> str: # Return an integer or a float.
	if c(FLOAT_CHANCE): # Return a float.
		return str(random.randrange(-MAX_INTEGER, MAX_INTEGER)) + "." + str(random.randrange(MAX_INTEGER))
	return str(random.randrange(-MAX_INTEGER, MAX_INTEGER)) # Return integer.


MAX_RAND_STRING_LENGTH = 100

alphabet = string.ascii_letters

def rand_string() -> str:
	return "".join([random.choice(alphabet) for _ in range(random.randrange(MAX_RAND_STRING_LENGTH))])

def mut_string(string: str) -> str: # Mutate string.

	if isinstance(string, bytes): # First convert to utf-8
		string = string.decode("utf-8")

	if is_float_or_num(string):
		# Mutate number.
		return numeric()#.encode("utf-8")



	return rand_string()#.encode("utf-8")


