
import sys
import xml.etree.ElementTree as ET # For parsing XML
from select_random_node import *
from attribute_handlers import *

test_data = '''<note>
<to>Tove</to>
<from>Jani</from>
<heading><somestuff>fefefe</somestuff></heading>
<body>Don't forget me this weekend!</body>
</note>'''

def test_get_all_paths():
	# get_all_paths_recursive
	root = ET.fromstring(test_data)
	res = get_all_paths(root)
	assert res == [[], [0], [1], [2], [2, 0], [3]]
	print("[+] test_get_all_paths passed!")
	return

# def split_transformations(transformation_string: str) -> list: # Split on stuff.

def test_split_transformation():
	test_data = "rotate(-10 50 100) translate(-36 45.5) skewX(40) scale(1 0.5)"
	res = split_transformations(test_data)
	print("res == "+str(res))
	assert res == ["rotate(-10 50 100)", "translate(-36 45.5)", "skewX(40)", "scale(1 0.5)"]
	print("[+] test_split_transformation passed!")


def test_gen_transformation():

	for _ in range(100):
		print(gen_transformation())

	return

def test_path_handler():

	for _ in range(100):

		print(path_handler(""))

	return

def test_points_handler():

	for _ in range(100):
		print(points_handler(""))
	return

if __name__=="__main__":

	test_get_all_paths()
	test_split_transformation()
	test_gen_transformation()
	test_path_handler()
	test_points_handler()

	print("[+] All tests passed!!!")

	exit(0)
