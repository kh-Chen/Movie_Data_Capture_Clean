import random
import openpyxl
import sys
import os
import unicodedata
import traceback
import time


# chararr = ['…','●','○','·','°','×','→','‘','―','★','—','”','“','≫','≪','◆','♂']
def get_display_width(text):
    """计算字符串的显示宽度（考虑宽窄字符）"""
    width = 0
    
    for char in str(text):
        # char_width = 2 if char not in chararr and unicodedata.east_asian_width(char) in ('F', 'W', 'A') else 1
        char_width = 2 if is_wide_character(char) else 1
        width += char_width
    return width

def get_terminal_width():
    try:
        return os.get_terminal_size().columns - 4
    except OSError:
        return 120

def is_wide_character(char):
    return unicodedata.east_asian_width(char) in ('F', 'W')

def pad_to_width_optimized(text, width):
    text = str(text)
    ellipsis = '…'
    ellipsis_width = get_display_width(ellipsis)
    
    current_width = 0
    char_list = []
    for char in text:
        char_width = 2 if is_wide_character(char) else 1
        if current_width + char_width > width:
            break
        current_width += char_width
        char_list.append(char)
    
    if len(char_list) != len(text):
        if current_width == width:
            c = char_list[-1]
            char_list = char_list[:-1]
            if is_wide_character(c):
                char_list.append(' ')

    result = ''.join(char_list)
    if result != text:
        result += ellipsis
        current_width += ellipsis_width
    
    return result + ' ' * (width - current_width)

def countlength(needed_widths,col_index,target_len):
    col_values = [row[col_index] for row in needed_widths]
    t = 0
    for val in col_values:
        if val > target_len:
            t += (val-target_len)
    return t


def calculate_column_widths_new(all_width, needed_widths, min_width=5):
    if not needed_widths or not needed_widths[0]:
        return []
    
    n_cols = len(needed_widths[0])
    max_widths = []
    final_widths = []
    for col_idx in range(n_cols):
        col_values = [row[col_idx] for row in needed_widths]
        col_max = max(col_values)
        max_widths.append(col_max)
        final_widths.append(col_max)
    
    max_width = sum(max_widths)
    if all_width >= max_width:
        return max_widths
    
    min_total = n_cols * min_width
    if min_total > all_width:
        raise ValueError(f"即使所有列都使用最小宽度({min_width})，总宽度({min_total})仍超过屏幕宽度({all_width})")
    
    aa = max_width-all_width
    for i in range(aa):
        lens = [countlength(needed_widths,col_idx,final_widths[col_idx]-1) for col_idx in range(n_cols)]
        
        index = 0
        minlen = 99999
        for idx,length in enumerate(lens):
            if final_widths[idx] <= min_width:
                continue
            if length<minlen:
                index = idx
                minlen = length
            elif length == minlen:
                if max_widths[idx] > max_widths[index]:
                    index = idx
                
        final_widths[index] -= 1
        for row in needed_widths:
            if row[index]>final_widths[index]:
               row[index] -= 1

    return final_widths

def get_row_idx(max_row:int, start:int, limit:int):
    printrowindexs = list(range(2, max_row + 1))
    if limit < max_row:
        if start < 0:
            printrowindexs = random.sample(printrowindexs, limit)
        else:
            if len(printrowindexs) < start+limit:
                printrowindexs = printrowindexs[:limit]
            else:
                printrowindexs = printrowindexs[start:start+limit]
    return printrowindexs

def print_data(n_cols:int, print_data_widths:slice, while_print_data:slice, max_row:int):
    terminal_width = get_terminal_width()
    spitcharlen = (n_cols-1)*3+3

    col_display_widths_print = calculate_column_widths_new(terminal_width-spitcharlen,print_data_widths,10)
    
    separator = "-" * (sum(col_display_widths_print)+spitcharlen+1)
    for idx, print_data_line in enumerate(while_print_data):
        if idx == 0 and n_cols!=1:
            print(separator)
            header = " | ".join(pad_to_width_optimized(print_data_line[i],col_display_widths_print[i]) for i in range(n_cols))
            print("| "+header+" |")
            print(separator)
        else:
            if n_cols!=1:
                line = " | ".join(pad_to_width_optimized(print_data_line[i],col_display_widths_print[i]) for i in range(n_cols))
                print("| "+line+" |")
            else:
                print(pad_to_width_optimized(print_data_line[0],col_display_widths_print[0]))
    
    if n_cols != 1:
        print(separator)
        print(f"总计{max_row} 行，显示 {len(while_print_data)-1} 行 ")



def read_xlsx(file_path, cols=[], start:int=0, limit:int=10):
    try:
        
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active
        max_row = sheet.max_row
        
        if len(cols) == 0:
            cols = [col_idx+1 for col_idx in range(sheet.max_column)]
        
        n_cols = len(cols)
        
        printrowindexs = get_row_idx(max_row,start,limit)

        while_print_data = []
        print_data_widths = []
        for row_idx,row in enumerate(sheet.iter_rows(min_row=1, values_only=True),start=1):
            if row_idx not in printrowindexs and (row_idx != 1 or n_cols == 1):
                continue
            print_data_line = []
            print_data_width_line = []
            for idx, col_idx in enumerate(cols):
                cell_data = row[col_idx-1]
                if cell_data is None:
                    cell_data = ""
                cell_data = str(cell_data).strip()
                if cell_data == "":
                    cell_data = str(row_idx)

                print_data_line.append(cell_data)
                print_data_width_line.append(get_display_width(cell_data))
            while_print_data.append(print_data_line)
            if row_idx!=1:
                print_data_widths.append(print_data_width_line)

        print_data(n_cols,print_data_widths,while_print_data,max_row)

    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到")
        sys.exit(1)
    except Exception as e:
        print(f"读取文件时出错: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python read_xlsx.py <文件路径> <字段> <分页>")
        print("示例: python read_xlsx.py data.xlsx 1,2,4,5,6 0,10|random,10")
        sys.exit(1)
    
    file_path = sys.argv[1]
    colnames = sys.argv[2]
    
    cols = []
    cols = colnames.split(",")
    cols = [int(c) for c in cols if c.isdigit()]

    numstr = sys.argv[3]
    _numstr = numstr.split(",")

    
    start = 0
    if "random" == _numstr[0]:
        start=-1
    elif _numstr[0].isdigit():
        start=int(_numstr[0])
        pass
    else:
        print("参数错误")
        sys.exit(1)
        pass

    if len(_numstr) !=2 or not _numstr[1].isdigit(): 
        print("参数错误")
        sys.exit(1)

    count = int(_numstr[1])

    read_xlsx(file_path,cols,start,count)



    