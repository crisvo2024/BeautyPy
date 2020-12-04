for line in lines:
   if line.startswith('\t'):
        for char in range(len(line)):
    		if line[char] == '\t':
    	    	line.replace('\t','    ',1)
    	    else:
				break