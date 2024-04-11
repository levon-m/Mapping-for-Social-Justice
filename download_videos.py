import requests
import subprocess
from bs4 import BeautifulSoup
import pandas as pd

#Gather all videos in article
def scrape_videos(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    videos = soup.find_all('video')
    #Find other tags/links to identify videos
    video_urls = [video.find('source')['src'] for video in videos if video.find('source')]
    return video_urls

#Download all videos in article
def download_video(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

#Apply exiftool
def extract_metadata(video_file):
    result = subprocess.run(['exiftool', video_file], capture_output=True, text=True)
    return result.stdout

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

    #Creating a DataFrame
    df = pd.DataFrame({
        'Video File': video_files,
        'Metadata': metadata_list
    })

    #Writing to Excel
    df.to_excel(output_excel, index=False)
    print(f"Data written to {output_excel}")

if __name__ == "__main__":
    article_url = input("Enter the URL of the article: ")
    output_excel = "video_metadata.xlsx"
    main(article_url, output_excel)
