import re
import base64
import requests
from bs4 import BeautifulSoup

#[url]=https://fofa.info/result?qbase64={0}&page={1}&page_size=10

#（组播）"udpxy" && country="CN" && region="Jiangsu" && protocol="http"
#InVkcHh5IiAmJiBjb3VudHJ5PSJDTiIgJiYgcmVnaW9uPSJKaWFuZ3N1IiAmJiBwcm90b2NvbD0iaHR0cCI%3D

#（组播）"udpxy" && country="CN" && region="Jiangsu" && org="Chinanet"
#InVkcHh5IiAmJiBjb3VudHJ5PSJDTiIgJiYgcmVnaW9uPSLmsZ%2Foi48iICYmIG9yZz0iQ2hpbmFuZXQi

#（酒店）"ZHGXTV" && region="Shanghai"
#IlpIR1hUViIgJiYgcmVnaW9uPSLkuIrmtbci


# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://fofa.info/',
}

search_url = 'https://fofa.info/result?qbase64='
search_txt = 'InVkcHh5IiAmJiBjb3VudHJ5PSJDTiIgJiYgcmVnaW9uPSJKaWFuZ3N1IiAmJiBwcm90b2NvbD0iaHR0cCI%3D'

# 编码查询字符串
bytes_string = search_txt.encode('utf-8')
search_txt = base64.b64encode(bytes_string).decode('utf-8')
search_url += search_txt

print(f"查询地址 : {search_url}")

# 发送带有头部信息的请求
response = requests.get(search_url, headers=headers, timeout=30)
response.raise_for_status()  # 检查是否请求成功
html_content = response.text

# 使用BeautifulSoup解析网页内容
html_soup = BeautifulSoup(html_content, "html.parser")
#print(f"html_content:{html_content}")

# 查找所有符合指定格式的网址
# 设置匹配的格式，如http://8.8.8.8:8888
pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
urls_all = re.findall(pattern, html_content)
print(f"urls_all:{len(urls_all)}")

# 去重得到唯一的URL列表
result_urls = set(urls_all)
print(f"result_urls:{result_urls}")

# --------------------------------------
# 防止频繁访问或者访问过快
# import time
# import random

# # 在每个请求前加上随机延时
# time.sleep(random.uniform(1, 5))  # 延迟 1 到 5 秒之间的随机时间