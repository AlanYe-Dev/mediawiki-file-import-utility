from urllib.parse import urlparse, parse_qs

def extract_filename(url_or_text):
    # Try to extract a filename from a URL or text
    parsed_url = urlparse(url_or_text)
    
    # Query string may contain the filename
    if 'wpDestFile' in parse_qs(parsed_url.query):
        filename = parse_qs(parsed_url.query)['wpDestFile'][0]
    else:
        # Try to extract the filename from the path
        path_parts = parsed_url.path.split('/')
        for part in reversed(path_parts):
            if part:
                # Delete File: prefix if present
                if part.startswith("File:"):
                    filename = part[5:]
                else:
                    filename = part
                break
        else:
            # Return None if no filename found
            return None
    
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    
    return filename

# Test Exampls
'''
messages = [
    "https://sonicpedia.org/w/index.php?title=Special:%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6&wpDestFile=Super_Sonic_Lost_World-0.png",
    "File:SLW_Game_Over.png",
    "https://sonicpedia.org/wiki/File:Sonic-Lost-World-Artwork.jpg",
    "Sonic-Lost-World-Artwork.jpg"
]

for msg in messages:
    filename = extract_filename(msg)
    if filename:
        print(f"Extracted filename: {filename}")
    else:
        print("No filename found")
'''
'''
input = input ("Please enter a string and I'll try to extract the filename from it: ")
filename = extract_filename(input)
if filename:
    print(f"Extracted filename: {filename}")
else:
    print("No filename found")
'''

with open('import.txt', 'r') as f:
    lines = f.readlines()

list = []
for line in lines:
    list.append(line.strip())

for filename in list:
    filename = extract_filename(filename)
    if filename:
        print(filename)
    else:
        print("No filename found")