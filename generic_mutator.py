
import random
import string as string_mod # string.printable

MAX_REPEAT_COUNT = 20

def remove_substring(string: str) -> str:
	start_index = random.randrange(max(len(string)-1, 1))
	end_index = random.randrange(start_index, len(string))
	return string[:start_index] + string[end_index:]

def multiply_substring(string: str) -> str:
	start_index = random.randrange(max(len(string)-1, 1))
	end_index = random.randrange(start_index, len(string))
	substr = string[start_index:end_index]
	where_to_place = random.randrange(max(len(string)-1, 1))
	return string[:where_to_place] + (substr * random.randrange(MAX_REPEAT_COUNT)) + string[where_to_place:]

def add_character(string: str) -> str:
	#if len(string)-1 >= 1:

	where_to_place = random.randrange(max(len(string)-1, 1))
	
	return string[:where_to_place] + random.choice(string_mod.printable) + string[where_to_place:]

def mutate_generic(string: str) -> str: # Mutate a string.

	strat = random.randrange(3)

	match strat:
		case 0:
			# Remove substring
			return remove_substring(string)
		case 1:
			# Multiply substring.
			return multiply_substring(string)
		case 2:
			# Add a character somewhere
			return add_character(string)
		case _:
			print("Invalid")
			assert False
	print("Invalid")
	assert False


