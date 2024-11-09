import os
import requests
from datetime import datetime, timedelta, timezone


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

# 定义
urls = read_txt_to_array('assets/snapshot/urls.txt')

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取当前日期并创建文件夹
current_date = datetime.now().strftime('%Y-%m-%d')
folder_name = os.path.join(current_dir, current_date)

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 下载文件并保存到文件夹
for url in urls:
    if url.startswith("http"):
        if "{MMdd}" in url: #特别处理113
            current_date_str = datetime.now().strftime("%m%d")
            url=url.replace("{MMdd}", current_date_str)

        if "{MMdd-1}" in url: #特别处理113
            yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%m%d")
            url=url.replace("{MMdd-1}", yesterday_date_str)

        try:
            # 获取文件内容
            response = requests.get(url)
            if response.status_code == 200:
                # 生成带时间戳的文件名
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                file_name = url.split('/')[-1]
                file_path = os.path.join(folder_name, f"{timestamp}_{file_name}")
                
                # 将内容写入文件
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                
                print(f"文件已保存：{file_path}")
            else:
                print(f"无法下载文件：{url}")
        
        except Exception as e:
            print(f"处理URL时发生错误：{e}")
