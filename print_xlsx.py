import random
import openpyxl
import sys
import os
import unicodedata
import traceback
import time


chararr = ['…','●','○','·','°','×','→','‘','―','★','—','”','“','≫','≪']
def get_display_width(text):
    """计算字符串的显示宽度（考虑宽窄字符）"""
    width = 0
    
    for char in str(text):
        char_width = 2 if char not in chararr and unicodedata.east_asian_width(char) in ('F', 'W', 'A') else 1
        width += char_width
    return width

def get_terminal_width():
    try:
        # 获取终端尺寸并返回列数（宽度）
        return os.get_terminal_size().columns - 10
    except OSError:
        # 当输出被重定向到文件时可能失败，返回默认值80
        return 120
    

def adjust_column_widths(all_width, col_width_arr):
    n = len(col_width_arr)
    min_total = 10 * n
    
    # 检查最小宽度是否超过总宽度
    if min_total > all_width:
        raise ValueError(f"每个字段最小宽度为10时，总宽度需求{min_total}已超过总宽度{all_width}")
    
    # 如果当前总和已经等于目标宽度，直接返回
    if sum(col_width_arr) == all_width:
        return col_width_arr
    
    # 初始化结果数组（确保每个字段至少为10）
    result = [max(10, width) for width in col_width_arr]
    current_total = sum(result)
    
    # 如果已经超过总宽度，需要缩减
    if current_total > all_width:
        # 计算需要缩减的总量
        reduction_needed = current_total - all_width
        # 计算可缩减的字段（当前宽度>10的字段）
        reducible_cols = [i for i, width in enumerate(result) if width > 10]
        reducible_weights = [result[i] - 10 for i in reducible_cols]
        total_reducible_weight = sum(reducible_weights)
        
        # 如果没有可缩减的字段，但总宽度还是超，抛异常（理论上不会发生）
        if not reducible_cols:
            raise ValueError("无法缩减到目标宽度（所有字段均为最小宽度10）")
        
        # 按可缩减权重比例分配缩减量
        for i, idx in enumerate(reducible_cols):
            reduction_share = int(round(reduction_needed * reducible_weights[i] / total_reducible_weight))
            # 确保缩减后不小于10
            result[idx] = max(10, result[idx] - reduction_share)
        
        # 处理整数舍入误差
        current_total = sum(result)
        adjustment = current_total - all_width
        if adjustment > 0:
            # 从可缩减字段中按权重顺序缩减
            for idx in sorted(reducible_cols, key=lambda i: result[i] - 10, reverse=True):
                if result[idx] > 10 and adjustment > 0:
                    result[idx] -= 1
                    adjustment -= 1
                    if adjustment == 0:
                        break
    
    # 如果当前总和小于目标宽度，需要增加
    elif current_total < all_width:
        # 计算需要增加的总量
        addition_needed = all_width - current_total
        # 计算权重总和（原始权重）
        total_weight = sum(col_width_arr)
        
        # 按原始权重比例分配增量
        additions = []
        for weight in col_width_arr:
            share = addition_needed * weight / total_weight
            additions.append(share)
        
        # 整数分配处理
        int_additions = [int(share) for share in additions]
        remainder = addition_needed - sum(int_additions)
        # 处理小数部分（按小数大小降序分配）
        decimals = [additions[i] - int_additions[i] for i in range(n)]
        for i in sorted(range(n), key=lambda i: decimals[i], reverse=True)[:int(remainder)]:
            int_additions[i] += 1
        
        # 应用增量
        result = [result[i] + int_additions[i] for i in range(n)]
    
    return result

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
        if len(cols) == 0:
            # header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
            cols = [col_idx+1 for col_idx in range(sheet.max_column)]
        
        col_display_widths_max = [0] * len(cols)
        col_display_widths_all = [{"count":0,"sum":0} for _ in range(len(cols))] 
        col_display_widths_avg = [0] * len(cols)

        max_row = sheet.max_row
        printrowindexs = list(range(2, max_row + 1))
        if num < max_row:
            printrowindexs = random.sample(printrowindexs, num)

        printrowindexs.append(1)
        
        
        for row_idx,row in enumerate(sheet.iter_rows(min_row=1, values_only=True),start=1):
            if row_idx not in printrowindexs:
                continue
            print_data_line = []
            for idx, col_idx in enumerate(cols):
                cell_data = row[col_idx-1]
                if cell_data is None:
                    cell_data = ""
                cell_data = str(cell_data).strip()
                width = get_display_width(cell_data)
                if width > col_display_widths_max[idx]:
                    col_display_widths_max[idx] = width
                if row_idx != 1 and cell_data != "":
                    col_display_widths_all[idx]["count"] += 1
                    col_display_widths_all[idx]["sum"] += width
                print_data_line.append(cell_data)
            print_data.append(print_data_line)

        charlen = (len(cols)-1)*2+2
        col_display_widths_print = []
        if sum(col_display_widths_max) + charlen <= terminal_width:
            col_display_widths_print = adjust_column_widths(terminal_width-charlen,col_display_widths_max)
        else:
            for idx in range(len(cols)):
                if col_display_widths_all[idx]["count"] > 0:
                    col_display_widths_avg[idx] = col_display_widths_all[idx]["sum"] // col_display_widths_all[idx]["count"]
                else:
                    col_display_widths_avg[idx] = 0
            
            col_display_widths_print = adjust_column_widths(terminal_width-charlen,col_display_widths_avg)
            
        # print(col_display_widths_print)
        separator = "-" * terminal_width
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