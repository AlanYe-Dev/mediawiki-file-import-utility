"""
    MediaWiki Import File Utility
    Author: _Wr_
    Version: 0.4.6

    Foundations:
     - MediaWiki API Demos (MIT license)
"""
import sys

import requests
import os
import yaml
import mwparserfromhell
from urllib.parse import urlparse, parse_qs


def extract_filename(url_or_text):
    # Try to parse URL
    parsed_url = urlparse(url_or_text)

    # Query wiki_filename from URL query parameters
    if 'wpDestFile' in parse_qs(parsed_url.query):
        wiki_filename = parse_qs(parsed_url.query)['wpDestFile'][0]
    else:
        # Extract wiki_filename from URL path
        path_parts = parsed_url.path.split('/')
        for part in reversed(path_parts):
            if part:
                # Remove "File:" prefix if present
                if part.startswith("File:"):
                    wiki_filename = part[5:]
                else:
                    wiki_filename = part
                break
        else:
            # Return None if wiki_filename cannot be extracted
            return None

    # Replace space with underscore
    wiki_filename = wiki_filename.replace(" ", "_")

    return wiki_filename


# Fetch page source code from MediaWiki API
def get_page_content(destination_wiki_url, wiki_page_title):
    params = {
        "action": "query",
        "format": "json",
        "titles": wiki_page_title,
        "prop": "revisions",
        "rvprop": "content"
    }

    response = requests.get(destination_wiki_url, params=params)
    data = response.json()

    # Extract page content
    page_id = list(data['query']['pages'].keys())[0]
    page = data['query']['pages'][page_id]
    content = page['revisions'][0]['*']

    return content


def extract_file_names(text):
    wiki_filename_list = []  # 用列表存储文件名
    wikicode = mwparserfromhell.parse(text)

    for node in wikicode.filter_wikilinks():
        if node.title.lower().startswith("file:"):
            wiki_filename_process = node.title[len("file:"):].strip()
            wiki_filename_list.append(wiki_filename_process)

    return wiki_filename_list


# Startup message
print(
    "MediaWiki Import File Utility\nVersion: 0.4.6\n"
    "https://github.com/AlanYe-Dev/mediawiki-file-import-utility\n")

# Read config file
# conf = yaml.load(open('./conf.yml'))
conf_filename = 'conf.yml'
eg_conf_filename = 'conf.yml.exmaple'
eg_conf_content = """\
# Please enter the credentials from Special:BotPasswords
# DO NOT share this file for security reasons.
# For more information, see https://github.com/AlanYe-Dev/mediawiki-file-import-utility#readme
bot:
    username: 
    password: 
"""

# Check if config file exists
if os.path.isfile(conf_filename):
    print(f"[INFO] Detected config file '{conf_filename}'.")
    with open('conf.yml', 'r') as config_file:
        conf = yaml.safe_load(config_file)
else:
    print(f"[WARNING] Did not detect config file '{conf_filename}'.")
    print("[WARNING] Please rename 'conf.yml.example' to 'conf.yml' and fill in the required fields.")
    print("[WARNING] For more information, see https://github.com/AlanYe-Dev/mediawiki-file-import-utility#readme")
    if not os.path.isfile(eg_conf_filename):
        with open(eg_conf_filename, "w") as file:
            file.write(eg_conf_content)
        input("Press Enter to exit...")
        exit()
    else:
        input("Press Enter to exit...")
        exit()

lgname = conf['bot']['username']
lgpassword = conf['bot']['password']

if "op://" in lgpassword or "op://" in lgname:
    print("[INFO] Detected 1Password credentials. Attempting to retrieve...")
    import subprocess

    if "op://" in lgpassword and "op://" in lgname:
        op_credentials = subprocess.check_output(f"op read {lgname} && op read {lgpassword}", shell=True, text=True)
        lgname = op_credentials.split('\n')[0]
        lgpassword = op_credentials.split('\n')[1]

    if "op://" in lgpassword and "op://" not in lgname:
        lgpassword = subprocess.check_output(f"op read {lgpassword}", shell=True, text=True)

    if "op://" in lgname and "op://" not in lgpassword:
        lgname = subprocess.check_output(f"op read {lgname}", shell=True, text=True)

    if "[ERROR]" in lgname or "[ERROR]" in lgpassword:
        print(
            "[ERROR] 1Password credentials retrieval failed. Please check your secret reference URI (op://) and try "
            "again.")
        input("Press Enter to exit...")
        exit()
    else:
        print("[INFO] 1Password credentials retrieved.")

print(f"[INFO] Logged in as: {lgname}")

# For debug purposes
# print(lgname, lgpassword)

to_wiki_url = input(
    "[INPUT] Please enter the API URL of the Wiki you want to upload to (default: https://sonicpedia.org/w/api.php): "
    "\n>")
if to_wiki_url == '':
    to_wiki_url = 'https://sonicpedia.org/w/api.php'

S = requests.Session()
URL = to_wiki_url
print(f"[INFO] Destination Wiki API URL: {URL}")
init_step = 1
print(f"[INFO] Init Step {init_step}: Retrieving login token...")

# Step 1: Retrieve a login token
PARAMS_1 = {
    "action": "query",
    "meta": "tokens",
    "type": "login",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_1)
DATA = R.json()
LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]
print(f"[INFO] Init Step {init_step}: Login token retrieved.")

# Step 2: Send a post request to login.
init_step = init_step + 1
print(f"[INFO] Init Step {init_step}: Requesting for login...")

PARAMS_2 = {
    'action': "login",
    'lgname': lgname,
    'lgpassword': lgpassword,
    'lgtoken': LOGIN_TOKEN,
    'format': "json"
}

