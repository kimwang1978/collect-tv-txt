####Testing

import time
import urllib.request
import re
from urllib.error import URLError, HTTPError
import ffmpeg


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

# 检测URL是否可访问并记录响应时间
def check_url(url, timeout=6):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    elapsed_time = None
    status_ok = False
    # resolution = None

    try:
        if "://" in url:
            start_time = time.time()
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
                if response.status == 200:
                    status_ok = True
                    # 尝试获取视频分辨率
                    # resolution = get_video_resolution(url)
    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason},{url}")
    except URLError as e:
        print(f"URL Error: {e.reason},{url}")
    except Exception as e:
        print(f"Error checking url: {e},{url}")

    return elapsed_time, status_ok

# def get_video_resolution(url):
#     try:
#         probe = ffmpeg.probe(url)
#         video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
#         if video_streams:
#             width = video_streams[0]['width']
#             height = video_streams[0]['height']
#             return f'{width}x{height}'
#     except Exception as e:
#         print(f"Error getting resolution: {e},{url}")
#     return None

# 处理单行文本并检测URL
def process_line(line):
    if "#genre#" in line or "://" not in line :
        return None, None  # 跳过包含“#genre#”的行
    parts = line.split(',')
    if len(parts) == 2:
        name, url = parts
        elapsed_time, is_valid= check_url(url.strip())
        if is_valid:
            return elapsed_time, line.strip()
        else:
            return 0.0, line.strip()
    return  0.0, line.strip()


#########################分割线########################

merged_output_lines=read_txt_to_array('merged_output.txt') 
new_merged_output_lines=[]
for line in merged_output_lines:
    if  "#genre#" in line:
        new_merged_output_lines.append(line)
    if  "://" not in line:
        new_merged_output_lines.append(line)
    if  "#genre#" not in line and "," in line and "://" in line:
        elapsed_time, line= process_line(line)
        newline=f"{elapsed_time},{line}"
        new_merged_output_lines.append(newline)    #.append(f"{elapsed_time:.2f}ms,{result}")


# 将合并后的文本写入文件
output_file = "test_merged_output.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in new_merged_output_lines:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_file}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")


