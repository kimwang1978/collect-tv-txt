import urllib.request
from urllib.parse import urlparse
import re #正则
import os
from datetime import datetime, timedelta, timezone
import random
import opencc #简繁转换

#简繁转换
def traditional_to_simplified(text: str) -> str:
    # 初始化转换器，"t2s" 表示从繁体转为简体
    converter = opencc.OpenCC('t2s')
    simplified_text = converter.convert(text)
    return simplified_text

# 执行开始时间
timestart = datetime.now()
# 报时  '',
#print(f"time: {datetime.now().strftime("%Y%m%d_%H_%M_%S")}")

#读取文本方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]  # 跳过空行
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

#read BlackList 2024-06-17 15:02
def read_blacklist_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    BlackList = [line.split(',')[1].strip() for line in lines if ',' in line]
    return BlackList

blacklist_auto=read_blacklist_from_txt('assets/blacklist1/blacklist_auto.txt') 
blacklist_manual=read_blacklist_from_txt('assets/blacklist1/blacklist_manual.txt') 
# combined_blacklist = list(set(blacklist_auto + blacklist_manual))
combined_blacklist = set(blacklist_auto + blacklist_manual)  #list是个列表，set是个集合，据说检索速度集合要快很多。2024-08-08

# 定义多个对象用于存储不同内容的行文本
sh_lines = []
ys_lines = [] #CCTV
ws_lines = [] #卫视频道
ty_lines = [] #体育频道
dy_lines = []
dsj_lines = []
gat_lines = [] #港澳台
gj_lines = [] #国际台
jlp_lines = [] #记录片
dhp_lines = [] #动画片
xq_lines = [] #戏曲
js_lines = [] #解说
cw_lines = [] #春晚
mx_lines = [] #明星
ztp_lines = [] #主题片
zy_lines = [] #综艺频道
yy_lines = [] #音乐频道
game_lines = [] #游戏频道
radio_lines = [] #收音机频道

zj_lines = [] #地方台-浙江频道
jsu_lines = [] #地方台-江苏频道
gd_lines = [] #地方台-广东频道
hn_lines = [] #地方台-湖南频道
ah_lines = [] #地方台-安徽频道
hain_lines = [] #地方台-海南频道
nm_lines = [] #地方台-内蒙频道
hb_lines = [] #地方台-湖北频道
ln_lines = [] #地方台-辽宁频道
sx_lines = [] #地方台-陕西频道
shanxi_lines = [] #地方台-山西频道
shandong_lines = [] #地方台-山东频道
yunnan_lines = [] #地方台-云南频道


##################【2024-07-30 18:04:56】
bj_lines = [] #地方台-北京频道
cq_lines = [] #地方台-重庆频道
fj_lines = [] #地方台-福建频道
gs_lines = [] #地方台-甘肃频道
gx_lines = [] #地方台-广西频道
gz_lines = [] #地方台-贵州频道
heb_lines = [] #地方台-河北频道
hen_lines = [] #地方台-河南频道
hlj_lines = [] #地方台-黑龙江频道
jl_lines = [] #地方台-吉林频道
jx_lines = [] #地方台-江西频道
nx_lines = [] #地方台-宁夏频道
qh_lines = [] #地方台-青海频道
sc_lines = [] #地方台-四川频道
tj_lines = [] #地方台-天津频道
xj_lines = [] #地方台-新疆频道

zb_lines = [] #直播中国
mtv_lines = [] #MTV

Olympics_2024_Paris_lines = [] #Paris_2024_Olympics  Olympics_2024_Paris ADD 2024-08-05
# favorite_lines = []

other_lines = []
other_lines_url = [] # 为降低other文件大小，剔除重复url添加

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
    if "CCTV" in part_str  and "://" not in part_str:
        part_str=part_str.replace("IPV6", "")  #先剔除IPV6字样
        part_str=part_str.replace("PLUS", "+")  #替换PLUS
        part_str=part_str.replace("1080", "")  #替换1080
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        if not filtered_str.strip(): #处理特殊情况，如果发现没有找到频道数字返回原名称
            filtered_str=part_str.replace("CCTV", "")

        if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):   # 特殊处理CCTV中部分4K和8K名称
            # 使用正则表达式替换，删除4K或8K后面的字符，并且保留4K或8K
            filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
            if len(filtered_str) > 2: 
                # 给4K或8K添加括号
                filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)

        return "CCTV"+filtered_str 
        
    elif "卫视" in part_str:
        # 定义正则表达式模式，匹配“卫视”后面的内容
        pattern = r'卫视「.*」'
        # 使用sub函数替换匹配的内容为空字符串
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str
    
    return part_str

# 准备支持m3u格式
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
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p") :
            txt_lines.append(f"{channel_name},{line.strip()}")
        
        # 处理后缀名为m3u，但是内容为txt的文件
        if "#genre#" not in line and "," in line and "://" in line:
            # 定义正则表达式，匹配频道名称,URL 的格式，并确保 URL 包含 "://"
            # xxxx,http://xxxxx.xx.xx
            pattern = r'^[^,]+,[^\s]+://[^\s]+$'
            if bool(re.match(pattern, line)):
                txt_lines.append(line)
    
    # 将结果合并成一个字符串，以换行符分隔
    return '\n'.join(txt_lines)

# 在list是否已经存在url 2024-07-22 11:18
def check_url_existence(data_list, url):
    """
    Check if a given URL exists in a list of data.

    :param data_list: List of strings containing the data
    :param url: The URL to check for existence
    :return: True if the URL exists in the list, otherwise False
    """
    # Extract URLs from the data list
    urls = [item.split(',')[1] for item in data_list]
    return url not in urls #如果不存在则返回true，需要

