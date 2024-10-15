import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta, timezone

# 定义
freetv_lines = []

#读取修改频道名称方法
def load_modify_name(filename):
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

#读取修改字典文件
rename_dic = load_modify_name('assets/freetv/freetv_rename.txt')

#纠错频道名称
def rename_channel(corrections, data):
    corrected_data = []
    for line in data:
        name, url = line.split(',', 1)
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data

#读取文本方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
# 组织过滤后的freetv
def process_channel_line(line):
    if  "#genre#" not in line and "," in line and "://" in line:
        channel_name, channel_address = line.split(',', 1)
        channel_address=channel_address+"$"+channel_name.strip().replace(' ', '_')
        line=channel_name+","+channel_address
        freetv_lines.append(line.strip())


def process_url(url):
    try:
        # 创建一个请求对象并添加自定义header
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        # 打开URL并读取内容
        with urllib.request.urlopen(req) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            # channel_name=""
            # channel_address=""

            # 逐行处理内容
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            for line in lines:
                if  "#genre#" not in line and "," in line and "://" in line:
                    # 拆分成频道名和URL部分
                    channel_name, channel_address = line.split(',', 1)
                    
                    if channel_name in freetv_dictionary:
                        process_channel_line(line) 

    except Exception as e:
        print(f"处理URL时发生错误：{e}")



#读取文本
freetv_dictionary=read_txt_to_array('assets/freetv/freetvlist.txt')  #all
freetv_dictionary_cctv=read_txt_to_array('assets/freetv/freetvlist_cctv.txt')   #二次分发cctv，单独存
freetv_dictionary_ws=read_txt_to_array('assets/freetv/freetvlist_ws.txt')   #二次分发卫视，单独存

freetv_cctv_lines = []
freetv_ws_lines = []
freetv_other_lines = []


# 定义
urls = ["https://freetv.fun/test_channels_original_new.txt"]

# 处理
for url in urls:
    print(f"处理URL: {url}")
    process_url(url)

# 获取当前的 UTC 时间
utc_time = datetime.now(timezone.utc)
# 北京时间
beijing_time = utc_time + timedelta(hours=8)
# 格式化为所需的格式
formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")

# freetv_all
freetv_lines_renamed=rename_channel(rename_dic,freetv_lines)
version=formatted_time+",url"
output_lines =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv,#genre#"] + sorted(set(freetv_lines_renamed))

# 将合并后的文本写入文件：全集
output_file = "assets/freetv/freetv_output.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")

# # # # # # # # # # # # # # # # # # # # # # # 分批再次保存
# $去掉
def clean_url(url):
    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

for line in freetv_lines_renamed:
    if  "#genre#" not in line and "," in line and "://" in line:
        channel_name=line.split(',')[0].strip()
        channel_address=clean_url(line.split(',')[1].strip())  #把URL中$之后的内容都去掉
        line=channel_name+","+channel_address #重新组织line

        if channel_name in freetv_dictionary_cctv: #央视频道
            freetv_cctv_lines.append(line.strip())
        elif channel_name in freetv_dictionary_ws: #卫视频道
            freetv_ws_lines.append(line.strip())
        else:
            freetv_other_lines.append(line.strip())

# freetv_cctv
output_lines_cctv =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv_cctv,#genre#"] + sorted(set(freetv_cctv_lines))
# freetv_ws
output_lines_ws =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv_ws,#genre#"] + sorted(set(freetv_ws_lines))
# freetv_other
output_lines_other =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv_other,#genre#"] + sorted(set(freetv_other_lines))

# 再次写入文件：分开
output_file_cctv = "assets/freetv/freetv_output_cctv.txt"
output_file_ws = "assets/freetv/freetv_output_ws.txt"
output_file_other = "assets/freetv/freetv_output_other.txt"
try:
    with open(output_file_cctv, 'w', encoding='utf-8') as f:
        for line in output_lines_cctv:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file_cctv}")

    with open(output_file_ws, 'w', encoding='utf-8') as f:
        for line in output_lines_ws:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file_ws}")
    
    with open(output_file_other, 'w', encoding='utf-8') as f:
        for line in output_lines_other:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file_other}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")