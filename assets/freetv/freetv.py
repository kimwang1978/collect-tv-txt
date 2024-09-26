import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime

# 定义
freetv_lines = []

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
        freetv_lines.append(line.strip())


        # channel_name=line.split(',')[0].strip()
        # channel_address=clean_url(line.split(',')[1].strip())  #把URL中$之后的内容都去掉
        # line=channel_name+","+channel_address #重新组织line

        # if channel_address not in combined_blacklist: # 判断当前源是否在blacklist中
        #     # 根据行内容判断存入哪个对象，开始分发
        #     if "CCTV" in channel_name and check_url_existence(ys_lines, channel_address) : #央视频道
        #         ys_lines.append(process_name_string(line.strip()))
        #     elif channel_name in Olympics_2024_Paris_dictionary and check_url_existence(Olympics_2024_Paris_lines, channel_address): #奥运频道 ADD 2024-08-05
        #         Olympics_2024_Paris_lines.append(process_name_string(line.strip()))
           

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
                    #需要加处理带#号源=予加速源
                    if channel_name in freetv_dictionary:
                        process_channel_line(line) # 如果没有井号，则照常按照每行规则进行分发

    except Exception as e:
        print(f"处理URL时发生错误：{e}")



#读取文本
freetv_dictionary=read_txt_to_array('assets/freetv/freetvlist.txt') 

# 定义
urls = ["https://freetv.fun/test_channels_original_new.txt"]

# 处理
for url in urls:
    print(f"处理URL: {url}")
    process_url(url)


# 
version=datetime.now().strftime("%Y%m%d-%H-%M-%S")+",url"
output_lines =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv,#genre#"] + sorted(set(freetv_lines))

# 将合并后的文本写入文件
output_file = "assets/freetv/freetv_output.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")