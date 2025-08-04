import random
import openpyxl
import sys
import os
import unicodedata
import traceback
import time


chararr = ['…','●','○','·','°','×','→','‘','―','★','—','”','“','≫','≪','◆','♂']
def get_display_width(text):
    """计算字符串的显示宽度（考虑宽窄字符）"""
    width = 0
    
    for char in str(text):
        # char_width = 2 if char not in chararr and unicodedata.east_asian_width(char) in ('F', 'W', 'A') else 1
        char_width = 2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1
        width += char_width
    return width

def get_terminal_width():
    try:
        # 获取终端尺寸并返回列数（宽度）
        return os.get_terminal_size().columns - 4
    except OSError:
        # 当输出被重定向到文件时可能失败，返回默认值80
        return 120

import math

def calculate_column_widths(all_width, needed_widths, min_width=5):
    """
    计算二维表格各列的最佳显示宽度，确保总宽度充分利用
    
    参数:
    all_width (int): 屏幕总宽度
    needed_widths (list of list of int): 二维列表，表示每个单元格完整显示需要的宽度
    min_width (int): 每列的最小宽度限制，默认为5
    
    返回:
    list: 每列的最佳宽度分配方案
    
    异常:
    ValueError: 当所有列都采用最小宽度时仍超出屏幕总宽度
    """
    # 处理空表情况
    if not needed_widths or not needed_widths[0]:
        return []
    
    n_cols = len(needed_widths[0])
    n_rows = len(needed_widths)
    
    # 1. 计算每列的基础需求
    max_widths = []  # 每列的最大需求
    avg_widths = []  # 每列的平均需求
    
    for col_idx in range(n_cols):
        col_values = [row[col_idx] for row in needed_widths]
        col_max = max(col_values)
        col_avg = sum(col_values) / n_rows
        max_widths.append(max(col_max, min_width))
        avg_widths.append(max(col_avg, min_width))

    # 3. 如果理想宽度总和不超过总宽度，直接返回理想宽度
    ideal_total = sum(max_widths)
    if ideal_total <= all_width:
        return max_widths
    
    # 2. 计算每列的加权需求（结合最大和平均需求）
    # 权重因子：最大值占70%，平均值占30%
    weighted_needs = [
        0.6 * max_widths[i] + 0.4 * avg_widths[i] 
        for i in range(n_cols)
    ]
    
    # 3. 检查最小宽度可行性
    min_total = n_cols * min_width
    if min_total > all_width:
        raise ValueError(f"即使所有列都使用最小宽度({min_width})，总宽度({min_total})仍超过屏幕宽度({all_width})")
    
    # 4. 如果加权需求总和≤总宽度，按比例分配整数宽度
    weighted_total = sum(weighted_needs)
    if weighted_total <= all_width:
        # 先按比例分配整数部分
        base_widths = [min(int(weighted_needs[i] * all_width / weighted_total),max_widths[i]) for i in range(n_cols)]
        allocated = sum(base_widths)
        
        # 处理分配不足的情况
        remaining = all_width - allocated
        if remaining > 0:
            # 按需求缺口降序排序
            deficit_indices = sorted(
                range(n_cols),
                key=lambda i: weighted_needs[i] - base_widths[i],
                reverse=True
            )

            deficit_indices = list(filter(lambda i: max_widths[i]-base_widths[i] > 0, deficit_indices))
            
            # 将剩余宽度分配给需求缺口最大的列
            for i in range(remaining):
                if len(deficit_indices) == 0:
                    break
                idx = deficit_indices[i % len(deficit_indices)]
                
                base_widths[idx] += 1
                if base_widths[idx] >= max_widths[idx]:
                    deficit_indices.remove(idx)
        return base_widths
    
    # 5. 压缩分配：在保证最小宽度的基础上按需分配
    # 初始化每列为最小宽度
    final_widths = [min_width] * n_cols
    remaining = all_width - min_total
    
    # 计算每列的实际额外需求（不超过最大需求）
    extra_needs = [
        min(max_widths[i] - min_width, weighted_needs[i] - min_width)
        for i in range(n_cols)
    ]
    total_extra_needed = sum(extra_needs)
    
    # 如果还有额外需求空间
    if total_extra_needed > 0:
        # 按比例分配额外空间（浮点数）
        extra_alloc_float = [
            remaining * (need / total_extra_needed)
            for need in extra_needs
        ]
        
        # 分配整数部分
        extra_alloc_int = [math.floor(a) for a in extra_alloc_float]
        for i in range(n_cols):
            final_widths[i] += int(extra_alloc_int[i])
        
        # 处理剩余空间（因取整产生）
        allocated = sum(final_widths)
        remaining_space = all_width - allocated
        
        if remaining_space > 0:
            # 计算每列的需求满足度（当前宽度 / 加权需求）
            satisfaction = [
                final_widths[i] / weighted_needs[i] if weighted_needs[i] > 0 else 1
                for i in range(n_cols)
            ]
            
            # 优先分配给满足度最低的列
            unsatisfied_indices = sorted(
                range(n_cols),
                key=lambda i: satisfaction[i]
            )
            
            # 分配剩余空间（每列最多增加1单位）
            for idx in unsatisfied_indices:
                if remaining_space <= 0:
                    break
                # 确保不超过实际最大需求
                if final_widths[idx] < max_widths[idx]:
                    final_widths[idx] += 1
                    remaining_space -= 1
    
    return final_widths

