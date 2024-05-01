import urllib.request
import re #正则
import os

# 定义要访问的多个URL
urls = [
    'https://raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt',
    'https://raw.githubusercontent.com/Guovin/TV/gd/result.txt',
    'https://raw.githubusercontent.com/ssili126/tv/main/itvlist.txt',
    'https://m3u.ibert.me/txt/fmml_ipv6.txt',
    'https://m3u.ibert.me/txt/ycl_iptv.txt',
    'https://m3u.ibert.me/txt/y_g.txt',
    'https://m3u.ibert.me/txt/j_home.txt',
    'https://raw.githubusercontent.com/gaotianliuyun/gao/master/list.txt',
    'https://gitee.com/xxy002/zhiboyuan/raw/master/zby.txt'
]

# 定义多个对象用于存储不同内容的行文本
ys_lines = []
ws_lines = []
ty_lines = []
dy_lines = []
dsj_lines = []
# favorite_lines = []

other_lines = []

def process_name_string(input_str):
    parts = input_str.split(',')
    processed_parts = []
    for part in parts:
        processed_part = process_part(part)
        processed_parts.append(processed_part)
    result_str = ','.join(processed_parts)
    return result_str

def process_part(part_str):
    # 处理逻辑
    if "CCTV" in part_str:
        part_str=part_str.replace("IPV6", "")  #先剔除IPV6字样
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        if not filtered_str.strip(): #处理特殊情况，如果发现没有找到频道数字返回原名称
            filtered_str=part_str 
        return "CCTV-"+filtered_str 
        
    elif "卫视" in part_str:
        # 定义正则表达式模式，匹配“卫视”后面的内容
        pattern = r'卫视「.*」'
        # 使用sub函数替换匹配的内容为空字符串
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str
    
    return part_str

def process_url(url):
    try:
        # 打开URL并读取内容
        with urllib.request.urlopen(url) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            channel_name=""
            channel_address=""

            # 逐行处理内容
            lines = text.split('\n')
            for line in lines:
                if  "#genre#" not in line and "," in line:
                    channel_name=line.split(',')[0].strip()
                    channel_address=line.split(',')[1].strip()
                    # 根据行内容判断存入哪个对象
                    if "CCTV" in channel_name:
                        ys_lines.append(process_name_string(line.strip()))
                    elif "卫视" in channel_name:
                        ws_lines.append(process_name_string(line.strip()))
                    elif "体育" in channel_name:
                        ty_lines.append(process_name_string(line.strip()))
                    elif channel_name in dy_dictionary:  #电影频道
                        dy_lines.append(process_name_string(line.strip()))
                    elif channel_name in dsj_dictionary:  #电视剧频道
                        dsj_lines.append(process_name_string(line.strip()))
                    else:
                        other_lines.append(line.strip())

                
    except Exception as e:
        print(f"处理URL时发生错误：{e}")


current_directory = os.getcwd()  #准备读取txt

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
#读取文本
dy_dictionary=read_txt_to_array('电影.txt')
dsj_dictionary=read_txt_to_array('电视剧.txt')


# 循环处理每个URL
for url in urls:
    print(f"处理URL: {url}")
    process_url(url)



# 定义一个函数，提取每行中逗号前面的数字部分作为排序的依据
def extract_number(s):
    num_str = s.split(',')[0].split('-')[1]  # 提取逗号前面的数字部分
    numbers = re.findall(r'\d+', num_str)   #因为有+和K
    return int(numbers[-1]) if numbers else 0
# 定义一个自定义排序函数
def custom_sort(s):
    if "CCTV-4K" in s:
        return 1  # 将包含 "4K" 的字符串排在后面
    elif "CCTV-8K" in s:
        return 2  # 将包含 "8K" 的字符串排在后面
    else:
        return 0  # 其他字符串保持原顺序

# 合并所有对象中的行文本（去重，排序后拼接）
all_lines =  ["央视频道,#genre#"] + sorted(sorted(set(ys_lines),key=lambda x: extract_number(x)), key=custom_sort) + ['\n'] + \
             ["卫视频道,#genre#"] + sorted(set(ws_lines)) + ['\n'] + \
             ["体育频道,#genre#"] + sorted(set(ty_lines)) + ['\n'] + \
             ["电影频道,#genre#"] + sorted(set(dy_lines)) + ['\n'] + \
             ["电视剧频道,#genre#"] + sorted(set(dsj_lines))

# 将合并后的文本写入文件
output_file = "merged_output.txt"
others_file = "others_output.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_file}")

    with open(others_file, 'w', encoding='utf-8') as f:
        for line in other_lines:
            f.write(line + '\n')
    print(f"Others已保存到文件: {others_file}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")
