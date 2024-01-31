import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import click

def download_image(url, folder_path, log_file):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            img_web_path = urlparse(url).path
            img_name = os.path.basename(img_web_path)
            filename = os.path.join(folder_path , img_name)
            path = str(filename).replace('\\\\', '\\')
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            with open(f'{log_file}', 'w') as file:
                file.write(f"Downloaded: {url}")
            print(f"Downloaded: {url}")
        else:
            with open(f'{log_file}', 'w') as file:
                file.write(f"Failed to download image[{url}].\nStatus code: {response.status_code}")
            print(f"Failed to download image[{url}].\nStatus code: {response.status_code}")
    
    except requests.exceptions.TooManyRedirects as e:
        print(f"Too many redirects for URL: {url}")
        with open(f'{log_file}', 'w') as file:
            file.write(f"Too many redirects for URL {url}: {e}")
        print(f"Too many redirects for URL {url}: {e}")

    except requests.exceptions.HTTPError as e:
        with open(f'{log_file}', 'w') as file:
            file.write(f"HTTP error occurred {url}: {e}")
        print(f"HTTP error occurred {url}: {e}")

    except requests.exceptions.RequestException as e:
        with open(f'{log_file}', 'w') as file:
            file.write(f"An error occurred {url}: {e}")
        print(f"An error occurred {url}: {e}")

def get_all_images_src(url, srcs, log_file):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            img_src_list = [img['data-src'] for img in img_tags if 'data-src' in img.attrs]
            srcs.extend(img_src_list)
        else:
            with open(log_file, 'w') as file:
                file.write(f"Url not found: {url}")
            print(f"Url not found: {url}")
    
    except requests.exceptions.TooManyRedirects as e:
        print(f"Too many redirects for URL: {url}")
        with open(f'{log_file}', 'w') as file:
            file.write(f"Too many redirects for URL {url}: {e}")
        print(f"Too many redirects for URL {url}: {e}")

    except requests.exceptions.HTTPError as e:
        with open(f'{log_file}', 'w') as file:
            file.write(f"HTTP error occurred {url}: {e}")
        print(f"HTTP error occurred {url}: {e}")

    except requests.exceptions.RequestException as e:
        with open(f'{log_file}', 'w') as file:
            file.write(f"An error occurred {url}: {e}")
        print(f"An error occurred {url}: {e}")
    
def get_all_links(url, urls, log_file, sub_urls = True):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all <a> tags
            all_a_tags = soup.find_all('a')
            # Extract and print links
            for a_tag in all_a_tags:
                href = a_tag.get('href')
                if href and not href.startswith('#'):
                    full_url = urljoin(url, href)
                    if not full_url.startswith('http'):
                        full_url = url + full_url[1:]
                    urls.add(full_url)
                    if sub_urls:
                        get_all_links(full_url, urls, log_file, sub_urls)  
        else:
            with open(f'{log_file}', 'w') as file:
                file.write(f"Failed to redirect to {url}.\nStatus code: {response.status_code}")
            print(f"Failed to redirect to {url}.\nStatus code: {response.status_code}")

    except requests.exceptions.TooManyRedirects as e:
        print(f"Too many redirects for URL: {url}")
        with open(f'{log_file}', 'w') as file:
            file.write(f"Too many redirects for URL {url}: {e}")
        print(f"Too many redirects for URL {url}: {e}")

    except requests.exceptions.HTTPError as e:
        with open(f'{log_file}', 'w') as file:
            file.write(f"HTTP error occurred {url}: {e}")
        print(f"HTTP error occurred {url}: {e}")

    except requests.exceptions.RequestException as e:
        with open(f'{log_file}', 'w') as file:
            file.write(f"An error occurred {url}: {e}")
        print(f"An error occurred {url}: {e}")    

@click.command()
@click.option('--url', default="https://unsplash.com", type=str, help='Specify a --url <url> to get the images')
@click.option('--out', default="downloaded", type=str, help='Specify a --dir <download folder path> for output data')
@click.option('--sub', default=False, type=bool, help='Specify a --sub True if you want to dig to sub directories.')
def main(url, out, sub):
    print(f"\n\nurl: {url}")
    print(f"out: {out}")
    print(f"sub: {sub}")
    download_dir = f'{out}\imgs'
    log_file_dir = f'{out}\log'

    #  If Images Download Dir Not Exists
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
            print(f"Directory '{download_dir}' didn't exist. Created.")
        except Exception as e:
            print(f"An error occurred while creating the directory {download_dir}\nError: {e}")

    #  If Logs Download Dir Not Exists
    if not os.path.exists(log_file_dir):
        try:
            os.makedirs(log_file_dir)
            print(f"Directory '{log_file_dir}' didn't exist. Created.")
        except Exception as e:
            print(f"An error occurred while creating the directory {log_file_dir}\nError: {e}")
            
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H-%M-%S")
    log_file = f'{log_file_dir}\{formatted_datetime}.txt'
    print(f"log_file: {log_file}\n\n")

    urls = set()
    srcs = []
    get_all_links(url, urls, log_file, sub_urls = sub)

    for url in urls:
        get_all_images_src(url, srcs, log_file)

    for src in srcs:
        download_image(src, download_dir, log_file)

if __name__=="__main__":
    main()
        
        
    