
import os

if __name__=="__main__":

	in_dir = "curl_stuff/"

	files = os.listdir(in_dir)

	strict_vals = {}

	for file in files:
		full_filename = in_dir + file # Prepend the directory...
		attr = file[4:-10]
		#print(attr)
		fh = open(full_filename, "r")
		lines = fh.readlines()
		fh.close()
		#print("="*100)
		for i, line in enumerate(lines):
			#if file in line:
			#	print(line)

			if "Syntax: " in line and "|" in line:
				#print(line)
				line = line[line.index("Syntax: ")+len("Syntax: "):]
				#print(line)
				if "Attribute Values" in line: # Proceed normally...
					line = line[:line.index("Attribute Values")]
					
					if "&" in line:
						continue
					assert "=" in line
					assert line[line.index("=")+1] == " "
					line = line[line.index("=")+2:]
					#print(line)
					possible_values = line.split(" | ")
					print(possible_values)
					strict_vals[attr] = possible_values
				elif ";" in line:
					#print(line)

					line = line[:line.index(";")]
					

					if "Property Values:" in line:
						line = line[:line.index("Property Values:")]

					if "&" in line:
						continue
					print("Fuck fuck: "+str(line))

					line = line[line.index(" "):]

					possible_values = line.split("|")
					print("possible_values == "+str(possible_values))
					for i in range(len(possible_values)):
						val = possible_values[i]
						val = val.replace(" ", "") # Remove space characters.
						possible_values[i] = val
					assert all([" " not in val for val in possible_values])
					#print("Here is the possible values: "+str(possible_values))
					strict_vals[attr] = possible_values

				elif "Property Values:" in line:
					line = line[:line.index("Property Values:")]
					print("Fuck!!!!")
					print("ffffffffffff" + line)
					values = line[line.index(" ")+1:]
					values = values.split(" | ")
					strict_vals[attr] = values
				else:
					print("Here is the entire line: "+str(line))
					#if "</div>" in line:
					#	print("Next line: "+str(lines[i+1]))
					#	print("Next line: "+str(lines[i+2]))
					#	print("Next line: "+str(lines[i+3]))
					#	print("Next line: "+str(lines[i+4]))

				#assert "Attribute Values" in line


		#print("="*100)

	print("Here are the strict values: ")
	print(strict_vals)
	exit(0)