# 处理带$的URL，把$之后的内容都去掉（包括$也去掉） 【2024-08-08 22:29:11】
def clean_url(url):
    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

# 添加channel_name前剔除部分特定字符
removal_list = ["_电信", "电信", "高清", "频道", "（HD）", "-HD","英陆","_ITV","(北美)","(HK)","AKtv","「IPV4」","「IPV6」",
                "频陆","备陆","壹陆","贰陆","叁陆","肆陆","伍陆","陆陆","柒陆", "频晴","频粤","[超清]","高清","超清","标清","斯特",
                "粤陆", "国陆","肆柒","频英","频特","频国","频壹","频贰","肆贰","频测","咪咕"]
def clean_channel_name(channel_name, removal_list):
    for item in removal_list:
        channel_name = channel_name.replace(item, "")

    # 检查并移除末尾的 'HD'
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]  # 去掉最后两个字符 "HD"
    
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]  # 去掉最后两个字符 "台"

    return channel_name

# 分发直播源，归类，把这部分从process_url剥离出来，为以后加入whitelist源清单做准备。
def process_channel_line(line):
    if  "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        channel_name=line.split(',')[0].strip()
        channel_name= clean_channel_name(channel_name, removal_list)  #分发前清理channel_name中特定字符
        channel_name = traditional_to_simplified(channel_name)  #繁转简

        channel_address=clean_url(line.split(',')[1].strip())  #把URL中$之后的内容都去掉
        line=channel_name+","+channel_address #重新组织line

        if channel_address not in combined_blacklist: # 判断当前源是否在blacklist中
            # 根据行内容判断存入哪个对象，开始分发
            if "CCTV" in channel_name and check_url_existence(ys_lines, channel_address) : #央视频道
                ys_lines.append(process_name_string(line.strip()))
            # elif channel_name in Olympics_2024_Paris_dictionary and check_url_existence(Olympics_2024_Paris_lines, channel_address): #奥运频道 ADD 2024-08-05
            #     Olympics_2024_Paris_lines.append(process_name_string(line.strip()))
            elif channel_name in ws_dictionary and check_url_existence(ws_lines, channel_address): #卫视频道
                ws_lines.append(process_name_string(line.strip()))
            elif channel_name in ty_dictionary and check_url_existence(ty_lines, channel_address):  #体育频道
                ty_lines.append(process_name_string(line.strip()))
            elif channel_name in dy_dictionary and check_url_existence(dy_lines, channel_address):  #电影频道
                dy_lines.append(process_name_string(line.strip()))
            elif channel_name in dsj_dictionary and check_url_existence(dsj_lines, channel_address):  #电视剧频道
                dsj_lines.append(process_name_string(line.strip()))
            elif channel_name in sh_dictionary and check_url_existence(sh_lines, channel_address):  #上海频道
                sh_lines.append(process_name_string(line.strip()))
            elif channel_name in gat_dictionary and check_url_existence(gat_lines, channel_address):  #港澳台
                gat_lines.append(process_name_string(line.strip()))
            elif channel_name in gj_dictionary and check_url_existence(gj_lines, channel_address):  #国际台
                gj_lines.append(process_name_string(line.strip()))
            elif channel_name in jlp_dictionary and check_url_existence(jlp_lines, channel_address):  #纪录片
                jlp_lines.append(process_name_string(line.strip()))
            elif channel_name in dhp_dictionary and check_url_existence(dhp_lines, channel_address):  #动画片
                dhp_lines.append(process_name_string(line.strip()))
            elif channel_name in xq_dictionary and check_url_existence(xq_lines, channel_address):  #戏曲
                xq_lines.append(process_name_string(line.strip()))
            elif channel_name in js_dictionary and check_url_existence(js_lines, channel_address):  #解说
                js_lines.append(process_name_string(line.strip()))
            elif channel_name in cw_dictionary and check_url_existence(cw_lines, channel_address):  #春晚
                cw_lines.append(process_name_string(line.strip()))
            elif channel_name in mx_dictionary and check_url_existence(mx_lines, channel_address):  #明星
                mx_lines.append(process_name_string(line.strip()))
            elif channel_name in ztp_dictionary and check_url_existence(ztp_lines, channel_address):  #主题片
                ztp_lines.append(process_name_string(line.strip()))
            elif channel_name in zy_dictionary and check_url_existence(zy_lines, channel_address):  #综艺频道
                zy_lines.append(process_name_string(line.strip()))
            elif channel_name in yy_dictionary and check_url_existence(yy_lines, channel_address):  #音乐频道
                yy_lines.append(process_name_string(line.strip()))
            elif channel_name in game_dictionary and check_url_existence(game_lines, channel_address):  #游戏频道
                game_lines.append(process_name_string(line.strip()))
            elif channel_name in radio_dictionary and check_url_existence(radio_lines, channel_address):  #收音机频道
                radio_lines.append(process_name_string(line.strip()))
            elif channel_name in zj_dictionary and check_url_existence(zj_lines, channel_address):  #地方台-浙江频道
                zj_lines.append(process_name_string(line.strip()))
            elif channel_name in jsu_dictionary and check_url_existence(jsu_lines, channel_address):  #地方台-江苏频道
                jsu_lines.append(process_name_string(line.strip()))
            elif channel_name in gd_dictionary and check_url_existence(gd_lines, channel_address):  #地方台-广东频道
                gd_lines.append(process_name_string(line.strip()))
            elif channel_name in hn_dictionary and check_url_existence(hn_lines, channel_address):  #地方台-湖南频道
                hn_lines.append(process_name_string(line.strip()))
            elif channel_name in hb_dictionary and check_url_existence(hb_lines, channel_address):  #地方台-湖北频道
                hb_lines.append(process_name_string(line.strip()))
            elif channel_name in ah_dictionary and check_url_existence(ah_lines, channel_address):  #地方台-安徽频道
                ah_lines.append(process_name_string(line.strip()))
            elif channel_name in hain_dictionary and check_url_existence(hain_lines, channel_address):  #地方台-海南频道
                hain_lines.append(process_name_string(line.strip()))
            elif channel_name in nm_dictionary and check_url_existence(nm_lines, channel_address):  #地方台-内蒙频道
                nm_lines.append(process_name_string(line.strip()))
            elif channel_name in ln_dictionary and check_url_existence(ln_lines, channel_address):  #地方台-辽宁频道
                ln_lines.append(process_name_string(line.strip()))
            elif channel_name in sx_dictionary and check_url_existence(sx_lines, channel_address):  #地方台-陕西频道
                sx_lines.append(process_name_string(line.strip()))
            elif channel_name in shanxi_dictionary and check_url_existence(shanxi_lines, channel_address):  #地方台-山西频道
                shanxi_lines.append(process_name_string(line.strip()))
            elif channel_name in shandong_dictionary and check_url_existence(shandong_lines, channel_address):  #地方台-山东频道
                shandong_lines.append(process_name_string(line.strip()))
            elif channel_name in yunnan_dictionary and check_url_existence(yunnan_lines, channel_address):  #地方台-云南频道
                yunnan_lines.append(process_name_string(line.strip()))
            elif channel_name in bj_dictionary and check_url_existence(bj_lines, channel_address):  #地方台-北京频道 ADD【2024-07-30 20:52:53】
                bj_lines.append(process_name_string(line.strip()))
            elif channel_name in cq_dictionary and check_url_existence(cq_lines, channel_address):  #地方台-重庆频道 ADD【2024-07-30 20:52:53】
                cq_lines.append(process_name_string(line.strip()))
            elif channel_name in fj_dictionary and check_url_existence(fj_lines, channel_address):  #地方台-福建频道 ADD【2024-07-30 20:52:53】
                            fj_lines.append(process_name_string(line.strip()))
            elif channel_name in gs_dictionary and check_url_existence(gs_lines, channel_address):  #地方台-甘肃频道 ADD【2024-07-30 20:52:53】
                gs_lines.append(process_name_string(line.strip()))
            elif channel_name in gx_dictionary and check_url_existence(gx_lines, channel_address):  #地方台-广西频道 ADD【2024-07-30 20:52:53】
                gx_lines.append(process_name_string(line.strip()))
            elif channel_name in gz_dictionary and check_url_existence(gz_lines, channel_address):  #地方台-贵州频道 ADD【2024-07-30 20:52:53】
                gz_lines.append(process_name_string(line.strip()))
            elif channel_name in heb_dictionary and check_url_existence(heb_lines, channel_address):  #地方台-河北频道 ADD【2024-07-30 20:52:53】
                heb_lines.append(process_name_string(line.strip()))
            elif channel_name in hen_dictionary and check_url_existence(hen_lines, channel_address):  #地方台-河南频道 ADD【2024-07-30 20:52:53】
                hen_lines.append(process_name_string(line.strip()))
            elif channel_name in hlj_dictionary and check_url_existence(hlj_lines, channel_address):  #地方台-黑龙江频道 ADD【2024-07-30 20:52:53】
                hlj_lines.append(process_name_string(line.strip()))
            elif channel_name in jl_dictionary and check_url_existence(jl_lines, channel_address):  #地方台-吉林频道 ADD【2024-07-30 20:52:53】
                jl_lines.append(process_name_string(line.strip()))
            elif channel_name in nx_dictionary and check_url_existence(nx_lines, channel_address):  #地方台-宁夏频道 ADD【2024-07-30 20:52:53】
                nx_lines.append(process_name_string(line.strip()))
            elif channel_name in jx_dictionary and check_url_existence(jx_lines, channel_address):  #地方台-江西频道 ADD【2024-07-30 20:52:53】
                jx_lines.append(process_name_string(line.strip()))
            elif channel_name in qh_dictionary and check_url_existence(qh_lines, channel_address):  #地方台-青海频道 ADD【2024-07-30 20:52:53】
                qh_lines.append(process_name_string(line.strip()))
            elif channel_name in sc_dictionary and check_url_existence(sc_lines, channel_address):  #地方台-四川频道 ADD【2024-07-30 20:52:53】
                sc_lines.append(process_name_string(line.strip()))
            elif channel_name in tj_dictionary and check_url_existence(tj_lines, channel_address):  #地方台-天津频道 ADD【2024-07-30 20:52:53】
                tj_lines.append(process_name_string(line.strip()))
            elif channel_name in xj_dictionary and check_url_existence(xj_lines, channel_address):  #地方台-新疆频道 ADD【2024-07-30 20:52:53】
                xj_lines.append(process_name_string(line.strip()))
            elif channel_name in zb_dictionary and check_url_existence(zb_lines, channel_address):  #直播中国
                zb_lines.append(process_name_string(line.strip()))
            elif channel_name in mtv_dictionary and check_url_existence(mtv_lines, channel_address):  #MTV
                mtv_lines.append(process_name_string(line.strip()))
            else:
                if channel_address not in other_lines_url:
                    other_lines_url.append(channel_address)   #记录已加url
                    other_lines.append(line.strip())


