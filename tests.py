
import sys
import xml.etree.ElementTree as ET # For parsing XML
from select_random_node import *

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

if __name__=="__main__":

	test_get_all_paths()

	print("[+] All tests passed!!!")

	exit(0)
