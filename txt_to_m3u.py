import sys

def convert(txt_file, m3u_file):
    with open(txt_file, 'r') as txt, open(m3u_file, 'w') as m3u:
        m3u.write("#EXTM3U\n")
        for line in txt:
            line = line.strip()
            if line:
                m3u.write(f"#EXTINF:-1,{line}\n")
                m3u.write(f"{line}\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_txt_to_m3u.py <input.txt> <output.m3u>")
        sys.exit(1)
    
    input_txt = sys.argv[1]
    output_m3u = sys.argv[2]
    convert(input_txt, output_m3u)