# 随机获取User-Agent,备用 
def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

def process_url(url):
    try:
        other_lines.append("◆◆◆　"+url)  # 存入other_lines便于check 2024-08-02 10:41
        
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

            #处理m3u和m3u8，提取channel_name和channel_address
            if get_url_file_extension(url)==".m3u" or get_url_file_extension(url)==".m3u8":
                text=convert_m3u_to_txt(text)

            # 逐行处理内容
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            for line in lines:
                if  "#genre#" not in line and "," in line and "://" in line:
                    # 拆分成频道名和URL部分
                    channel_name, channel_address = line.split(',', 1)
                    #需要加处理带#号源=予加速源
                    if "#" not in channel_address:
                        process_channel_line(line) # 如果没有井号，则照常按照每行规则进行分发
                    else: 
                        # 如果有“#”号，则根据“#”号分隔
                        url_list = channel_address.split('#')
                        for channel_url in url_list:
                            newline=f'{channel_name},{channel_url}'
                            process_channel_line(newline)

            other_lines.append('\n') #每个url处理完成后，在other_lines加个回车 2024-08-02 10:46

    except Exception as e:
        print(f"处理URL时发生错误：{e}")


current_directory = os.getcwd()  #准备读取txt

#读取文本
ys_dictionary=read_txt_to_array('主频道/CCTV.txt') #仅排序用
sh_dictionary=read_txt_to_array('主频道/shanghai.txt') #过滤+排序
ws_dictionary=read_txt_to_array('主频道/卫视频道.txt') #过滤+排序
ty_dictionary=read_txt_to_array('主频道/体育频道.txt') #过滤
dy_dictionary=read_txt_to_array('主频道/电影.txt') #过滤
dsj_dictionary=read_txt_to_array('主频道/电视剧.txt') #过滤
gat_dictionary=read_txt_to_array('主频道/港澳台.txt') #过滤
gj_dictionary=read_txt_to_array('主频道/国际台.txt') #过滤
jlp_dictionary=read_txt_to_array('主频道/纪录片.txt') #过滤
dhp_dictionary=read_txt_to_array('主频道/动画片.txt') #过滤
xq_dictionary=read_txt_to_array('主频道/戏曲频道.txt') #过滤
js_dictionary=read_txt_to_array('主频道/解说频道.txt') #过滤
cw_dictionary=read_txt_to_array('主频道/春晚.txt') #过滤+排序
mx_dictionary=read_txt_to_array('主频道/明星.txt') #过滤
ztp_dictionary=read_txt_to_array('主频道/主题片.txt') #过滤
zy_dictionary=read_txt_to_array('主频道/综艺频道.txt') #过滤
yy_dictionary=read_txt_to_array('主频道/音乐频道.txt') #过滤
game_dictionary=read_txt_to_array('主频道/游戏频道.txt') #过滤
radio_dictionary=read_txt_to_array('主频道/收音机频道.txt') #过滤

