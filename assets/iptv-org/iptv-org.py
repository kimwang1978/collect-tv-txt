
import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta, timezone


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
rename_dic = load_modify_name('assets/iptv-org/iptv_org_rename.txt')

# 定义
freetv_lines = []

# 定义
urls = [
    "https://iptv-org.github.io/iptv/languages/zho.m3u",
    # "https://iptv-org.github.io/iptv/countries/us.m3u",
    "https://iptv-org.github.io/iptv/countries/tw.m3u"
        ]




