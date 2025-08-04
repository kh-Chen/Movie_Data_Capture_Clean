import os
 

# @blockprint
def run():
    print("test mode")



# def query98t():
#     header = {
#         'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#         'Accept-Encoding':'gzip',
#         'Accept-Language':'zh-CN,en-US;q=0.7,en;q=0.3',
#         'Cookie':'cPNj_2132_saltkey=YRQbrnQ4; _safe=esfVvaXV7aASX1D7; ',
#         'DNT':'1',
#         'Host':'gauz.8uly.net',
#         'Priority':'u=0, i',
#         'Referer':'https://gauz.8uly.net/forum.php',
#         'Sec-Fetch-Dest':'document',
#     }

#     for i in range(5):
#         print(i)

#     html = httprequest.get(url='https://gauz.8uly.net/forum-103-1.html',extra_headers=header)
#     print(html)
#     tree = etree.fromstring(html, etree.HTMLParser()) 
#     tag_a_arr = tree.xpath("//a[starts-with(@href, 'thread-') and contains(@class, 'xst')]")
#     tag_a_arr = tag_a_arr[5:]
#     print(len(tag_a_arr))
#     for tag_a in tag_a_arr:
#         data = tag_a.text
#         data = re.sub(r'\[[^\]]*\]', '', data)
#         datas = data.split(' ',1)
#         number = datas[0].strip()
#         title = datas[1].strip()
#         if number != '' and title != '':
#             print(number,title)
        


# def bk_downloaded_file():
    
#     filenames=os.listdir(r"/mnt/f/downloaded")
#     filenames.sort()
    
#     title    = ["番号","标题","演员","评分","人数","发布时间"]
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active
#     sheet.title = "Data"  
#     sheet.append(title)

#     for name in filenames:

#         name = os.path.splitext(name)[0]
#         data = name.split(' ')
#         if len(data) < 2:
#             continue
#         wdata = []

#         wdata.append(data[2])  # number
#         wdata.append(data[5])
#         wdata.append(data[4])
#         _t = data[3].split('∕')
#         wdata.append(_t[0].replace('[',''))
#         wdata.append(_t[1].replace(']',''))
#         wdata.append(data[1])
#         sheet.append(wdata)
#     workbook.save("downloaded.xlsx")
        

