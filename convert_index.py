import pickle

# file = input('Enter name of extracted multistream index text file : ')
infile = 'multistream_index.txt'
outfile = 'wiki_index.pkl'

with open(infile, 'r') as f:
    data = f.readlines()

page_names = {line.split(':')[2][:-1] for line in data}

with open(outfile, 'wb') as f:
    pickle.dump(page_names, f)