zb_dictionary=read_txt_to_array('主频道/直播中国.txt') #过滤
mtv_dictionary=read_txt_to_array('主频道/MTV.txt') #过滤
#Olympics_2024_Paris_dictionary=read_txt_to_array('主频道/奥运频道.txt') #过滤

zj_dictionary=read_txt_to_array('地方台/浙江频道.txt') #过滤
jsu_dictionary=read_txt_to_array('地方台/江苏频道.txt') #过滤
gd_dictionary=read_txt_to_array('地方台/广东频道.txt') #过滤
hn_dictionary=read_txt_to_array('地方台/湖南频道.txt') #过滤
ah_dictionary=read_txt_to_array('地方台/安徽频道.txt') #过滤
hain_dictionary=read_txt_to_array('地方台/海南频道.txt') #过滤
nm_dictionary=read_txt_to_array('地方台/内蒙频道.txt') #过滤
hb_dictionary=read_txt_to_array('地方台/湖北频道.txt') #过滤
ln_dictionary=read_txt_to_array('地方台/辽宁频道.txt') #过滤
sx_dictionary=read_txt_to_array('地方台/陕西频道.txt') #过滤
shanxi_dictionary=read_txt_to_array('地方台/山西频道.txt') #过滤
shandong_dictionary=read_txt_to_array('地方台/山东频道.txt') #过滤
yunnan_dictionary=read_txt_to_array('地方台/云南频道.txt') #过滤

##################【2024-07-30 18:04:56】
bj_dictionary=read_txt_to_array('地方台/北京频道.txt') #过滤
cq_dictionary=read_txt_to_array('地方台/重庆频道.txt') #过滤
fj_dictionary=read_txt_to_array('地方台/福建频道.txt') #过滤
gs_dictionary=read_txt_to_array('地方台/甘肃频道.txt') #过滤
gx_dictionary=read_txt_to_array('地方台/广西频道.txt') #过滤
gz_dictionary=read_txt_to_array('地方台/贵州频道.txt') #过滤
heb_dictionary=read_txt_to_array('地方台/河北频道.txt') #过滤
hen_dictionary=read_txt_to_array('地方台/河南频道.txt') #过滤
hlj_dictionary=read_txt_to_array('地方台/黑龙江频道.txt') #过滤
jl_dictionary=read_txt_to_array('地方台/吉林频道.txt') #过滤
jx_dictionary=read_txt_to_array('地方台/江西频道.txt') #过滤
nx_dictionary=read_txt_to_array('地方台/宁夏频道.txt') #过滤
qh_dictionary=read_txt_to_array('地方台/青海频道.txt') #过滤
sc_dictionary=read_txt_to_array('地方台/四川频道.txt') #过滤
tj_dictionary=read_txt_to_array('地方台/天津频道.txt') #过滤
xj_dictionary=read_txt_to_array('地方台/新疆频道.txt') #过滤

