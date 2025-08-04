
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

    print(all_width)
    print("max",max_widths)
    print("avg",avg_widths)
    # 如果理想宽度总和不超过总宽度，直接返回理想宽度
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
        print("re1",base_widths)
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
    print("need",extra_needs)
    
    # 如果还有额外需求空间
    if total_extra_needed > 0:
        # 按比例分配额外空间（浮点数）
        extra_alloc_float = [
            remaining * (need / total_extra_needed)
            for need in extra_needs
        ]
        print("alloc",extra_alloc_float)
        
        # 分配整数部分
        extra_alloc_int = [math.floor(a) for a in extra_alloc_float]
        for i in range(n_cols):
            final_widths[i] += int(extra_alloc_int[i])
        print("f1",final_widths)
        # 处理剩余空间（因取整产生）
        allocated = sum(final_widths)
        remaining_space = all_width - allocated
        print("remaining_space",remaining_space)
        
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
    print("re",final_widths)
    return final_widths

def countlength(needed_widths,col_index,target_len):
    col_values = [row[col_index] for row in needed_widths]
    t = 0
    # print(col_index,t)
    for val in col_values:
        if val > target_len:
            t += (val-target_len)
    # print(col_index,target_len,t)
    return t


def calculate_column_widths_new(all_width, needed_widths, min_width=5):
    if not needed_widths or not needed_widths[0]:
        return []
    
    n_cols = len(needed_widths[0])
    max_widths = []
    final_widths = []
    # maxindex = 0
    # maxvalue = 0
    for col_idx in range(n_cols):
        col_values = [row[col_idx] for row in needed_widths]
        col_max = max(col_values)
        # if col_max > maxvalue:
        #     maxindex = col_idx
        #     maxvalue = col_max
        max_widths.append(max(col_max, min_width))
        final_widths.append(max(col_max, min_width))
    
    print(max_widths)
    max_width = sum(max_widths)
    print(all_width)
    print("maxlength",max_width)
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
        print(lens)
        for idx,length in enumerate(lens):

            if length<minlen:
                index = idx
                minlen = length
            elif length == minlen:
                if max_widths[idx] > max_widths[index]:
                    index = idx
                
        
        print(index,minlen)
        final_widths[index] -= 1
        for row in needed_widths:
            if row[index]>final_widths[index]:
               row[index] -= 1

    
    return final_widths




        
            
        

    
    



if __name__ == "__main__":


    data=[
        [9, 117, 9, 5, 5],
        [9, 60, 9, 4, 5],
        [9, 68, 9, 5, 5],
        [9, 83, 9, 5, 5],
        [9, 72, 11, 5, 5],
        [9, 65, 9, 5, 5],
        [9, 45, 9, 5, 5],
        [9, 143, 20, 5, 4],
        [9, 169, 38, 5, 3],
        [10, 86, 11, 4, 4],
    ]
    length=155
    print(calculate_column_widths_new(length,data))
