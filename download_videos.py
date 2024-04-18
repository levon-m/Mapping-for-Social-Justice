import requests
import subprocess
import re
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, parse_qs, urljoin

#Gather all videos in article
def scrape_videos(article_url):
    try:
        response = requests.get(article_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        videos = soup.find_all('video')
        video_urls = [urljoin(article_url, video.find('source')['src']) for video in videos if video.find('source')]

        print("Found video URLs:", video_urls)

        #Find iframes possibly containing video links
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if 'youtube' in src or 'vimeo' in src:
                video_id = extract_video_id_from_url(src)
                video_urls.append(convert_video_id_to_direct_link(video_id, src))

        #Find video links in a tags and scripts
        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.search(r'\.(mp4|avi|mov)$', href):
                video_urls.append(urljoin(article_url, href))

        return video_urls
    except Exception as e:
        print("Error during scraping:", e)
        return []

#Extract video ID from URLs
def extract_video_id_from_url(url):
    parsed_url = urlparse(url)
    if 'youtube' in parsed_url.netloc:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif 'vimeo' in parsed_url.netloc:
        return parsed_url.path.split('/')[-1]
    return None

#Convert video ID to a direct video link if possible
#Placeholder function for potential future API calls
def convert_video_id_to_direct_link(video_id, src):
    if video_id is None:
        return src  #Return the original src if no ID was extracted
    if 'youtube' in src:
        return f"https://www.youtube.com/watch?v={video_id}"
    elif 'vimeo' in src:
        return f"https://vimeo.com/{video_id}"
    return src

def download_video(url, filename):
    try:
        response = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

#Apply exiftool
def extract_metadata(video_file):
    try:
        result = subprocess.run(['exiftool', video_file], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Failed to extract metadata from {video_file}: {e}")
        return ""

def main(article_url, output_excel):
    video_urls = scrape_videos(article_url)
    video_files = []
    metadata_list = []

    for idx, video_url in enumerate(video_urls):
        filename = f"video_{idx}.mp4"
        print(f"Downloading video from {video_url}...")
        download_video(video_url, filename)
        print("Extracting metadata...")
        metadata = extract_metadata(filename)
        video_files.append(filename)
        metadata_list.append(metadata)

    if video_files and metadata_list:
        df = pd.DataFrame({
            'Video File': video_files,
            'Metadata': metadata_list
        })
        df.to_excel(output_excel, index=False)
        print(f"Data written to {output_excel}")
    else:
        print("No videos were processed.")

if __name__ == "__main__":
    article_url = input("Enter the URL of the article: ")
    output_excel = "video_metadata.xlsx"
    main(article_url, output_excel)
