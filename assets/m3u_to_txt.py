import urllib.request
import opencc #简繁转换

#简繁转换
def traditional_to_simplified(text: str) -> str:
    # 初始化转换器，"t2s" 表示从繁体转为简体
    converter = opencc.OpenCC('t2s')
    simplified_text = converter.convert(text)
    return simplified_text

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
            channel_name = traditional_to_simplified(channel_name)
            
        # 处理 URL 行
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p") :
            print(f"{channel_name},{line.strip()}")
            txt_lines.append(f"{channel_name},{line.strip()}")
        
    
    # 将结果合并成一个字符串，以换行符分隔
    return '\n'.join(txt_lines)

url="https://tvv.wqwqwq.sbs/iptv.m3u"
# 创建一个请求对象并添加自定义header
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

# 打开URL并读取内容
with urllib.request.urlopen(req) as response:
    # 以二进制方式读取数据
    data = response.read()
    # 将二进制数据解码为字符串
    text = data.decode('utf-8')

    text=convert_m3u_to_txt(text)