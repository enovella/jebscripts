import re
import string

PATH   = "/tmp/methodsignatures.txt"
REGEXES = [
			r'.*\([BSI][BSI][BSI]\)Ljava/lang/String;$',
			r'.*\([BSI][BSI]Ljava/lang/String;\)Ljava/lang/String;$',
			r'.*\([BSI]Ljava/lang/String;\)Ljava/lang/String;$',
			r'.*\([BSI]Ljava/lang/String;[BSI]\)Ljava/lang/String;$',	
			r'.*\(Ljava/lang/String;[BSI]\)Ljava/lang/String;$',	
			r'.*\(Ljava/lang/String;[BSI][BSI]\)Ljava/lang/String;$',
			r'.*\([BSI]Ljava/lang/String;\)Ljava/lang/String;$',
	      ]

lines = []
with open(PATH,"r") as f:
	 lines = f.readlines()

for line in lines:
	for regex in REGEXES:
		matches = re.findall(regex, line)
		if matches:
			print str(matches[0]).decode('unicode-escape')

