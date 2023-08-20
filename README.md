# MediaWiki File Import Utility 
A utility which can easily import file from another wiki.

## Requirements

- Destination Wiki API URL (Example: https://example.com/w/api.php)
- Import Source Wiki Main URL (Example: https://example.com/wiki/)
- A list of import filename

Also, this requires ```$wgAllowCopyUploads = true;``` in the wiki's local settings and an account with the ```upload_by_url``` user right. 

## Usage

### Fetch a bot password

1. Turn to **Special:BotPasswords** on the Destination Wiki
2. Fill in your username/passwords
3. Create a new bot
4. Remember to add upload permissions
5. Save the bot passwords, it should be like ```xxx@xxx``` and a random key.

### Average User

1. Download the latest build version from [here](https://github.com/AlanYe-Dev/mediawiki-file-import-utility/actions/workflows/pyinstaller-windows.yml).
2. Duplicate ```conf.yml.example```, rename it to ```conf.yml```.
3. Fill in the Bot credentials previous fetched.
4. Optional: Prepare a list of import filename to ```import.txt```.
5. Run **main.exe**.

### Development

1. Clone this repository.
2. Duplicate ```conf.yml.example```, rename it to ```conf.yml```.
3. Fill in the Bot credentials previous fetched.
4. Optional: Prepare a list of import filename to ```import.txt```.
5. ```python3 src/main.py```

## Build
Use PyInstaller to complete the build process.
``` pyinstaller -F src/main.py```