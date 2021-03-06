import os
from cv2 import cv2
import json
import numpy as np
from skimage.metrics import structural_similarity as ssim
from datetime import datetime

from PIL import Image
import pytesseract
import re 
import collections

import utils as utils

def find_scenes(video_path, min_scene_length=1, abs_min=0.75, abs_max=0.98, find_subscenes=True, max_subscenes_per_minute=12):
    """
    Detects scenes within a video. 
    
    Calculates the structual similarity index measure (SSIM) between each subsequent frame then uses
    the list of SSIMs to identify where scene changes are. 
    
    Parameters:
    video_path (string): Path of the video to be used.
    min_scene_length (int): Minimum scene length in seconds. Default 1s
    abs_min (float): Minimum SSIM value for non-scene changes, i.e. any frame with SSIM < abs_min 
        is defined as a scene change. Default 0.7
    abs_max (float): Maximum SSIM value for scene_changes, i.e. any frame with SSIM > abs_max
        is defined as NOT a scene change. Default 0.98
    find_subscenes (boolean): Find subscenes or not. Default True
    max_subscenes_per_minute (int): Maximum number of subscenes per minute within a scene. If number
        of subscenes found exceeds max_subscenes_per_minute, then none of those subscenes are returned.
        Rational is that too many detected subscenes is more likely a result of a video clip or other
        noisy media and not actual scene changes. 
    
    Returns:
    string: List of dictionaries dumped to a JSON string. Each dict corresponds to a scene/subscene,
        with the key/item pairs being starting timestamp (start), array representation of a image (frame_data), ending 
        timestamp (end), and boolean indicating if it's a scene or subscene (is_subscene).
    """
    
    try:
        file_name = video_path[video_path.rfind('/')+1 : video_path.find('.')]
        directory = os.path.join(os.getcwd(), file_name)
        #if not os.path.exists(directory):
        #    os.mkdir(directory)
         
        # Get the video capture and number of frames and fps
        cap = cv2.VideoCapture(video_path)
        cap.get(cv2.CAP_PROP_FPS)
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # Mininum number of frames per scene
        min_frames = min_scene_length*fps
        # Stores the last frame read
        last_frame = 0
        # List of similarities (SSIMs) between frames
        similarities = np.zeros(num_frames)
        timestamps = np.zeros(num_frames)
        
        for i in range(num_frames):
            # Read the next frame, resizing and converting to grayscale

            ret, frame = cap.read()
            if (ret == False):
                break

            # Save the time stamp of each frame 
            timestamps[i] = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            
            curr_frame = cv2.cvtColor(cv2.resize(frame, (320,240)), cv2.COLOR_BGR2GRAY)

            # Calculate the SSIM between the current frame and last frame

            if i >= 1:
                similarities[i] = ssim(last_frame, curr_frame)
                
            # Save the current frame for the next iteration
            last_frame = curr_frame
            

        # Find cuts by finding where SSIM < abs_min
        cuts = np.argwhere(similarities < abs_min).flatten()

        # Get real scene cuts by filtering out those that happen within min_frames of the last cut
        scene_cuts = [cuts[0]]
        for i in range(1, len(cuts)):
            if cuts[i] >= cuts[i-1] + min_frames:
                scene_cuts += [cuts[i]]
        scene_cuts += [num_frames-1]

        # Initialize list of scenes
        scenes = []

        # Iterate through the scene cuts
        for i in range(1, len(scene_cuts)):
            if not find_subscenes:
                continue

            scenes += [{'start': scene_cuts[i-1], 
                #'img_file': img_file, 
                'end': scene_cuts[i], 
                'is_subscene': False,
                'frame_data': []
                }]    
            
            
        # Write the image file for each scene and convert start/end to timestamp
        for i, scene in enumerate(scenes):
            cap.set(1, (scene['start'] + scene['end']) // 2)
            res, frame = cap.read()
            if (res == False):
                break
            #img_file = os.path.join(os.getcwd(), file_name, "%d.jpg"%i)
            #cv2.imwrite(img_file, frame)
            # we dont want microsecond accuracy; the [:12] cuts off the last 3 unwanted digits
            scene['start'] = datetime.utcfromtimestamp(timestamps[scene['start']]).strftime("%H:%M:%S.%f")[:12]
            scene['end'] = datetime.utcfromtimestamp(timestamps[scene['end'] ]).strftime("%H:%M:%S.%f")[:12]            
            #scene['img_file'] = img_file
            scene['frame_data'] = frame
            
        
        return scenes
    
    except Exception as e:
        print("findScene() throwing Exception:" + str(e))
        raise e


def scene_to_text(scenes):
    """
    Detects text and return as a bag of word representation from a scene 
    
    """
    scene_text_dict = []
    scene_text_list = []
    for i, scene in enumerate(scenes):
        if len(scene['frame_data']) == 0:
            break
        scene_image = Image.fromarray(scene['frame_data'])
        str_text = pytesseract.image_to_string(scene_image)
        #list_text = list(filter(('').__ne__, re.split(" |\n|, ???. |:|.\n|\x0c", str_text)))
        list_text = list(filter(('').__ne__, re.split(" |\n", str_text)))
        bag_of_word = collections.Counter(list_text)
        scene_text_dict.append(
            {'start': scene['start'], 
             'end': scene['end'], 
             'bag_of_word': dict(bag_of_word)
            })
        scene_text_list.append(list_text)
    return scene_text_dict, scene_text_list