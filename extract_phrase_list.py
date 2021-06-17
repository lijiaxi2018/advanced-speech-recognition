import os
import sys
import atexit
import time
import json
import video_to_text as vtt
import utils as utils

def extract_phrase_list(file_name):
    """
    Args:
        file_name: an mov or mp4 file where the key words will be extracted

    Returns: a list of phrases that are extracted from the input video file. These are the extracted keywords

    """

    # cut the lecture videos into different scenes
    scenes = vtt.find_scenes(file_name, min_scene_length=1, abs_min=0.75, abs_max=0.98, find_subscenes=True,
                                     max_subscenes_per_minute=12)

    # for each scene, get its dictionary
    scene_text_dict, transcations = vtt.scene_to_text(scenes)
    frequent_patterns = utils.sequential_pattern_mining(transcations, 2)
    print(scene_text_dict)
    print("Raw Dictionary ==================================================================================")

    # combine the multiple dictionary into one
    phraseDict = utils.convert_dict_to_phraseDict(scene_text_dict)
    print(phraseDict)
    print("Combined raw dictionary ==================================================================================")

    # clean up the each dictionary by removing non-letters and non-numbers
    phraseDict = utils.process_phraseDict(phraseDict)
    print(phraseDict)
    print("cleaned dictionaries ==================================================================================")

    # process the dictionary by comparing frequency with the brown corpus
    phraseList = utils.process_by_frequency(phraseDict)
    print(phraseList)
    print("initial phrase list ==================================================================================")

    # process the phrase list by removing stop words
    phraseList = utils.remove_stop_words(phraseList)
    print(phraseList)
    print("Final list after removing stop words ====================================================================")
    print()

    # extract frequent patterns and put them into a list
    print(frequent_patterns)
    print("frequent patterns ===============================================================================")
    print()
    frequent_patterns_list = utils.patterns_to_list(frequent_patterns)

    # combine the frequent patterns with single phrase list into one list
    phraseList = phraseList + frequent_patterns_list
    print(phraseList)
    print("Final phrase list ===============================================================================")
    print()

    return phraseList

