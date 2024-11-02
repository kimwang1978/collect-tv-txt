import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import os
from urllib.parse import urlparse
import socket  #check p3p源 rtp源
import subprocess #check rtmp源

import json

timestart = datetime.now()

# 读取文件内容
def read_txt_file(file_path):
    skip_strings = ['#genre#']  # 定义需要跳过的字符串数组['#', '@', '#genre#'] 
    required_strings = ['://']  # 定义需要包含的字符串数组['必需字符1', '必需字符2'] 

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [
            line for line in file
            if not any(skip_str in line for skip_str in skip_strings) and all(req_str in line for req_str in required_strings)
        ]
    return lines

def get_video_resolution(video_path):
    # 使用 ffprobe 命令来获取视频的流信息，以 JSON 格式输出
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height', '-of', 'json', video_path
    ]
    
    # 运行命令并捕获输出
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # 解析 JSON 输出
    video_info = json.loads(result.stdout)
    
    # 提取宽度和高度
    width = video_info['streams'][0]['width']
    height = video_info['streams'][0]['height']
    
    return width, height

# 检测URL是否可访问并记录响应时间
def check_url(url, timeout=6):
    start_time = time.time()
    elapsed_time = None
    success = False
    
    try:
        if url.startswith("http"):
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    success = True
        elif url.startswith("p3p"):
            success = check_p3p_url(url, timeout)
        elif url.startswith("p2p"):
            success = check_p2p_url(url, timeout)
        elif url.startswith("rtmp") or url.startswith("rtsp") :
            success = check_rtmp_url(url, timeout)
        elif url.startswith("rtp"):
            success = check_rtp_url(url, timeout)

        # 如果执行到这一步，没有异常，计算时间
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒

    except Exception as e:
        print(f"Error checking {url}: {e}")
        # 在发生异常的情况下，将 elapsed_time 设置为 None
        elapsed_time = None

    return elapsed_time, success

def check_rtmp_url(url, timeout): 
    try:
        result = subprocess.run(['ffprobe', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if result.returncode == 0:
            return True
    except subprocess.TimeoutExpired:
        print(f"Timeout checking {url}")
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return False

def check_rtp_url(url, timeout):
    try:
        # 解析URL
        parsed_url = urlparse(url)
        
        # 提取主机名（IP地址）和端口号
        host = parsed_url.hostname
        port = parsed_url.port

        # 创建一个 socket 连接
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)  # 设置超时时间
            s.connect((host, port))
            s.sendto(b'', (host, port))  # 发送空的UDP数据包
            s.recv(1)  # 尝试接收数据
        return True
    except (socket.timeout, socket.error):
        return False

def check_p3p_url(url, timeout):
    try:
        # 解析URL
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        
        # 检查解析是否成功
        if not host or not port or not path:
            raise ValueError("Invalid p3p URL")

        # 创建一个 TCP 连接
        with socket.create_connection((host, port), timeout=timeout) as s:
            # 发送一个简单的请求（根据协议定义可能需要调整）
            request = f"GET {path} P3P/1.0\r\nHost: {host}\r\n\r\n"
            s.sendall(request.encode())
            
            # 读取响应
            response = s.recv(1024)
            
            # 简单判断是否收到有效响应
            if b"P3P" in response:
                return True
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return False

def check_p2p_url(url, timeout):
    try:
        # 解析URL
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path

        # 检查解析是否成功
        if not host or not port or not path:
            raise ValueError("Invalid P2P URL")

        # 创建一个 TCP 连接
        with socket.create_connection((host, port), timeout=timeout) as s:
            # 自定义请求，这里只是一个占位符，需根据具体协议定义
            request = f"YOUR_CUSTOM_REQUEST {path}\r\nHost: {host}\r\n\r\n"
            s.sendall(request.encode())
            
            # 读取响应
            response = s.recv(1024)
            
            # 自定义响应解析，这里简单示例
            if b"SOME_EXPECTED_RESPONSE" in response:
                return True
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return False

# 处理单行文本并检测URL
def process_line(line):
    if "#genre#" in line or "://" not in line :
        return None, None  # 跳过包含“#genre#”的行
    parts = line.split(',')
    if len(parts) == 2:
        name, url = parts
        elapsed_time, is_valid = check_url(url.strip())
        if is_valid:
            return elapsed_time, line.strip()
        else:
            return None, line.strip()
    return None, None

# 多线程处理文本并检测URL
def process_urls_multithreaded(lines, max_workers=18):
    blacklist =  [] 
    successlist = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_line, line): line for line in lines}
        for future in as_completed(futures):
            elapsed_time, result = future.result()
            if result:
                if elapsed_time is not None:
                    successlist.append(f"{elapsed_time:.2f}ms,{result}")
                else:
                    blacklist.append(result)
    return successlist, blacklist

