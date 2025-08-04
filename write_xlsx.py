import openpyxl
import sys

def overwrite(file_path, keywordcol, keyword, targetcol, newdata):
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active

    for row_idx,row in enumerate(sheet.iter_rows(min_row=1, values_only=True),start=1):
        if row_idx == 1:
            continue
        if row is None or len(row) < max(keywordcol, targetcol):
            print(f"第 {row_idx} 行数据不完整，跳过")
            continue
        _d = row[keywordcol-1]
        if _d is None:
            print(row_idx,row)
            _d = ""
        if keyword in _d:
            sheet.cell(row=row_idx, column=targetcol, value=newdata)
            break
    
    workbook.save(file_path)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("用法: python write_xlsx.py <文件路径> 关键字匹配列 关键字 复写列 新值")
        print("示例: python write_xlsx.py data.xlsx 1 cawd-110 2 new_value")
        sys.exit(1)
    
    # mode = sys.argv[1]
    file_path = sys.argv[1]
    keywordcol = sys.argv[2]
    keyword = sys.argv[3]
    newcol = sys.argv[4]
    newdata = sys.argv[5]

    
    if keywordcol.isdigit(): 
        keywordcol = int(keywordcol)
    else:
        print("数量参数必须是一个整数")
        sys.exit(1)
    if newcol.isdigit(): 
        newcol = int(newcol)
    else:
        print("数量参数必须是一个整数")
        sys.exit(1)

    
    overwrite(file_path,keywordcol,keyword,newcol,newdata)
    