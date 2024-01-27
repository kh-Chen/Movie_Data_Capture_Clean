import time,os
from unicodedata import category
from pathlib import Path

def cn_space(v: str, n: int) -> int:
    return n - [category(c) for c in v[0:n]].count('Lo')

def file_modification_days(filename: str) -> int:
    """
    文件修改时间距此时的天数
    """
    mfile = Path(filename)
    if not mfile.is_file():
        return 9999
    mtime = int(mfile.stat().st_mtime)
    now = int(time.time())
    days = int((now - mtime) / (24 * 60 * 60))
    if days < 0:
        return 9999
    return days

def create_folder(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            raise RuntimeError()
        
# def escape_path(path, escape_literals: str):  # Remove escape literals
#     backslash = '\\'
#     for literal in escape_literals:
#         path = path.replace(backslash + literal, '')
#     return path

def image_ext(url):
    try:
        ext = os.path.splitext(url)[-1]
        if ext in {'.jpg', '.jpge', '.bmp', '.png', '.gif'}:
            return ext
        return ".jpg"
    except:
        return ".jpg"
    
def file_not_exist_or_empty(filepath) -> bool:
    return not os.path.isfile(filepath) or os.path.getsize(filepath) == 0

def legalization_of_file_path(filepath:str):
    temp = os.path.splitext(filepath)
    suffix = temp[-1]
    filep = temp[0]

    names = filep.split("/")
    re = []
    for index, name in enumerate(names):
        name = special_characters_replacement(name)
        max = 255-3
        if index == len(names)-1:
            max = max - len(suffix)
            
        len_name = 0
        for _index, every_char in enumerate(name):
            len_name += len(every_char.encode())
            if max < len_name:
                name = name[:_index] + '…'
                break
        if index == len(names)-1:
            name = name + suffix
        re.append(name)

    return '/'.join(re)


def special_characters_replacement(text) -> str:
    if not isinstance(text, str):
        return text
    return (text.replace('\\', '∖').  # U+2216 SET MINUS @ Basic Multilingual Plane
            replace('/', '∕').  # U+2215 DIVISION SLASH @ Basic Multilingual Plane
            replace(':', '꞉').  # U+A789 MODIFIER LETTER COLON @ Latin Extended-D
            replace('*', '∗').  # U+2217 ASTERISK OPERATOR @ Basic Multilingual Plane
            replace('?', '？').  # U+FF1F FULLWIDTH QUESTION MARK @ Basic Multilingual Plane
            replace('"', '＂').  # U+FF02 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
            replace('\'', '＇'). # U+FF07 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
            replace('<', 'ᐸ').  # U+1438 CANADIAN SYLLABICS PA @ Basic Multilingual Plane
            replace('>', 'ᐳ').  # U+1433 CANADIAN SYLLABICS PO @ Basic Multilingual Plane
            replace('|', 'ǀ').  # U+01C0 LATIN LETTER DENTAL CLICK @ Basic Multilingual Plane
            replace('&lsquo;', '‘').  # U+02018 LEFT SINGLE QUOTATION MARK
            replace('&rsquo;', '’').  # U+02019 RIGHT SINGLE QUOTATION MARK
            replace('&hellip;', '…').
            replace('&amp;', '＆').
            replace("&", '＆')
            )


# if __name__ == '__main__':
#     print(legalization_of_file_path("/mnt/f/store/JAV_output/NwmXrB 2023 PRED-458-C [4.45∕135] 竹内有紀 我太爱比父亲大一岁的大叔上司了。无法抗拒体液和粘膜持续接触的快感，继续出轨….mp4"))