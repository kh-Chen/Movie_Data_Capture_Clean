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
        0.7 * max_widths[i] + 0.3 * avg_widths[i] 
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
        base_widths = [int(weighted_needs[i] * all_width / weighted_total) for i in range(n_cols)]
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
            # 将剩余宽度分配给需求缺口最大的列
            for i in range(remaining):
                idx = deficit_indices[i % n_cols]
                base_widths[idx] += 1
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

def read_xlsx(file_path, num=10,cols=[]):
    try:
        terminal_width = get_terminal_width()
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active

        print_data = []
        print_data_width = []
        if len(cols) == 0:
            # header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
            cols = [col_idx+1 for col_idx in range(sheet.max_column)]
        
        col_display_widths_max = [0] * len(cols)
        # col_display_widths_all = [{"count":0,"sum":0} for _ in range(len(cols))] 
        # col_display_widths_avg = [0] * len(cols)

        max_row = sheet.max_row
        printrowindexs = list(range(2, max_row + 1))
        if num < max_row:
            printrowindexs = random.sample(printrowindexs, num)

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
                # if row_idx != 1 and cell_data != "":
                #     col_display_widths_all[idx]["count"] += 1
                #     col_display_widths_all[idx]["sum"] += width
                print_data_line.append(cell_data)
                print_data_width_line.append(width)
            print_data.append(print_data_line)
            print_data_width.append(print_data_width_line)

        spitcharlen = (len(cols)-1)*2+2

        col_display_widths_print = calculate_column_widths(terminal_width-spitcharlen,print_data_width,5)
        # print(col_display_widths_max)
        # print(col_display_widths_print)
        # print(terminal_width-spitcharlen)
        # print(sum(col_display_widths_print))
        separator = "-" * (sum(col_display_widths_print)+spitcharlen+1)
        for idx, print_data_line in enumerate(print_data):
            if idx == 0:
                print(separator)
                header = "| ".join(pad_to_width(print_data_line[i],col_display_widths_print[i]) for i in range(len(cols)))
                print("| "+header+"|")
                print(separator)
            else:
                line = "| ".join(pad_to_width(print_data_line[i],col_display_widths_print[i]) for i in range(len(cols)))
                print("| "+line+"|")
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
        print("用法: python read_xlsx.py <文件路径> <数量>")
        print("示例: python read_xlsx.py data.xlsx 10")
        sys.exit(1)
    
    # mode = sys.argv[1]
    file_path = sys.argv[1]
    num = sys.argv[2]
    if num.isdigit(): 
        num = int(num)
    else:
        print("数量参数必须是一个整数")
        sys.exit(1)

    col = []
    if len(sys.argv) > 3:
        col = sys.argv[3:]
        col = [int(c) for c in col if c.isdigit()]
    read_xlsx(file_path,num,col)