R = S.post(URL, data=PARAMS_2)
DATA = R.json()

if "error" in DATA:
    print(f"[ERROR] Init Step {init_step}: Login failed.")
    print(f"[ERROR] Init Step {init_step}: {DATA['error']['code']}: {DATA['error']['info']}")
    input("Press Enter to exit...")
    exit()
else:
    print(f"[INFO] Init Step {init_step}: Login request completed.")

# Step 3: While logged in, retrieve a CSRF token
init_step = init_step + 1
print(f"[INFO] Init Step {init_step}: Retrieving CSRF token...")

PARAMS_3 = {
    "action": "query",
    "meta": "tokens",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_3)
DATA = R.json()
CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]
print(f"[INFO] Init Step {init_step}: CSRF token retrieved.")
print("[INFO] Init Process completed")

# upload_file_name_list = ['Please_dont_turn_into_Tropical_Jungle.jpg']
# from_wiki_url = 'https://sonic.fandom.com/wiki/Special:FilePath/'

from_wiki_url = input(
    "[INPUT] Please enter the URL of the Wiki you want to import from (default: https://sonic.fandom.com/wiki/): \n>")
if from_wiki_url == '':
    from_wiki_url = 'https://sonic.fandom.com/wiki/'
print(f"[INFO] Source Wiki URL: {from_wiki_url}")
from_wiki_url = f'{from_wiki_url}Special:FilePath/'
upload_file_name_list = []
add_upload_filename = True
count = 0

print(
    "[INFO] This tool can automatically extract the filename from strings, so all you need to do is to copy and paste "
    "the URL or the text into the input box or save it to a text file.")
method = input(
    "[INPUT] Please enter the method you want to use to import files (default: 1)\n1. Import from dialog\n2. Import "
    "from text file\n3. Import from an existing wiki page (example: Main_page)\n>")
if method == '':
    method = 1
else:
    method = int(method)

if method == 1:
    while add_upload_filename:
        count = count + 1
        add_upload_file = input(f"[INPUT] Please enter the filename you want to upload ({count}): \n>")

        if add_upload_file == '' and count == 1:
            print("You must enter at least one filename!")
            count = 0
            add_upload_filename = True
        if add_upload_file == '' and count != 1:
            add_upload_filename = False
            count = count - 1
            print("[INFO] Collected all filenames.")
        else:
            filename = extract_filename(add_upload_file)
            upload_file_name_list.append(filename)

if method == 2:
    file_name = input(
        "[INPUT] Please enter the filename of the text file you want to import from (default: import.txt): \n>")
    if file_name == '':
        file_name = 'import.txt'
    with open(file_name, 'r') as f:
        for line in f:
            count = count + 1
            filename = extract_filename(line)
            upload_file_name_list.append(filename)
    print(f"[INFO] Collected all filenames from {file_name}.")

if method == 3:
    wiki_page_input = True
    wiki_page_count = 0
    wiki_page_titles = []  # Store user input page titles
    upload_file_name_list = []  # Store file names

    while wiki_page_input:
        wiki_page_count = wiki_page_count + 1
        page_title = input(
            f"[INPUT] Please enter the title of the wiki page you want to import from ({wiki_page_count}):\n>")
        if page_title == '' and wiki_page_count == 1:
            # Show error and let the user input again
            print("[ERROR] You must enter at least one page title!")
            wiki_page_count = 0
            wiki_page_input = True

        if page_title == '' and wiki_page_count != 1:
            # Finish input
            wiki_page_input = False
            wiki_page_count = wiki_page_count - 1
            print("[INFO] Collected all titles of wiki pages.")
        else:
            wiki_page_titles.append(page_title)
            wiki_page_input = True

    # Iterate through user-inputted page titles and extract file names
    for page_title in wiki_page_titles:
        # Get page source code
        wiki_text = get_page_content(to_wiki_url, page_title)
        # Extract file names from the source code
        file_names = extract_file_names(wiki_text)
        # Replace spaces with underscores in file names and add them to upload_file_name_list
        for filename in file_names:
            filename_with_underscore = filename.replace(" ", "_")
            upload_file_name_list.append(filename_with_underscore)

    # Save the count of extracted file names
    count = len(upload_file_name_list)

print("[INFO] Start uploading...")
upload_count = 0
success_count = 0
failed_count = 0

for title in upload_file_name_list:
    upload_count = upload_count + 1
    PARAMS_4 = {
        "action": "upload",
        "filename": title,
        "url": f"{from_wiki_url}{title}",
        "format": "json",
        "token": CSRF_TOKEN,
        "ignorewarnings": 1
    }

    R = S.post(URL, data=PARAMS_4)
    DATA = R.json()

    if "error" in DATA:
        print(f"[ERROR] Upload process ({upload_count}/{count}): {title} failed")
        print(f"[ERROR] {DATA['error']['code']}: {DATA['error']['info']}")
        failed_count = failed_count + 1
    else:
        print(f"[INFO] Upload process ({upload_count}/{count}): {title} completed", end="\r")
        success_count = success_count + 1

if count == 1:
    print(f"\n[INFO] Process completed ({upload_count}/{count}): Completed: {success_count}, Failed: {failed_count}")
else:
    print(f"[INFO] Process completed ({upload_count}/{count}): Completed: {success_count}, Failed: {failed_count}")

if input("[INPUT] Do you want to repeat the process? (y/n)\n>") == 'y':
    os.execl(sys.executable, f'"{sys.executable}"', *sys.argv)
else:
    input("Press Enter to exit...")
    exit()