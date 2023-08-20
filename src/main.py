"""
    MediaWiki Import File Utility
    Author: _Wr_

    Foundations:
     - MediaWiki API Demos (MIT license)
"""

import requests
import os
import yaml
from urllib.parse import urlparse, parse_qs

"""
DEFINE FUNCTIONS
"""
def extract_filename(url_or_text):
    # Try to parse URL
    parsed_url = urlparse(url_or_text)
    
    # Query filename from URL query parameters
    if 'wpDestFile' in parse_qs(parsed_url.query):
        filename = parse_qs(parsed_url.query)['wpDestFile'][0]
    else:
        # Extract filename from URL path
        path_parts = parsed_url.path.split('/')
        for part in reversed(path_parts):
            if part:
                # Remove "File:" prefix if present
                if part.startswith("File:"):
                    filename = part[5:]
                else:
                    filename = part
                break
        else:
            # Return None if filename cannot be extracted
            return None
    
    # Replace space with underscore
    filename = filename.replace(" ", "_")
    
    return filename

# Startup message
print ("MediaWiki Import File Utility (by _Wr_)\nVersion: 0.2\n")

# Read config file
#conf = yaml.load(open('./conf.yml'))
file_name = 'conf.yml'

# Check if config file exists
if os.path.isfile(file_name):
    print(f"[INFO] Detected config file '{file_name}'.")
    with open('conf.yml', 'r') as config_file:
        conf = yaml.safe_load(config_file)
else:
    print(f"[ERROR] Did not detect config file '{file_name}'.\nPlease rename 'conf.yml.example' to 'conf.yml' and fill in the required fields.")
    input ("Press Enter to exit...")
    exit()



lgname = conf['bot']['username']
lgpassword = conf['bot']['password']

to_wiki_url = input ("[INPUT] Please enter the API URL of the Wiki you want to upload to (default: https://sonicpedia.org/w/api.php): \n>")
if to_wiki_url == '':
    to_wiki_url = 'https://sonicpedia.org/w/api.php'

S = requests.Session()
URL = to_wiki_url
print (f"[INFO] Destination Wiki API URL: {URL}")
init_step = 1
print (f"[INFO] Init Step {init_step}: Retrieving login token...")
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
print (f"[INFO] Init Step {init_step}: Login token retrieved.")
# Step 2: Send a post request to login. Use of main account for login is not
# supported. Obtain credentials via Special:BotPasswords
# (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword

init_step = init_step + 1
print (f"[INFO] Init Step {init_step}: Requesting for login...")

PARAMS_2 = {
    'action':"login",
    'lgname':lgname,
    'lgpassword':lgpassword,
    'lgtoken':LOGIN_TOKEN,
    'format':"json"
}

R = S.post(URL, data=PARAMS_2)
DATA = R.json()

if "error" in DATA:
    print (f"[ERROR] Init Step {init_step}: Login failed.")
    print (f"[ERROR] Init Step {init_step}: {DATA['error']['code']}: {DATA['error']['info']}")
    input ("Press Enter to exit...")
    exit()
else:
    print (f"[INFO] Init Step {init_step}: Login request completed.")
# Step 3: While logged in, retrieve a CSRF token

init_step = init_step + 1
print (f"[INFO] Init Step {init_step}: Retrieving CSRF token...")

PARAMS_3 = {
    "action": "query",
    "meta":"tokens",
    "format":"json"
}

R = S.get(url=URL, params=PARAMS_3)
DATA = R.json()

CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]
print (f"[INFO] Init Step {init_step}: CSRF token retrieved.")
print (f"[INFO] Init Process completed")
''' !!!!!!!!!!!!!! '''

#upload_file_name_list = ['Please_dont_turn_into_Tropical_Jungle.jpg']
#from_wiki_url = 'https://sonic.fandom.com/wiki/Special:FilePath/'


from_wiki_url = input ("[INPUT] Please enter the URL of the Wiki you want to import from (default: https://sonic.fandom.com/wiki/): \n>")
if from_wiki_url == '':
    from_wiki_url = 'https://sonic.fandom.com/wiki/'
print (f"[INFO] Source Wiki URL: {from_wiki_url}")
from_wiki_url = f'{from_wiki_url}Special:FilePath/'
upload_file_name_list = []
add_upload_filename = True
count = 0

print ("[INFO] This tool can automatically extract the filename from strings, so all you need to do is to copy and paste the URL or the text into the input box or save it to a text file.")
method = input ("[INPUT] Please enter the method you want to use to import files (default: 1)\n1. Import from dialog\n2. Import from text file\n>")
if method == '':
    method = 1
else:
    method = int(method)

if method == 1:
    while add_upload_filename == True:
        count = count + 1
        add_upload_file = input (f"[INPUT] Please enter the filename you want to upload ({count}): \n>")

        if add_upload_file == '' and count == 1:
            print ("You must enter at least one filename!")
            count = 0
            add_upload_filename = True
        if add_upload_file == '' and count != 1:
            add_upload_filename = False
            count = count - 1
            print ("[INFO] Collected all filenames.")
        else:
            filename = extract_filename(add_upload_file)
            upload_file_name_list.append (filename)
if method == 2:
    file_name = input ("[INPUT] Please enter the filename of the text file you want to import from (default: import.txt): \n>")
    if file_name == '':
        file_name = 'import.txt'
    with open (file_name, 'r') as f:
        for line in f:
            count = count + 1
            filename = extract_filename(line)
            upload_file_name_list.append (filename)
    print (f"[INFO] Collected all filenames from {file_name}.")

print ("[INFO] Start uploading...")
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
    #print(DATA)
    if "error" in DATA:
        print (f"[ERROR] Upload process ({upload_count}/{count}): {title} failed")
        print (f"[ERROR] {DATA['error']['code']}: {DATA['error']['info']}")
        failed_count = failed_count + 1
    else:
        print (f"[INFO] Upload process ({upload_count}/{count}): {title} completed")
        success_count = success_count + 1

print (f"[INFO] Process completed ({upload_count}/{count}): Successed: {success_count}, Failed: {failed_count}")
input ("Press Enter to exit...")