#读取纠错频道名称方法
def load_corrections_name(filename):
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): #跳过空行
                continue
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

#读取纠错文件
corrections_name = load_corrections_name('assets/corrections_name.txt')

#纠错频道名称
#correct_name_data(corrections_name,xxxx)
def correct_name_data(corrections, data):
    corrected_data = []
    for line in data:
        name, url = line.split(',', 1)
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data


def sort_data(order, data):
    # 创建一个字典来存储每行数据的索引
    order_dict = {name: i for i, name in enumerate(order)}
    
    # 定义一个排序键函数，处理不在 order_dict 中的字符串
    def sort_key(line):
        name = line.split(',')[0]
        return order_dict.get(name, len(order))
    
    # 按照 order 中的顺序对数据进行排序
    sorted_data = sorted(data, key=sort_key)
    return sorted_data





# 定义
urls = read_txt_to_array('assets/urls-daily.txt')
# 处理
for url in urls:
    if url.startswith("http"):
        if "{MMdd}" in url: #特别处理113
            current_date_str = datetime.now().strftime("%m%d")
            url=url.replace("{MMdd}", current_date_str)

        if "{MMdd-1}" in url: #特别处理113
            yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%m%d")
            url=url.replace("{MMdd-1}", yesterday_date_str)
            
        print(f"处理URL: {url}")
        process_url(url)



# 定义一个函数，提取每行中逗号前面的数字部分作为排序的依据
def extract_number(s):
    num_str = s.split(',')[0].split('-')[1]  # 提取逗号前面的数字部分
    numbers = re.findall(r'\d+', num_str)   #因为有+和K
    return int(numbers[-1]) if numbers else 999
# 定义一个自定义排序函数
def custom_sort(s):
    if "CCTV-4K" in s:
        return 2  # 将包含 "4K" 的字符串排在后面
    elif "CCTV-8K" in s:
        return 3  # 将包含 "8K" 的字符串排在后面 
    elif "(4K)" in s:
        return 1  # 将包含 " (4K)" 的字符串排在后面
    else:
        return 0  # 其他字符串保持原顺序



#读取whitelist,把高响应源从白名单中抽出加入merged_output。
print(f"ADD whitelist_auto.txt")
whitelist_auto_lines=read_txt_to_array('assets/blacklist1/whitelist_auto.txt') #
for whitelist_line in whitelist_auto_lines:
    if  "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
        whitelist_parts = whitelist_line.split(",")
        try:
            response_time = float(whitelist_parts[0].replace("ms", ""))
        except ValueError:
            print(f"response_time转换失败: {whitelist_line}")
            response_time = 60000  # 单位毫秒，转换失败给个60秒
        if response_time < 2000:  #2s以内的高响应源
            process_channel_line(",".join(whitelist_parts[1:]))

# 随机取得URL
def get_random_url(file_path):
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 查找逗号后面的部分，即URL
            url = line.strip().split(',')[-1]
            urls.append(url)    
    # 随机返回一个URL
    return random.choice(urls) if urls else None

daily_mtv="(新)每日一首,"+get_random_url('assets/今日推荐.txt')

# 获取当前的 UTC 时间
utc_time = datetime.now(timezone.utc)
# 北京时间
beijing_time = utc_time + timedelta(hours=8)
# 格式化为所需的格式
formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")

about_video1="https://gitee.com/kabigo/tv/raw/master/assets/about1080p.mp4"
about_video2="https://gitlab.com/p2v5/wangtv/-/raw/main/about1080p.mp4"
version=formatted_time+","+about_video1
about="关于本源(iptv365.org),"+about_video2
# 瘦身版
# 
all_lines_simple =  ["更新时间,#genre#"] +[version] +[about] +[daily_mtv]+read_txt_to_array('专区/about.txt')+ ['\n'] +\
             ["🧨2025春晚🧨,#genre#"] + read_txt_to_array('专区/2025春晚.txt') + ['\n'] + \
             ["💓专享源🅰️,#genre#"] + read_txt_to_array('专区/♪专享源①.txt') + ['\n'] + \
             ["💓专享源🅱️,#genre#"] + read_txt_to_array('专区/♪专享源②.txt') + ['\n'] + \
             ["💓专享央视,#genre#"] + read_txt_to_array('专区/♪优质央视.txt') + ['\n'] + \
             ["💓专享卫视,#genre#"] + read_txt_to_array('专区/♪优质卫视.txt') + ['\n'] + \
             ["💓港澳台📶,#genre#"] + read_txt_to_array('专区/♪港澳台.txt') + ['\n'] + \
             ["💓AKTV🚀📶,#genre#"] + read_txt_to_array('专区/AKTV.txt') + ['\n'] + \
             ["💓台湾台📶,#genre#"] + read_txt_to_array('专区/♪台湾台.txt') + ['\n'] + \
             ["💓电视剧🔁,#genre#"] + read_txt_to_array('专区/♪电视剧.txt') + ['\n'] + \
             ["💓优质个源,#genre#"] + read_txt_to_array('专区/♪优质源.txt') + ['\n'] + \
             ["💓儿童专享,#genre#"] + read_txt_to_array('专区/♪儿童专享.txt') + ['\n'] + \
             ["💓咪咕直播,#genre#"] + read_txt_to_array('专区/♪咪咕直播.txt') + ['\n'] + \
             ["🏀SPORTS⚽️,#genre#"] + read_txt_to_array('专区/♪sports.txt') + ['\n'] + \
             ["🍹定制台☕️,#genre#"] + read_txt_to_array('专区/♪定制源.txt') + ['\n'] + \
             ["🍹定制P3P☕️,#genre#"] + read_txt_to_array('专区/p3p.txt') + ['\n'] + \
             ["💓英语频道,#genre#"] + read_txt_to_array('专区/♪英语频道.txt') + ['\n'] + \
             ["💓4K(Test),#genre#"] + read_txt_to_array('专区/4K.txt') + ['\n'] + \
             ["☘️湖南频道,#genre#"] + sort_data(hn_dictionary,set(correct_name_data(corrections_name,hn_lines))) + ['\n'] + \
             ["☘️湖北频道,#genre#"] + sort_data(hb_dictionary,set(correct_name_data(corrections_name,hb_lines))) + ['\n'] + \
             ["☘️广东频道,#genre#"] + sort_data(gd_dictionary,set(correct_name_data(corrections_name,gd_lines))) + ['\n'] + \
             ["☘️浙江频道,#genre#"] + sort_data(zj_dictionary,set(correct_name_data(corrections_name,zj_lines))) + ['\n'] + \
             ["☘️山东频道,#genre#"] + sort_data(shandong_dictionary,set(correct_name_data(corrections_name,shandong_lines))) + ['\n'] + \
             ["上海频道,#genre#"] + sort_data(sh_dictionary,set(correct_name_data(corrections_name,sh_lines))) + ['\n'] + \
             ["体育频道,#genre#"] + sort_data(ty_dictionary,set(correct_name_data(corrections_name,ty_lines))) + ['\n']

