
import sys
import xml.etree.ElementTree as ET # For parsing XML
import random
from select_random_node import *
from mutators import *

def mutate_node(node_to_mutate, parent_node): # Mutate the node.
	# Now select strategy. For now, just modify the attributes.
	attributes = node_to_mutate.attrib # List of attributes.
	# Select one randomly.
	print("attributes == "+str(attributes))
	print("list(attributes) == "+str(list(attributes)))
	rand_attrib = random.choice(list(attributes))
	print("Selected random attribute: "+str(rand_attrib))
	print("attributes[rand_attrib] == "+str(attributes[rand_attrib]))
	prev_type = str(type(attributes[rand_attrib]))
	print("prev_type == "+str(prev_type))
	attributes[rand_attrib] = mut_string(attributes[rand_attrib]) # Mutate string
	print("str(type(attributes[rand_attrib])) == "+str(str(type(attributes[rand_attrib]))))
	assert prev_type == str(type(attributes[rand_attrib]))
	return node_to_mutate

def mutate_tree(tree): # Mutate tree.
	# First select the random node to mutate.
	node_to_mutate, parent_node = select_random_node_func(tree)
	mutate_node(node_to_mutate, parent_node)

def mutate(data: str) -> str: # Main mutation function.

	# First try to parse as xml (SVG is basically XML)
	root = ET.fromstring(data)
	mutate_tree(root) # Modify in-place
	mutated_contents = ET.tostring(root, encoding="utf-8", short_empty_elements=False) # Convert back to string representation. Preserve empty elements.
	return mutated_contents

if __name__=="__main__":
	# Just take a file from sys.argv[1] and then open it, then mutate it once, then save it in sys.argv[2]

	if len(sys.argv) != 3:
		print("Usage: "+str(sys.argv[0])+" INPUT_SVG_FILE OUTPUT_SVG_FILE")

	infile = open(sys.argv[1], "rb")
	contents = infile.read()
	infile.close()

	contents = contents.decode("utf-8") # Convert to normal string.
	print("contents == "+str(contents))
	print("type(contents) == "+str(type(contents)))
	contents = mutate(contents) # Mutate.
	print("type(contents) == "+str(type(contents)))
	#contents = contents.encode("utf-8") # Convert back to bytes

	# The xml library adds "ns0:" strings everywhere for god knows what reason. I couldn't find anything in the docs about it so just replace all instances of that string with an empty string.


	contents = contents.replace(b"</ns0:", b"</")
	contents = contents.replace(b"<ns0:", b"<")
	contents = contents.replace(b":ns0", b"")

	assert b"ns0" not in contents

	outfile = open(sys.argv[2], "wb")
	outfile.write(contents)
	outfile.close()

	print("[+] Done!")

	exit(0) # Exit