def pad_to_width(text, width):
    """填充文本到指定显示宽度（考虑宽窄字符）"""
    while True:
        current_width = get_display_width(text)
        _charlen = len(text)-2
        if current_width >= width:
            text = text[:_charlen] + "…"
        else:
            break
    
    # 计算需要添加的空格数量
    padding = width - current_width
    return text + ' ' * padding

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
        max_widths.append(max(col_max, min_width))
        final_widths.append(max(col_max, min_width))
    
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

            if length<minlen:
                index = idx
                minlen = length
            elif length == minlen:
                if max_widths[idx] > max_widths[index]:
                    index = idx
                
        
        # print(index,minlen)
        final_widths[index] -= 1
        for row in needed_widths:
            if row[index]>final_widths[index]:
               row[index] -= 1

    
    return final_widths

def read_xlsx(file_path, cols=[], start:int=0, limit:int=10):
    try:
        terminal_width = get_terminal_width()
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active

        print_data = []
        print_data_width = []
        if len(cols) == 0:
            cols = [col_idx+1 for col_idx in range(sheet.max_column)]
        
        col_display_widths_max = [0] * len(cols)

        max_row = sheet.max_row
        printrowindexs = list(range(2, max_row + 1))
        if limit < max_row:
            if start < 0:
                printrowindexs = random.sample(printrowindexs, limit)
            else:
                if len(printrowindexs) < start+limit:
                    printrowindexs = printrowindexs[:limit]
                else:
                    printrowindexs = printrowindexs[start:start+limit]

        if len(cols) != 1:
            printrowindexs.append(1)
        
        for row_idx,row in enumerate(sheet.iter_rows(min_row=1, values_only=True),start=1):
            if row_idx not in printrowindexs:
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
                width = get_display_width(cell_data)+1
                if width > col_display_widths_max[idx]:
                    col_display_widths_max[idx] = width
                print_data_line.append(cell_data)
                print_data_width_line.append(width)
            print_data.append(print_data_line)
            if row_idx!=1:
                print_data_width.append(print_data_width_line)

        spitcharlen = (len(cols)-1)*2+2
        for a in print_data_width:
            print(a)
        col_display_widths_print = calculate_column_widths_new(terminal_width-spitcharlen,print_data_width,5)
        # print(col_display_widths_max)
        # print(col_display_widths_print)
        separator = "-" * (sum(col_display_widths_print)+spitcharlen+1)
        for idx, print_data_line in enumerate(print_data):
            if idx == 0 and len(cols)!=1:
                print(separator)
                header = "| ".join(pad_to_width(print_data_line[i],col_display_widths_print[i]) for i in range(len(cols)))
                print("| "+header+"|")
                print(separator)
            else:
                if len(cols)!=1:
                    line = "| ".join(pad_to_width(print_data_line[i],col_display_widths_print[i]) for i in range(len(cols)))
                    print("| "+line+"|")
                    pass
                else:
                    print(pad_to_width(print_data_line[0],col_display_widths_print[0]))
        
        if len(cols) != 1:
            print(separator)
            print(f"总计{max_row-1} 行，显示 {len(print_data)-1} 行 ")

    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到")
        sys.exit(1)
    except Exception as e:
        print(f"读取文件时出错: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python read_xlsx.py <文件路径> <字段> <分页>")
        print("示例: python read_xlsx.py data.xlsx 1,2,4,5,6 0,10|random,10")
        sys.exit(1)
    
    # mode = sys.argv[1]
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



    