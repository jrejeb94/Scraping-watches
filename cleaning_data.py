# import csv
# import fileinput
import re

file = "D:/Extra_Projects/watches/philips_auctions1.csv"
fout = open('D:/Extra_Projects/watches/philips_out.csv', 'wb')
with open(file, 'rb') as csvfile:
    new_file = ''
    i = 0
    for line in csvfile:
        line = line.decode("utf-8")
        test = True
        while test:
            test = False
            if '\t' in line or '       ' in line:
                line = line.replace('                              \n        ', ';')
                line = line.replace('  ', '')
                line = line.replace('\t', '')
                test = True
            if '\n' in line:
                line = line.replace('\n', '')
                test = True
        # # line = line.decode("utf-8")
        # line = line.replace(' ""', " '")
        # line = line.replace('"" ', "'' ")
        # line = line.replace('","",', '"," ",')
        # line = line.replace(',"","",', '," "," ",')
        # line = line.replace('"",', "' ,")
        line = line.replace('","","","', '","')
        # line = line.replace('"".', "'.")
        # line = line.replace('","""', '"," ')
        # line = line.replace('""","', ' ","')
        # line = line.replace('","","', '"," ","')
        # line = line.replace('\n', '')
        # line = line.replace(",' ,", ',')
        i += 1
        if i == 1:
            line = line.replace(',', ';')
            line = line.replace(';pages;pages-href', '')
            first_line = line+'\n'
        else:
            new_file = new_file + line

    lines = re.split('""1', new_file)
    join_line = first_line
    for line in lines:
        cells = line[1:].split('","')
        join_line += ';'.join(cells) + '\n'

    fout.write(join_line.encode("utf-8"))

fout.close()