# 写入文件
def write_list(file_path, data_list):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data_list:
            file.write(item + '\n')

# 增加外部url到检测清单，同时支持检测m3u格式url
# urls里所有的源都读到这里。
urls_all_lines = []

def get_url_file_extension(url):
    # 解析URL
    parsed_url = urlparse(url)
    # 获取路径部分
    path = parsed_url.path
    # 提取文件扩展名
    extension = os.path.splitext(path)[1]
    return extension

def convert_m3u_to_txt(m3u_content):
    # 分行处理
    lines = m3u_content.split('\n')
    
    # 用于存储结果的列表
    txt_lines = []
    
    # 临时变量用于存储频道名称
    channel_name = ""
    
    for line in lines:
        # 过滤掉 #EXTM3U 开头的行
        if line.startswith("#EXTM3U"):
            continue
        # 处理 #EXTINF 开头的行
        if line.startswith("#EXTINF"):
            # 获取频道名称（假设频道名称在引号后）
            channel_name = line.split(',')[-1].strip()
        # 处理 URL 行
        elif line.startswith("http"):
            txt_lines.append(f"{channel_name},{line.strip()}")
    
    # print(f"js: {len(txt_lines)} ")
    # 将结果合并成一个字符串，以换行符分隔
    #return '\n'.join(txt_lines)
    return txt_lines

def process_url(url):
    try:
        # 打开URL并读取内容
        with urllib.request.urlopen(url) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            if get_url_file_extension(url)==".m3u" or get_url_file_extension(url)==".m3u8":
                m3u_lines=convert_m3u_to_txt(text)
                print(f"url: {url} ")
                print(f"js: {len(m3u_lines)} ")
                urls_all_lines.extend(m3u_lines)
            elif get_url_file_extension(url)==".txt":
                lines = text.split('\n')
                for line in lines:
                    if  "#genre#" not in line and "," in line and "://" in line:
                        #channel_name=line.split(',')[0].strip()
                        #channel_address=line.split(',')[1].strip()
                        urls_all_lines.append(line.strip())
            
            
    
    except Exception as e:
        print(f"处理URL时发生错误：{e}")


# 去重复源 2024-08-06 (检测前剔除重复url，提高检测效率)
def remove_duplicates_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            # channel_name=line.split(',')[0].strip()
            channel_url=line.split(',')[1].strip()
            if channel_url not in urls: # 如果发现当前url不在清单中，则假如newlines
                urls.append(channel_url)
                newlines.append(line)
    return newlines

# 处理带$的URL，把$之后的内容都去掉（包括$也去掉） 【2024-08-08 22:29:11】
#def clean_url(url):
#    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
#    if last_dollar_index != -1:
#        return url[:last_dollar_index]
#    return url
def clean_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            last_dollar_index = line.rfind('$')
            if last_dollar_index != -1:
                line=line[:last_dollar_index]
            newlines.append(line)
    return newlines

# 处理带#的URL  【2024-08-09 23:53:26】
def split_url(lines):
    newlines=[]
    for line in lines:
        # 拆分成频道名和URL部分
        channel_name, channel_address = line.split(',', 1)
        #需要加处理带#号源=予加速源
        if  "#" not in channel_address:
            newlines.append(line)
        elif  "#" in channel_address and "://" in channel_address: 
            # 如果有“#”号，则根据“#”号分隔
            url_list = channel_address.split('#')
            for url in url_list:
                if "://" in url: 
                    newline=f'{channel_name},{url}'
                    newlines.append(line)
    return newlines