# 合并所有对象中的行文本（去重，排序后拼接）
# ["奥运频道,#genre#"] + sort_data(Olympics_2024_Paris_dictionary,set(correct_name_data(corrections_name,Olympics_2024_Paris_lines))) + ['\n'] + \
# 
all_lines =  ["更新时间,#genre#"] +[version]  +[about] +[daily_mtv]+read_txt_to_array('专区/about.txt') + ['\n'] +\
             ["🧨2025春晚🧨,#genre#"] + read_txt_to_array('专区/2025春晚.txt') + ['\n'] + \
             ["💓专享源🅰️,#genre#"] + read_txt_to_array('专区/♪专享源①.txt') + ['\n'] + \
             ["💓专享源🅱️,#genre#"] + read_txt_to_array('专区/♪专享源②.txt') + ['\n'] + \
             ["💓专享央视,#genre#"] + read_txt_to_array('专区/♪优质央视.txt') + ['\n'] + \
             ["💓专享卫视,#genre#"] + read_txt_to_array('专区/♪优质卫视.txt') + ['\n'] + \
             ["💓港澳台📶,#genre#"] + read_txt_to_array('专区/♪港澳台.txt') + ['\n'] + \
             ["💓AKTV🚀📶,#genre#"] + read_txt_to_array('专区/AKTV.txt') + ['\n'] + \
             ["💓台湾台📶,#genre#"] + read_txt_to_array('专区/♪台湾台.txt') + ['\n'] + \
             ["💓电视剧🔁,#genre#"] + read_txt_to_array('专区/♪电视剧.txt') + ['\n'] + \
             ["💓优质个源,#genre#"] + read_txt_to_array('专区/♪优质源.txt') + ['\n'] + \
             ["💓儿童专享,#genre#"] + read_txt_to_array('专区/♪儿童专享.txt') + ['\n'] + \
             ["💓咪咕直播,#genre#"] + read_txt_to_array('专区/♪咪咕直播.txt') + ['\n'] + \
             ["🏀SPORTS⚽️,#genre#"] + read_txt_to_array('专区/♪sports.txt') + ['\n'] + \
             ["🍹定制台☕️,#genre#"] + read_txt_to_array('专区/♪定制源.txt') + ['\n'] + \
             ["🍹定制P3P☕️,#genre#"] + read_txt_to_array('专区/p3p.txt') + ['\n'] + \
             ["💓英语频道,#genre#"] + read_txt_to_array('专区/♪英语频道.txt') + ['\n'] + \
             ["💓4K(Test),#genre#"] + read_txt_to_array('专区/4K.txt') + ['\n'] + \
             ["🌐央视频道,#genre#"] + sort_data(ys_dictionary,correct_name_data(corrections_name,ys_lines)) + ['\n'] + \
             ["📡卫视频道,#genre#"] + sort_data(ws_dictionary,correct_name_data(corrections_name,ws_lines)) + ['\n'] + \
             ["上海频道,#genre#"] + sort_data(sh_dictionary,correct_name_data(corrections_name,sh_lines)) + ['\n'] + \
             ["体育频道,#genre#"] + sort_data(ty_dictionary,correct_name_data(corrections_name,ty_lines)) + ['\n'] + \
             ["电影频道,#genre#"] + sort_data(dy_dictionary,correct_name_data(corrections_name,dy_lines)) + ['\n'] + \
             ["电视剧频道,#genre#"] + sort_data(dsj_dictionary,correct_name_data(corrections_name,dsj_lines)) + ['\n'] + \
             ["明星,#genre#"] + sort_data(mx_dictionary,correct_name_data(corrections_name,mx_lines)) + ['\n'] + \
             ["主题片,#genre#"] + sort_data(ztp_dictionary,correct_name_data(corrections_name,ztp_lines)) + ['\n'] + \
             ["港澳台,#genre#"] + sort_data(gat_dictionary,correct_name_data(corrections_name,gat_lines)) + ['\n'] + \
             ["国际台,#genre#"] + sort_data(gj_dictionary,set(correct_name_data(corrections_name,gj_lines))) + ['\n'] + \
             ["纪录片,#genre#"] + sort_data(jlp_dictionary,set(correct_name_data(corrections_name,jlp_lines)))+ ['\n'] + \
             ["动画片,#genre#"] + sort_data(dhp_dictionary,set(correct_name_data(corrections_name,dhp_lines)))+ ['\n'] + \
             ["戏曲频道,#genre#"] + sort_data(xq_dictionary,set(correct_name_data(corrections_name,xq_lines))) + ['\n'] + \
             ["综艺频道,#genre#"] + sorted(set(correct_name_data(corrections_name,zy_lines))) + ['\n'] + \
             ["音乐频道,#genre#"] + sorted(set(yy_lines)) + ['\n'] + \
             ["游戏频道,#genre#"] + sorted(set(game_lines)) + ['\n'] + \
             ["☘️湖南频道,#genre#"] + sort_data(hn_dictionary,set(correct_name_data(corrections_name,hn_lines))) + ['\n'] + \
             ["☘️湖北频道,#genre#"] + sort_data(hb_dictionary,set(correct_name_data(corrections_name,hb_lines))) + ['\n'] + \
             ["☘️广东频道,#genre#"] + sort_data(gd_dictionary,set(correct_name_data(corrections_name,gd_lines))) + ['\n'] + \
             ["☘️浙江频道,#genre#"] + sort_data(zj_dictionary,set(correct_name_data(corrections_name,zj_lines))) + ['\n'] + \
             ["☘️山东频道,#genre#"] + sort_data(shandong_dictionary,set(correct_name_data(corrections_name,shandong_lines))) + ['\n'] + \
             ["☘️江苏频道,#genre#"] + sorted(set(correct_name_data(corrections_name,jsu_lines))) + ['\n'] + \
             ["☘️安徽频道,#genre#"] + sorted(set(correct_name_data(corrections_name,ah_lines))) + ['\n'] + \
             ["☘️海南频道,#genre#"] + sorted(set(correct_name_data(corrections_name,hain_lines))) + ['\n'] + \
             ["☘️内蒙频道,#genre#"] + sorted(set(correct_name_data(corrections_name,nm_lines))) + ['\n'] + \
             ["☘️辽宁频道,#genre#"] + sorted(set(correct_name_data(corrections_name,ln_lines))) + ['\n'] + \
             ["☘️陕西频道,#genre#"] + sorted(set(correct_name_data(corrections_name,sx_lines))) + ['\n'] + \
             ["☘️山西频道,#genre#"] + sorted(set(correct_name_data(corrections_name,shanxi_lines))) + ['\n'] + \
             ["☘️云南频道,#genre#"] + sorted(set(correct_name_data(corrections_name,yunnan_lines))) + ['\n'] + \
             ["☘️北京频道,#genre#"] + sorted(set(correct_name_data(corrections_name,bj_lines))) + ['\n'] + \
             ["☘️重庆频道,#genre#"] + sorted(set(correct_name_data(corrections_name,cq_lines))) + ['\n'] + \
             ["☘️福建频道,#genre#"] + sorted(set(correct_name_data(corrections_name,fj_lines))) + ['\n'] + \
             ["☘️甘肃频道,#genre#"] + sorted(set(correct_name_data(corrections_name,gs_lines))) + ['\n'] + \
             ["☘️广西频道,#genre#"] + sorted(set(correct_name_data(corrections_name,gx_lines))) + ['\n'] + \
             ["☘️贵州频道,#genre#"] + sorted(set(correct_name_data(corrections_name,gz_lines))) + ['\n'] + \
             ["☘️河北频道,#genre#"] + sorted(set(correct_name_data(corrections_name,heb_lines))) + ['\n'] + \
             ["☘️河南频道,#genre#"] + sorted(set(correct_name_data(corrections_name,hen_lines))) + ['\n'] + \
             ["☘️黑龙江频道,#genre#"] + sorted(set(correct_name_data(corrections_name,hlj_lines))) + ['\n'] + \
             ["☘️吉林频道,#genre#"] + sorted(set(correct_name_data(corrections_name,jl_lines))) + ['\n'] + \
             ["☘️江西频道,#genre#"] + sorted(set(correct_name_data(corrections_name,jx_lines))) + ['\n'] + \
             ["☘️宁夏频道,#genre#"] + sorted(set(correct_name_data(corrections_name,nx_lines))) + ['\n'] + \
             ["☘️青海频道,#genre#"] + sorted(set(correct_name_data(corrections_name,qh_lines))) + ['\n'] + \
             ["☘️四川频道,#genre#"] + sorted(set(correct_name_data(corrections_name,sc_lines))) + ['\n'] + \
             ["☘️天津频道,#genre#"] + sorted(set(correct_name_data(corrections_name,tj_lines))) + ['\n'] + \
             ["☘️新疆频道,#genre#"] + sorted(set(correct_name_data(corrections_name,xj_lines))) + ['\n'] + \
             ["解说频道,#genre#"] + sorted(set(js_lines)) + ['\n'] + \
             ["春晚,#genre#"] + sort_data(cw_dictionary,set(cw_lines))  + ['\n'] + \
             ["直播中国,#genre#"] + sorted(set(correct_name_data(corrections_name,zb_lines))) + ['\n'] + \
             ["MTV,#genre#"] + sorted(set(correct_name_data(corrections_name,mtv_lines))) + ['\n'] + \
             ["收音机频道,#genre#"] + sort_data(radio_dictionary,set(radio_lines))  + ['\n'] + \
             ["❤️与凤行,#genre#"] + read_txt_to_array('专区/特供频道/♪与凤行.txt')  + ['\n'] + \
             ["❤️以家人之名,#genre#"] + read_txt_to_array('专区/特供频道/♪以家人之名.txt')

