import pandas as pd
import os
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from multiprocessing import Pool
import re
import subprocess

def download_GenerateVideoSource_mpd(mpd_url, folder_name):
    # Function to download the MPD file containing video and audio sources
    headers = {"User-Agent": UserAgent().firefox}
    response = requests.get(mpd_url, headers=headers, stream=True)
    file_path = os.path.join(folder_name, 'GenerateVideoSource.mpd')
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f'Failed to download the {label} GenerateVideoSource.')

def analysis_GenerateVideoSource_mpd():
    # Function to analyze the downloaded MPD file to extract video and audio URLs
    with open('../data/{}/GenerateVideoSource.mpd'.format(label), 'r', encoding='utf-8') as f:
        mpd_source = f.read()
    soup = BeautifulSoup(mpd_source, 'xml')
    mpd_video_data = soup.find('AdaptationSet', {'mimeType': 'video/mp4'})
    video_init_url = re.findall(r'initialization="([^"]+)"', str(mpd_video_data))
    video_init_url = video_init_url[0].replace('&amp;', '&')
    video_media_url = re.findall(r'media="([^"]+)"', str(mpd_video_data))
    video_media_url = video_media_url[0].replace('&amp;', '&')
    mpd_audio_data = soup.find('AdaptationSet', {'mimeType': 'audio/mp4'})
    audio_init_url = re.findall(r'initialization="([^"]+)"', str(mpd_audio_data))
    audio_init_url = audio_init_url[0].replace('&amp;', '&')
    audio_media_url = re.findall(r'media="([^"]+)"', str(mpd_audio_data))
    audio_media_url = audio_media_url[0].replace('&amp;', '&')
    video_time = re.findall(r'PT(\d+)M', str(soup.find('MPD')))
    video_time = int(video_time[0])
    return video_init_url, video_media_url, audio_init_url, audio_media_url, video_time

def download_init_segment(url, folder_name):
    # Function to download initialization segment (init segment) for video and audio
    os.makedirs(folder_name, exist_ok=True)
    headers = {"User-Agent": UserAgent().firefox}
    response = requests.get(url, headers=headers, stream=True)
    file_path = os.path.join(folder_name, 'segmenti.mp4')
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f'Failed to download the {label} init segment.')

def set_segments_url(audio_url, video_url, video_time):
    # Function to set URLs for video and audio segments based on duration
    max_count = video_time * 15 + 30  # Adjusted maximum count based on video duration
    audio_segments_urls = [audio_url.replace('$Number$', f'{nn}') for nn in range(0, max_count)]
    video_segments_urls = [video_url.replace('$Number$', f'{mm}') for mm in range(0, max_count)]
    return audio_segments_urls, video_segments_urls

def download_segment(url_folder_tuple):
    # Function to download individual segments using multiprocessing
    url, folder_name, index = url_folder_tuple
    file_path = os.path.join(folder_name, f'segment{index}.mp4')
    headers = {"User-Agent": UserAgent().firefox}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)

def download_segments(urls, folder_name):
    # Function to download multiple segments concurrently using multiprocessing
    os.makedirs(folder_name, exist_ok=True)
    url_folder_tuples = [(url, folder_name, index) for index, url in enumerate(urls)]
    num_processes = 10  # Number of processes for multiprocessing
    with Pool(processes=num_processes) as pool:
        pool.map(download_segment, url_folder_tuples)

