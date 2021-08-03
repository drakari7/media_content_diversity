import os
import re

# local imports
import tools as tl
from channel_class import NewsChannel

# Some news channels put some repetitive information
# at the end of every video description, such as links to their socials
# This information is useless for our analysis
# and also pollutes the data with grammatically incorrect sentences
# This script aims to remove them


links = tl.get_temp_links()

for link in links:
    channel = NewsChannel(link)

    data_file = channel.data_file_path
    write_file = data_file + '.new'

    with open(data_file, 'r') as rf:
        lines = rf.readlines()

    count = 0

    with open(write_file, 'w') as wf:
        for line_no, line in enumerate(lines[:], start=1):
            pattern = r"About Us: IndiaTV is the country's most trusted Hindi News Channel"
            chunks = re.split(pattern, line)

            temp = ' '.join(chunks[0].splitlines()).rstrip()
            print(temp, file=wf)

            if len(chunks) > 1:
                count += 1
                # print(line_no)

    print(count)
