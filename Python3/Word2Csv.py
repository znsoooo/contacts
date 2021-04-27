# build 20210423

# Convert Word's tables (not paragraphs) to Csv.

# Tips:
# Word's tables are not ideal structured data.
# Use Word to convert is slow and inaccurate,
# Convert from Excel is better.

# TODO
# auto convert doc to docx

import os
import docx


def ReadWord(file):
    doc = docx.Document(file)
    data = []
    for table in doc.tables:
        sheet_data = []
        for row in table.rows:
            row_cells = row.cells
            # unique list
            # row_cells_nui = sorted(list(set(row_cells)), key=row_cells.index) # Good!
            row_cells = [item.text for i, item in enumerate(row_cells) if row_cells.index(item) == i] # Slower but Good!
            sheet_data.append(row_cells)
        data.append(sheet_data)
    return data


def WashData(data):
    for i, item in enumerate(data):
        if isinstance(item, list):
            WashData(item)
        else:
            data[i] = data[i].strip().replace('\n', ' ').replace('\r', ' ').replace(' ', '') # replace after strip
    return data # wash list in place


def WriteTxt(data, file): # Good!
    with open(file, 'w') as f:
        f.write('\n'.join(','.join(row) for row in sum(data, [])))


def Word2Csv(file):
    root, ext = os.path.splitext(file)
    if ext == '.doc':
        file2 = root + '.docx' # only ".docx" type can read
        ...
        file = file2
    data = WashData(ReadWord(file))
    WriteTxt(data, root+'.csv')
    return data


file = '办公电话号码表.docx'
data = Word2Csv(file)

from pprint import pprint
pprint(data[0]) # sheet1