if __name__ == "__main__":
    # 定义要访问的多个URL
    urls = [
        'https://freetv.fun/test_channels_original_new.txt'
        #'https://raw.githubusercontent.com/xiangjiao169/yf2025/main/yf169.txt'
        #'',
        #''
    ]
    for url in urls:
        print(f"处理URL: {url}")
        process_url(url)   #读取上面url清单中直播源存入urls_all_lines

    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取上一层目录
    parent_dir = os.path.dirname(current_dir)

    # input_file1 = os.path.join(parent_dir, 'merged_output.txt')  # 输入文件路径1
    # input_file2 = os.path.join(current_dir, 'blacklist_auto.txt')  # 输入文件路径2 
    success_file = os.path.join(current_dir, 'test_whitelist_auto.txt')  # 成功清单文件路径
    success_file_tv = os.path.join(current_dir, 'test_whitelist_auto_tv.txt')  # 成功清单文件路径
    blacklist_file = os.path.join(current_dir, 'test_blacklist_auto.txt')  # 黑名单文件路径

    # 读取输入文件内容
    # lines1 = read_txt_file(input_file1)
    # lines2 = read_txt_file(input_file2)
    lines=urls_all_lines # 从list变成集合提供检索效率⇒发现用了set后加#合并多行url，故去掉
    # 计算合并后合计个数
    urls_hj_before = len(lines)

    # 分级带#号直播源地址
    lines=split_url(lines)
    urls_hj_before2 = len(lines)

    # 去$
    lines=clean_url(lines)
    urls_hj_before3 = len(lines)

    # 去重
    lines=remove_duplicates_url(lines)
    urls_hj = len(lines)

    # 处理URL并生成成功清单和黑名单
    successlist, blacklist = process_urls_multithreaded(lines)
    
    # 给successlist, blacklist排序
    # 定义排序函数
    def successlist_sort_key(item):
        time_str = item.split(',')[0].replace('ms', '')
        return float(time_str)
    
    successlist=sorted(successlist, key=successlist_sort_key)
    blacklist=sorted(blacklist)

    # 计算check后ok和ng个数
    urls_ok = len(successlist)
    urls_ng = len(blacklist)

    # 把successlist整理一下，生成一个可以直接引用的源，方便用zyplayer手动check
    def remove_prefix_from_lines(lines):
        result = []
        for line in lines:
            if  "#genre#" not in line and "," in line and "://" in line:
                parts = line.split(",")
                result.append(",".join(parts[1:]))
        return result


    # 加时间戳等
    version=datetime.now().strftime("%Y%m%d-%H-%M-%S")+",url"
    successlist_tv = ["更新时间,#genre#"] +[version] + ['\n'] +\
                  ["whitelist,#genre#"] + remove_prefix_from_lines(successlist)
    successlist = ["更新时间,#genre#"] +[version] + ['\n'] +\
                  ["RespoTime,whitelist,#genre#"] + successlist
    blacklist = ["更新时间,#genre#"] +[version] + ['\n'] +\
                ["blacklist,#genre#"]  + blacklist

    # 写入成功清单文件
    write_list(success_file, successlist)
    write_list(success_file_tv, successlist_tv)

    # 写入黑名单文件
    write_list(blacklist_file, blacklist)

    print(f"成功清单文件已生成: {success_file}")
    print(f"成功清单文件已生成(tv): {success_file_tv}")
    print(f"黑名单文件已生成: {blacklist_file}")

    # 写入history
    timenow=datetime.now().strftime("%Y%m%d_%H_%M_%S")
    history_success_file = f'history/blacklist/{timenow}_whitelist_auto.txt'
    history_blacklist_file = f'history/blacklist/{timenow}_blacklist_auto.txt'
    write_list(history_success_file, successlist)
    write_list(history_blacklist_file, blacklist)
    print(f"history成功清单文件已生成: {history_success_file}")
    print(f"history黑名单文件已生成: {history_blacklist_file}")

    # 执行的代码
    timeend = datetime.now()

    # 计算时间差
    elapsed_time = timeend - timestart
    total_seconds = elapsed_time.total_seconds()

    # 转换为分钟和秒
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    # 格式化开始和结束时间
    timestart_str = timestart.strftime("%Y%m%d_%H_%M_%S")
    timeend_str = timeend.strftime("%Y%m%d_%H_%M_%S")

    print(f"开始时间: {timestart_str}")
    print(f"结束时间: {timeend_str}")
    print(f"执行时间: {minutes} 分 {seconds} 秒")
    print(f"urls_hj最初: {urls_hj_before} ")
    print(f"urls_hj分解井号源后: {urls_hj_before2} ")
    print(f"urls_hj去$后: {urls_hj_before3} ")
    print(f"urls_hj去重后: {urls_hj} ")
    print(f"  urls_ok: {urls_ok} ")
    print(f"  urls_ng: {urls_ng} ")
            

    
