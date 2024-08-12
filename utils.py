
# Some random utility functions.

import random

def is_float_or_num(string) -> bool: # Returns true if a string represents an integer or a float.
	if string.replace('.','',1).replace('-','',1).isdigit() and string.count(".") <= 1: # Floats can only have one period character.
		return True
	return False

def is_float(string) -> bool: # Returns true if a string represents a float.
	if string.replace('.','',1).replace('-','',1).isdigit() and string.count(".") == 1: # Floats can only have one period character.
		return True
	return False

# is_int

def is_int(string) -> bool: # Returns true if a string represents an integer.
	if string.replace('.','',1).replace('-','',1).isdigit() and string.count(".") == 0: # Floats can only have one period character.
		return True
	return False

def c(chance: float) -> bool: # Check chance.
	return random.random() <= chance
