import requests
import mwparserfromhell

# 定义API地址和页面标题
to_wiki_url = "https://sonicpedia.org/w/api.php"
page_title = "迷失山谷"

# Fetch page source code from MediaWiki API
def get_page_content(to_wiki_url, page_title):
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "revisions",
        "rvprop": "content"
    }

    response = requests.get(to_wiki_url, params=params)
    data = response.json()
    
    # Extract page content
    page_id = list(data['query']['pages'].keys())[0]
    page = data['query']['pages'][page_id]
    content = page['revisions'][0]['*']
    
    return content

# Extract file names from MediaWiki page
def extract_file_names(text):
    file_names = []  # 用列表存储文件名
    wikicode = mwparserfromhell.parse(text)
    
    for node in wikicode.filter_wikilinks():
        if node.title.lower().startswith("file:"):
            file_name = node.title[len("file:"):].strip()
            file_names.append(file_name)
    
    return file_names

# Fetch page source code
wiki_text = get_page_content(to_wiki_url, page_title)

# Extract file names
file_names = extract_file_names(wiki_text)

# Save file names to import.txt
with open("import.txt", "w", encoding="utf-8") as output_file:
    for i, file_name in enumerate(file_names):
        if i != len(file_names) - 1:
            output_file.write(file_name + "\n")
        else:
            output_file.write(file_name)
