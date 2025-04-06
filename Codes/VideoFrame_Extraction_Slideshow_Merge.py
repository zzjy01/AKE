import os
import pathlib
import time
import cv2
import imutils
import shutil
import img2pdf
import glob
import pandas as pd

# Configuration constants
FRAME_RATE = 5  # Frame rate: the number of frames to process per second (lower is faster)
WARMUP = FRAME_RATE  # The initial frames to skip before starting to process
FGBG_HISTORY = FRAME_RATE * 15  # The number of frames to consider in the background model
VAR_THRESHOLD = 16  # Variance threshold to decide if a pixel is part of the background or foreground
DETECT_SHADOWS = False  # Whether to detect shadows; setting to True increases complexity
MIN_PERCENT = 0.3  # Minimum percentage difference between foreground and background to detect motion stop
MAX_PERCENT = 4  # Maximum percentage difference between foreground and background to detect ongoing motion


def get_frames(video_path):
    '''Extract frames from the video at video_path, skipping frames as per FRAME_RATE'''
    # Open video file and initialize frame dimensions
    vs = cv2.VideoCapture(video_path)
    if not vs.isOpened():
        raise Exception(f'unable to open file {video_path}')

    total_frames = vs.get(cv2.CAP_PROP_FRAME_COUNT)  # Get the total number of frames
    frame_time = 0
    frame_count = 0

    # Loop over the video frames
    while True:
        # Set the current frame's timestamp in the video
        vs.set(cv2.CAP_PROP_POS_MSEC, frame_time * 1000)  # Set position in the video (in milliseconds)
        frame_time += 1 / FRAME_RATE  # Increment time by the frame rate
        (_, frame) = vs.read()  # Read the frame

        # If no frame is read, we've reached the end of the video
        if frame is None:
            break
        frame_count += 1
        yield frame_count, frame_time, frame  # Yield the frame count, timestamp, and frame image

    vs.release()


def detect_unique_screenshots(video_path, file_name, output_folder_screenshot_path):
    '''Detect unique frames and capture them as screenshots'''
    # Prepare the output file to store frame times
    file_name_h = os.path.splitext(file_name)[0]
    file_name_h = 'time_{}.txt'.format(file_name_h)
    file_path_time = os.path.join(input_dir_name, file_name_h)

    # Initialize background subtractor for motion detection
    fgbg = cv2.createBackgroundSubtractorMOG2(history=FGBG_HISTORY, varThreshold=VAR_THRESHOLD,
                                              detectShadows=DETECT_SHADOWS)
    captured = False  # Flag to track if a screenshot has been captured
    start_time = time.time()
    (W, H) = (None, None)  # Frame dimensions
    frame_time_list = []  # List to store times of captured frames
    screenshoots_count = 0  # Counter for the number of captured screenshots

    # Loop through the frames of the video
    for frame_count, frame_time, frame in get_frames(video_path):  # Get frame count, time, and image
        orig = frame.copy()  # Clone the original frame (to save later)
        frame = imutils.resize(frame, width=600)  # Resize the frame to speed up processing
        mask = fgbg.apply(frame)  # Apply the background subtraction mask to detect motion

        # Initialize frame dimensions if not already set
        if W is None or H is None:
            (H, W) = mask.shape[:2]

        # Calculate the percentage of foreground pixels
        p_diff = (cv2.countNonZero(mask) / float(W * H)) * 100

        # If the foreground percentage is below MIN_PERCENT and motion has stopped, capture the frame
        if p_diff < MIN_PERCENT and not captured and frame_count > WARMUP:
            captured = True
            frame_time = frame_time - 2  # Adjust time to account for delay
            if frame_time < 0:
                frame_time = 0
            frame_time_list.append(round(frame_time))  # Store the frame's timestamp

            # Save the screenshot with a timestamp-based filename
            filename = f"{screenshoots_count:03}_{round(frame_time)}.png"
            path = str(pathlib.Path(output_folder_screenshot_path, filename))
            print(f"Saving {path}")
            cv2.imencode('.png', orig)[1].tofile(path)  # Save the frame as PNG (prevent encoding issues)
            screenshoots_count += 1

        # If motion is detected again, reset the captured flag
        elif captured and p_diff >= MAX_PERCENT:
            captured = False

    print(f'{screenshoots_count} screenshots Captured!')

    # Save the frame times to a text file
    with open(file_path_time, 'w') as f:
        for ti in frame_time_list:
            f.write(str(ti) + '\n')
    return


def initialize_output_folder(file_name):
    '''Initialize the output folder for screenshots (delete if exists)'''
    base_name = os.path.splitext(file_name)[0]  # Get base name without extension
    output_folder_screenshot_path = os.path.join(input_dir_name, 'images_' + base_name)  # Define output folder path

    # If the folder exists, remove it
    if os.path.exists(output_folder_screenshot_path):
        shutil.rmtree(output_folder_screenshot_path)

    # Create a new folder
    os.makedirs(output_folder_screenshot_path, exist_ok=True)

    # Set permissions to ensure it is readable and writable
    os.chmod(output_folder_screenshot_path, 0o777)
    print(f'Initialized output folder: {output_folder_screenshot_path}')
    return output_folder_screenshot_path


def convert_screenshots_to_pdf(output_folder_screenshot_path, file_name):
    '''Convert the captured screenshots to a PDF'''
    file_name = os.path.splitext(file_name)[0]  # Remove file extension
    output_pdf_path = '{}/ppt_{}'.format(input_dir_name, file_name) + '.pdf'  # Define output PDF path

    # Convert PNG images in the folder to a PDF and save it
    with open(output_pdf_path, "wb") as f:
        f.write(img2pdf.convert(sorted(glob.glob(f"{output_folder_screenshot_path}/*.png"))))  # Convert images to PDF

    print('PDF Created!')
    print(f'PDF saved at {output_pdf_path}')


if __name__ == "__main__":
    # Main execution starts here

    # Read data from Excel file
    df = pd.read_excel('../data/SPIE_data.xlsx', header=0)
    label_list = df.iloc[:, 0].tolist()  # Extract label list from Excel

    # Loop through each label to process the corresponding video
    for label_index, label in enumerate(label_list):
        input_dir_name = os.path.join('../data', str(label))  # Target folder for the video
        target_video = f"{label}.mp4"  # Video file name

        video_path = os.path.join(input_dir_name, target_video)

        # Check if the video file exists
        if os.path.exists(video_path):  # If the video exists, process it
            print(f"Processing: {target_video}")
            output_folder_screenshot_path = initialize_output_folder(target_video)  # Initialize output folder
            detect_unique_screenshots(video_path, target_video,
                                      output_folder_screenshot_path)  # Detect and capture screenshots

            # Convert captured screenshots to a PDF
            convert_screenshots_to_pdf(output_folder_screenshot_path, target_video)
        else:
            print(f"{target_video} not found, skipping.")
