
# This file is responsible to generate different colors.

import random

all_colors = ["black", "red", "blue", "navy"] # Just some colors

def hex_gen():
	res = "#" + "".join([str(hex(random.randrange(16)))[2:] for _ in range(6)])
	assert len(res) == 7
	return res

def hsl_gen(): # HSL generation
	thing = random.randrange(0xff)
	percent_one = random.randrange(101)
	percent_two = random.randrange(101)

	return "hsl("+str(thing)+", "+str(percent_one)+"%, "+str(percent_two)+"%)"

def normal_string(): # Just some color string.
	return random.choice(all_colors) # Just select some random color

def color_gen():
	gen_funcs = [normal_string, hsl_gen, hex_gen]
	rand_gen_func = random.choice(gen_funcs) # Get a random color generation function.
	return rand_gen_func()

