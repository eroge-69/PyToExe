def remove_blank_lines(Labdata.txt, Output.txt):
    with open(Labdata.txt, 'r') as infile, open(Output.txt, 'w') as outfile:
        for line in infile:
            if line.strip():  # Only write non-blank lines
                outfile.write(line)
