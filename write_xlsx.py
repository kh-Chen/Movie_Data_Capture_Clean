import openpyxl
import sys

def overwrite(file_path, linenum, targetcol, newdata):
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active
    lines = linenum.split(',')
    for lineidx in lines:
        sheet.cell(row=int(lineidx), column=targetcol, value=newdata)
    
    workbook.save(file_path)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("用法: python write_xlsx.py <文件路径> 行号 复写列 新值")
        print("示例: python write_xlsx.py data.xlsx 108 2 new_value")
        sys.exit(1)
    
    # mode = sys.argv[1]
    file_path = sys.argv[1]
    linenum = sys.argv[2]
    newcol = sys.argv[3]
    newdata = sys.argv[4]

    if newcol.isdigit(): 
        newcol = int(newcol)
    else:
        print("数量参数必须是一个整数")
        sys.exit(1)

    
    overwrite(file_path,linenum,newcol,newdata)
    