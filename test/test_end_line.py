for line, index in enumerate(lines):
    if index == len(lines-1):
        if line[index] == '\n':
            line.replace('\n', '')