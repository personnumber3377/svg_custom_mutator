
import sys
import xml.etree.ElementTree as ET # For parsing XML
import random

def get_all_paths_recursive(cur_node, current_path):
	out = [current_path]
	for i, child in enumerate(cur_node): # Loop over all child nodes...
		# print("current_path + [i] == "+str(current_path + [i]))
		# out.append(get_all_paths_recursive(child, current_path + [i]))
		out += get_all_paths_recursive(child, current_path + [i])
	return out


def get_all_paths(tree):
	return get_all_paths_recursive(tree, [])

def select_random_node_func(tree): # Select a random node with equal probability.
	all_paths = get_all_paths(tree)
	ran_path = random.choice(all_paths)
	parent = None # parent node.
	out = tree
	for ind in ran_path:
		parent = out
		out = out[ind] # Traverse the tree according to the randomly chosen path.
	return out, parent
	


