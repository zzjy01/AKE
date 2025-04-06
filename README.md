# Building a Multimodal Dataset of Academic Paper for Keyword Extraction
**This paper constructs a multimodal academic paper dataset for keyword extraction research**
## Overview
**Data and source Code for the paper: Building a Multimodal Dataset of Academic Paper for Keyword Extraction**

Current keyword extraction task typically relies solely on textual data, while neglecting information from other modalities such as image and audio. This leads to deficiencies in information richness and overlooks potential correlations, thereby constraining the model's ability to learn representations of the data and the accuracy of model predictions. Furthermore, the currently available multimodal datasets for keyword extraction task are particularly scarce, further hindering the progress of research on multimodal keyword extraction task. Therefore, this study constructs a multimodal dataset of academic paper consisting of 1000 samples (918 from SPIE and 82 from VideoLectures), with each sample containing paper text, images, audio, and keywords. However, since the VideoLectures website is currently inaccessible for retrieving multimodal academic paper data, only the SPIE-related data is displayed.
## Directory structure
<pre>
AKE                                                              Root directory
├─  Codes 
│       ├─   Web_crawler_video_generation.py                     Download academic conference videos
│       └─   VideoFrame_Extraction_Slideshow_Merge.py            Extract slides from the video and switch time nodes
└─  Data
         ├─   SPIE_data.xlsx                                     Store SPIE data information
         └─   title'\d'
                  ├─  GenerateVideoSource.mpd                    The website retrieves the mpd file of the video
                  ├─  GenerateVideoSource_adjust.mpd             Modify and adjust the mpd file
                  ├─  video_segments                             Multiple video segments
                  ├─  audio_segments                             Multiple audio segments
                  ├─  title'\d'.mp4                              A video composed of multiple segments
                  ├─  images_title'\d'                           Folder for storing slide images
                  ├─  ppt_ttitle'\d'.pdf                         PDF file of slide image synthesis
                  └─  time_title'\d'.txt                         Time nodes for switching between each slide
</pre>
## Dataset Discription

The multimodal dataset of academic paper comprises 1, 000 samples, each containing paper text, text keywords, slide images, and audio. Table 1 describes the maximum, minimum, and average lengths of each type of data. The maximum length of paper text is 9313 words, the minimum length is 1084 words, and the average length is 4051 words. The maximum number of keywords is 11, the minimum is 2, and the average number of keywords is 5.4. The number of slides refers to its' pages, with a maximum of 41 pages, a minimum of 9 pages, and an average of 23.5 pages. The complete audio time ranges from a maximum of 36min32s to a minimum of 9min12s, with an average duration of 18min17s.

- Statistics on the Length of Various Types of Data

|Data Type|Min Length|Max length|Average Length|
|-|-|-|-|
|Paper Text|1084 words|9313 words|4051 words|
|Keywords|2|11|5.4|
|Slides|9 pages|41 pages|23.5 pages|
|Audio|9min12s|36min32s|18min17s|

## Requirements

- Python==3.9
- img2pdf == 0.4.4

## Quick Start
**Implementation Steps**

The multimodal academic paper data is stored in the SPIE_data.xlsx file, which contains the following information: 
- <code>label</code> Labels for each data sample
- <code>detailed_page_url</code> Link to the original webpage details for each data sample
- <code>title</code> Title of each data sample
- <code>abstract</code> Abstract of each data sample
- <code>keywords</code> Keywords for each data sample
- <code>paper_url</code> Download link for each data sample paper
- <code>video_url</code> Download link for each data sample video
  
In the codes folder, there are two Python files: <code>Web_crawler_video_generation.py</code> and <code>VideoFrame_Extraction_Slideshow_Merge.py</code>. The former is used for downloading academic conference videos, while the latter extracts slide images from the video and stores them in the <code>data-timages_title'\d'</code> folder. It then merges these images into a single PDF file <code>(ppt_title'\d'.pdf)</code> and records the time points when each slide changes, storing this information in the <code>time_title'\d'.txt</code> file.

When you open the <code>SPIE_data.xlsx</code>, you will notice that the last column, <code>video_url</code> is empty. Due to certain reasons on the SPIE data website, you need to open the <code>detailed_page_url</code> and find the link starting with "Generation" under the "Inspect - Network" tab. Copy this link into the corresponding video_url column in <code>SPIE_data.xlsx</code>. Since the link has a certain validity period, I recommend running the crawler script after gathering a sufficient number of links. Additionally, after the crawling process is completed, it is advisable to check whether the file is complete. <code>GenerateVideoSource.mpd</code>, <code>GenerateVideoSource_adjust.mpd</code>, <code>video_segments</code>, and <code>audio_segments</code> are intermediate files generated during the execution of the code. You can also check whether they exist or not to determine if the data has been downloaded successfully.

When crawling papers and audio transcripts from the SPIE website, using a browser driver such as Selenium often encounters restrictions due to anti-scraping mechanisms. SPIE detects browser fingerprint information, such as <code>webdriver</code>, to identify automated operations and triggers a CAPTCHA verification during access. Since web scrapers cannot automatically complete this verification, further access is blocked. Therefore, the traditional browser driver approach is not feasible, and a more sophisticated method must be used to bypass these restrictions. First, it is necessary to manually log in to the SPIE website using a regular browser. Accessing the site through an institutional VPN can help complete the authentication process. Once successfully logged in, the website typically stores the user's session state in cookies or session storage. Based on this authenticated environment, the scraper can proceed with further operations without triggering another CAPTCHA verification. With the session maintained, the scraper should avoid opening new pages directly using a browser driver. Instead, Bazhuayu RPA, a web scraping tool, should be used. By leveraging Bazhuayu RPA, a new tab can be opened within the logged-in browser environment to download the paper. Since this new tab is created within an already authenticated session, SPIE continues to recognize the user as a normal visitor, thereby avoiding CAPTCHA verification. At this point, the scraper can further parse the page's HTML, extract the paper's download link, and save the file with a name based on the paper title or DOI.  For extracting audio transcripts, the process is more complex. SPIE's audio text is typically not embedded directly within the HTML but is dynamically loaded via JavaScript events. As a result, even after accessing the paper's detail page, the complete audio transcript may not be immediately available. To resolve this, an event-triggering mechanism can be utilized. For example, after opening the details page, the user can simulate manual interaction by clicking the video to enter full-screen mode, thereby triggering JavaScript to load the full transcript. Once loaded, the scraper can extract the HTML source code, parse it, and retrieve the audio text content.
## Citation
Please cite the following paper if you use this code and dataset in your work.

>Zhang, J., Yan, X., Xiang, Y., Zhang, Y., & Zhang, C. (2024). Building a Multimodal Dataset of Academic Paper for Keyword Extraction. Proceedings of the Association for Information Science and Technology, 61(1), 435-446.  [[doi]](https://doi.org/10.1002/pra2.1040)  [[Dataset & Source Code]](https://github.com/zzjy01/AKE.git) 
