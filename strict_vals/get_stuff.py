
import os

def get_filename(line):

	assert "geeks.org/" in line
	oof = line[line.index("geeks.org/")+len("geeks.org/"):]
	oof = oof[:oof.index("/")]
	print(oof)
	return oof

if __name__=="__main__":

	fh = open("links.txt", "r")
	lines = fh.readlines()
	fh.close()

	for line in lines:
		line = line[line.index("\"")+1:] # Skip to the start of the link
		line = line[:line.index("\"")]
		print(line)
		cmd = "curl "+str(line)+" > curl_stuff/"+str(get_filename(line))
		print("Running this: "+str(cmd))
		os.system(cmd)


	exit(0)