# # custom定制
# custom_lines_zhang =  ["更新时间,#genre#"] +[version] + ['\n'] +\
#             ["港澳台,#genre#"] + sort_data(gat_dictionary,set(correct_name_data(corrections_name,gat_lines))) + ['\n'] 



# 将合并后的文本写入文件
output_file = "merged_output.txt"
output_file_simple = "merged_output_simple.txt"
others_file = "others_output.txt"

# NEW将合并后的文本写入文件
new_output_file = "live.txt"
new_output_file_simple = "live_lite.txt"

# # custom定制
# output_file_custom_zhang = "custom/zhang.txt"

try:
    # 瘦身版
    with open(output_file_simple, 'w', encoding='utf-8') as f:
        for line in all_lines_simple:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_file_simple}")

    with open(new_output_file_simple, 'w', encoding='utf-8') as f:
        for line in all_lines_simple:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {new_output_file_simple}")

    # 全集版
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_file}")

    with open(new_output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {new_output_file}")

    # 其他
    with open(others_file, 'w', encoding='utf-8') as f:
        for line in other_lines:
            f.write(line + '\n')
    print(f"Others已保存到文件: {others_file}")

    # 定制
    # with open(output_file_custom_zhang, 'w', encoding='utf-8') as f:
    #     for line in custom_lines_zhang:
    #         f.write(line + '\n')
    # print(f"合并后的文本已保存到文件: {output_file_custom_zhang}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")

################# 添加生成m3u文件
# 报时
#print(f"time: {datetime.now().strftime("%Y%m%d_%H_%M_%S")}")

channels_logos=read_txt_to_array('assets/logo.txt') #读入logo库
def get_logo_by_channel_name(channel_name):
    
    # 遍历数组查找频道名称
    for line in channels_logos:
        # 去除首尾空白并检查是否为空行(没有这个判断logo中如果出现空行会出错)
        if not line.strip():
            continue
        name, url = line.split(',')
        if name == channel_name:
            return url
    return None

# #output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml,https://epg.112114.xyz/pp.xml.gz,https://assets.livednow.com/epg.xml"\n'
# output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n'

# with open(output_file, "r", encoding='utf-8') as file:
#     input_text = file.read()

# lines = input_text.strip().split("\n")
# group_name = ""
# for line in lines:
#     parts = line.split(",")
#     if len(parts) == 2 and "#genre#" in line:
#         group_name = parts[0]
#     elif len(parts) == 2:
#         channel_name = parts[0]
#         channel_url = parts[1]
#         logo_url=get_logo_by_channel_name(channel_name)
#         if logo_url is None:  #not found logo
#             output_text += f"#EXTINF:-1 group-title=\"{group_name}\",{channel_name}\n"
#             output_text += f"{channel_url}\n"
#         else:
#             output_text += f"#EXTINF:-1  tvg-name=\"{channel_name}\" tvg-logo=\"{logo_url}\"  group-title=\"{group_name}\",{channel_name}\n"
#             output_text += f"{channel_url}\n"

# with open("merged_output.m3u", "w", encoding='utf-8') as file:
#     file.write(output_text)

# print("merged_output.m3u文件已生成。")


def make_m3u(txt_file, m3u_file, m3u_file_copy):
    try:
        #output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml,https://epg.112114.xyz/pp.xml.gz,https://assets.livednow.com/epg.xml"\n'
        output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'

        # # 打开txt文件读取
        # with open(txt_file, 'r', encoding='utf-8') as txt:
        #     lines = txt.readlines()

        # # 创建m3u文件并写入
        # with open(m3u_file, 'w', encoding='utf-8') as m3u:
        #     # 写入m3u文件的头部信息
        #     m3u.write('#EXTM3U\n')

        #     # 写入音频文件路径
        #     for line in lines:
        #         line = line.strip()
        #         if line:  # 忽略空行
        #             m3u.write(f'{line}\n')
        with open(txt_file, "r", encoding='utf-8') as file:
            input_text = file.read()

        lines = input_text.strip().split("\n")
        group_name = ""
        for line in lines:
            parts = line.split(",")
            if len(parts) == 2 and "#genre#" in line:
                group_name = parts[0]
            elif len(parts) == 2:
                channel_name = parts[0]
                channel_url = parts[1]
                logo_url=get_logo_by_channel_name(channel_name)
                if logo_url is None:  #not found logo
                    output_text += f"#EXTINF:-1 group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
                else:
                    output_text += f"#EXTINF:-1  tvg-name=\"{channel_name}\" tvg-logo=\"{logo_url}\"  group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"

        with open(f"{m3u_file}", "w", encoding='utf-8') as file:
            file.write(output_text)
        with open(f"{m3u_file_copy}", "w", encoding='utf-8') as file:
            file.write(output_text)

        print(f"M3U文件 '{m3u_file}' 生成成功。")
        print(f"M3U文件 '{m3u_file_copy}' 生成成功。")
    except Exception as e:
        print(f"发生错误: {e}")

make_m3u(output_file, "merged_output.m3u", "live.m3u")
make_m3u(output_file_simple, "merged_output_simple.m3u", "live_lite.m3u")


# 执行结束时间
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

combined_blacklist_hj = len(combined_blacklist)
all_lines_hj = len(all_lines)
other_lines_hj = len(other_lines)
print(f"blacklist行数: {combined_blacklist_hj} ")
print(f"merged_output.txt行数: {all_lines_hj} ")
print(f"others_output.txt行数: {other_lines_hj} ")


#备用1：http://tonkiang.us
#备用2：https://www.zoomeye.hk,https://www.shodan.io,https://tv.cctv.com/live/
#备用3：(BlackList检测对象)http,rtmp,p3p,rtp（rtsp，p2p）

