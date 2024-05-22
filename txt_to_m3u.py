import sys

def convert(txt_file, m3u_file):
    with open(txt_file, 'r') as txt, open(m3u_file, 'w') as m3u:
        m3u.write("#EXTM3U\n")

        group_name = ""
        for line in txt:
            line = line.strip()
            parts = line.split(",")
            if len(parts) == 2 and "#genre#" in line:
                group_name = parts[0]
            elif len(parts) == 2:
                m3u.write(f"#EXTINF:-1 group-title=\"{group_name}\",{parts[0]}\n")
                m3u.write(f"{parts[1]}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_txt_to_m3u.py <input.txt> <output.m3u>")
        sys.exit(1)
    
    input_txt = sys.argv[1]
    output_m3u = sys.argv[2]
    convert(input_txt, output_m3u)
