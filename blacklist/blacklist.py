import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import os
from urllib.parse import urlparse


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

# 检测URL是否可访问并记录响应时间
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}
def check_url(url, timeout=8):
    try:
    	if  "://" in url:
            start_time = time.time()
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
                if response.status == 200:
                    return elapsed_time, True
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return None, False

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
def process_urls_multithreaded(lines, max_workers=50):
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
    
    # 将结果合并成一个字符串，以换行符分隔
    return '\n'.join(txt_lines)


def process_url(url):
    try:
        # 打开URL并读取内容
        with urllib.request.urlopen(url) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            if get_url_file_extension(url)==".m3u" or get_url_file_extension(url)==".m3u8":
                urls_all_lines.append(convert_m3u_to_txt(text))
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

if __name__ == "__main__":
    # 定义要访问的多个URL
    urls = [
        'https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u',
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u',
        'https://gitlab.com/p2v5/wangtv/-/raw/main/wang-tvlive.txt',
        'https://raw.githubusercontent.com/kimwang1978/tvbox/main/%E5%A4%A9%E5%A4%A9%E5%BC%80%E5%BF%83/lives/%E2%91%AD%E5%BC%80%E5%BF%83%E7%BA%BF%E8%B7%AF.txt',
        'https://raw.githubusercontent.com/mlvjfchen/TV/main/iptv_list.txt', 
        'https://raw.githubusercontent.com/gdstchdr1/IPTV/main/bc.txt',  #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/skddyj/iptv/main/IPTV.m3u',  #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/wwb521/live/main/tv.m3u',  #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/lalifeier/IPTV/main/txt/IPTV.txt',  #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/yoursmile66/TVBox/main/live.txt',  #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8', #15分钟更新1次   #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/PizazzGY/TVBox/main/live.txt', #ADD 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/pxiptv/live/main/iptv.txt', #ADD 【2024-08-02 16:48:40】#每日更新1次
        'https://notabug.org/vnjd/yydu/raw/master/yyfug.txt', #ADD 【2024-08-06】
        'https://tvkj.top/tvlive.txt', #ADD 【2024-08-06】
        'https://pan.beecld.com/f/OXMcA/%E6%98%A5%E8%B5%A2%E5%A4%A9%E4%B8%8B.txt', #ADD 【2024-08-06】
        'http://kxrj.site:55/lib/kx2024.txt',   #ADD 【2024-08-07】
        'https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt',   #ADD 2024-08-05 每天更新一次
        'https://raw.githubusercontent.com/balala2oo8/iptv/main/o.m3u',   #ADD 【2024-08-07】#每日更新2次
        'https://wzsvip.github.io/ipv4.txt',   #ADD 【2024-08-08】
        'http://wz.42web.io/ipv4.txt',   #ADD 【2024-08-08】
        'https://wzsvip.github.io/ipv4.m3u'   #ADD 【2024-08-08】
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

    input_file1 = os.path.join(parent_dir, 'merged_output.txt')  # 输入文件路径1
    input_file2 = os.path.join(current_dir, 'blacklist_auto.txt')  # 输入文件路径2 
    success_file = os.path.join(current_dir, 'whitelist_auto.txt')  # 成功清单文件路径
    success_file_tv = os.path.join(current_dir, 'whitelist_auto_tv.txt')  # 成功清单文件路径（另存一份直接引用源）
    blacklist_file = os.path.join(current_dir, 'blacklist_auto.txt')  # 黑名单文件路径

    # 读取输入文件内容
    lines1 = read_txt_file(input_file1)
    lines2 = read_txt_file(input_file2)
    # lines=list(set(urls_all_lines + lines1 + lines2))
    lines=set(urls_all_lines + lines1 + lines2) # 从list变成集合提供检索效率
    # 计算合并后合计个数
    urls_hj_before = len(lines)

    # 去$
    lines=clean_url(lines)
    urls_hj_before2 = len(lines)

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
    
    successlist=sorted(set(successlist), key=successlist_sort_key)
    blacklist=sorted(set(blacklist))

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
    write_list(history_blacklist_file, successlist)
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
    print(f"urls_hj去$前: {urls_hj_before2} ")
    print(f"urls_hj去重后: {urls_hj} ")
    print(f"  urls_ok: {urls_ok} ")
    print(f"  urls_ng: {urls_ng} ")
            

    
