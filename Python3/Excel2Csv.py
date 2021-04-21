# build 20210421

# TODO
# auto convert xlsx to xls

import os
import xlrd


def ReadExcel(file):
    # only ".xls" type contain merge_info
    xls = xlrd.open_workbook(file, formatting_info=True)

    data = []
    merge = []
    for sheet in xls.sheets():
        sheet_data = []
        for row in range(sheet.nrows):
            rows = sheet.row_values(row)
            for c, cell in enumerate(rows):
                if isinstance(cell, float):
                    if cell.is_integer():
                        rows[c] = str(int(cell))
                    else:
                        rows[c] = str(cell)
            sheet_data.append(rows)
        data.append(sheet_data)
        merge.append(sheet.merged_cells)

    return data, merge


def MergeCell(data, merge):
    data2 = []
    for sheet_data, sheet_merge in zip(data, merge):
        # only merge vertical
        for r1, r2, c1, c2 in sheet_merge:
            for r in range(r1, r2):
                sheet_data[r][c1] = sheet_data[r1][c1]
                for c in range(c1+1, c2):
                    sheet_data[r][c] = None
        # remove merge horizontal
        sheet_data2 = [[cell for cell in row if cell is not None] for row in sheet_data]
        # remove blanks in tail
        for row in sheet_data2:
            while len(row) and row[-1] == '': # Good!
                row.pop()
        data2.append(sheet_data2)

    return data2


def WashData(data):
    for i, item in enumerate(data):
        if isinstance(item, list):
            WashData(item)
        else:
            data[i] = data[i].strip().replace('\n', ' ').replace('\r', ' ') # replace after strip
    return data # wash list in place


def WriteTxt(data, file): # Good!
    with open(file, 'w') as f:
        f.write('\n'.join(','.join(row) for row in sum(data, [])))


def Excel2Csv(file):
    root, ext = os.path.splitext(file)
    if ext == '.xlsx':
        file2 = root + '.xls' # only ".xls" type contain merge_info
        ...
        file = file2
    data = WashData(MergeCell(*ReadExcel(file)))
    WriteTxt(data, root+'.csv')
    return data


file = '办公电话号码表.xls'
data = Excel2Csv(file)

from pprint import pprint
pprint(data[0]) # sheet1
