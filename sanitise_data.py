import os
# This file is for sanitising the data that was scraped
# The data contained some unexpected linebreaks
# This fixes that

files = list(map(lambda x: 'channel_data/' + x, os.listdir('channel_data')))

for file in files[:]:
    os.rename(file, file + '.old')      # Rename files to old to save backup
    tempfile = file

    with open(tempfile, 'w') as tmp:
        with open(file+'.old', "r") as f:

            lines = f.readlines()

            for line in lines:
                chunks = line.split('\\#\\')

                if len(chunks) == 4 or len(chunks) == 1:
                    tmp.write(line[:-1])
                else:
                    tmp.write(line)
