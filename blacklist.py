import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from datetime import datetime


# 读取文件内容
def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

# 检测URL是否可访问并记录响应时间
def check_url(url, timeout=5):
    try:
    	if  "://" in url:
            start_time = time.time()
            with urllib.request.urlopen(url, timeout=timeout) as response:
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
def process_urls_multithreaded(lines, max_workers=10):
    blacklist = []
    successlist = []

    version=datetime.now().strftime("%Y%m%d-%H-%M-%S")+",url"
    blacklist.append("更新时间,#genre#")
    blacklist.append(version)
    blacklist.append("blacklist,#genre#")

    successlist.append("更新时间,#genre#")
    successlist.append(version)
    successlist.append("RespoTime,whitelist,#genre#")

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

if __name__ == "__main__":
    input_file = 'merged_output.txt'  # 输入文件路径
    success_file = 'whitelist_auto.txt'  # 成功清单文件路径
    blacklist_file = 'blacklist_auto.txt'  # 黑名单文件路径

    # 读取输入文件内容
    lines = read_txt_file(input_file)

    # 处理URL并生成成功清单和黑名单
    successlist, blacklist = process_urls_multithreaded(lines)

    # 写入成功清单文件
    write_list(success_file, successlist)

    # 写入黑名单文件
    write_list(blacklist_file, blacklist)

    print(f"成功清单文件已生成: {success_file}")
    print(f"黑名单文件已生成: {blacklist_file}")