def set_new_mpd(folder_name):
    # Function to update the MPD file with new segment URLs
    folder_path = os.path.join(folder_name, 'GenerateVideoSource.mpd')
    with open(f'{folder_path}', 'r') as rfile:
        mpd_content = rfile.read()
    soup = BeautifulSoup(mpd_content, 'xml')
    v_adaptation_set_tag = soup.find('AdaptationSet', {'mimeType': 'video/mp4'})
    v_representation_tag = v_adaptation_set_tag.find('Representation')
    v_segmenttemplate_tag = v_representation_tag.find('SegmentTemplate')
    v_segmenttemplate_tag['initialization'] = 'video_segments/segmenti.mp4'
    v_segmenttemplate_tag['media'] = 'video_segments/segment$Number$.mp4'
    a_adaptation_set_tag = soup.find('AdaptationSet', {'mimeType': 'audio/mp4'})
    a_representation_tag = a_adaptation_set_tag.find('Representation')
    a_segmenttemplate_tag = a_representation_tag.find('SegmentTemplate')
    a_segmenttemplate_tag['initialization'] = 'audio_segments/segmenti.mp4'
    a_segmenttemplate_tag['media'] = 'audio_segments/segment$Number$.mp4'
    with open(f'{folder_name}/GenerateVideoSource_adjust.mpd', 'w') as wfile:
        wfile.write(soup.prettify())

def record_video(input_source, output_file):
    # Function to record video using VLC based on input source and output file
    original_dir = os.getcwd()  # Save the original working directory
    video_file = os.path.join('../data', label)
    os.chdir(video_file)  # Change to base_folder directory
    vlc_path = r'D:\VLC\vlc.exe'  # VLC installation path
    command = [
        vlc_path,
        '--intf', 'dummy',  # Use dummy interface mode
        '--no-video',  # Do not display video
        '--no-audio',  # Do not play audio
        input_source,
        '--sout', f"#file{{dst={output_file}}}",  # Output to file, no display
        'vlc://quit'  # Quit VLC after completion
    ]

    # Execute VLC command and capture output and error information
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Print output and error information for debugging
    print("Output:", result.stdout.decode())
    print("Error:", result.stderr.decode())
    os.chdir(original_dir)

if __name__ == '__main__':
    # Main execution starts here
    df = pd.read_excel('../data/SPIE_data.xlsx', header=0)  # Read data from Excel
    label_list = df.iloc[:, 0].tolist()  # Extract label list from Excel
    mpd_urls = df.iloc[:, 6].tolist()  # Extract MPD URLs from Excel
    title_list = df.iloc[:, 2].tolist()  # Extract title list from Excel

    for label_index, label in enumerate(label_list):
        folder_name = os.path.join('../data', format(label))
        os.makedirs(folder_name, exist_ok=True)
        mpd_url = mpd_urls[label_index]
        title = title_list[label_index]
        print(mpd_url)
        print(title)

        # Define folder names for audio and video segments
        folder_name_audio = os.path.join(folder_name, 'audio_segments')
        folder_name_video = os.path.join(folder_name, 'video_segments')
        mpd_input_file = 'GenerateVideoSource_adjust.mpd'
        mp4_output_file = f'{label}.mp4'

        try:
            # Download MPD file and initialize variables
            download_GenerateVideoSource_mpd(mpd_url, folder_name)
            video_init_url, video_media_url, audio_init_url, audio_media_url, video_time = analysis_GenerateVideoSource_mpd()

            # Download initialization segments for video and audio
            download_init_segment(video_init_url, folder_name_video)
            download_init_segment(audio_init_url, folder_name_audio)

            # Set URLs for audio and video segments
            audio_segments_urls, video_segments_urls = set_segments_url(audio_media_url, video_media_url, video_time)

            # Download audio and video segments
            download_segments(audio_segments_urls, folder_name_audio)
            download_segments(video_segments_urls, folder_name_video)
            download_segments(audio_segments_urls, folder_name_audio)
            download_segments(video_segments_urls, folder_name_video)

            # Update MPD file with new segment URLs
            set_new_mpd(folder_name)

        except Exception as e:
            # Handle exceptions during download or processing
            with open('video_false_label.txt', 'w') as video_false_label:
                video_false_label.write(label)

        try:
            # Record video using VLC
            record_video(mpd_input_file, mp4_output_file)

        except Exception as e:
            # Handle exceptions during video recording
            with open('video_Conversion_f_label.txt', 'w') as video_Conversion_f_label:
                video_Conversion_f_label.write(label)
