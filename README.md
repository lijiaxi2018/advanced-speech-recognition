# Technical Keywords Extractions from Lecture Videos

## Introduction
This repo includes a program that takes a lecture video as an input, and 
outputs the technical key words that appear in the lecture video. These keywords can be used to provide 
useful hints to the speech recognition of that video lecture. Note that this program is specifically 
designed for the speech-to-text recognition system in ClassTranscribe, an educational delivery 
platform that allows instructors to post lecture videos. However, this program can also be used 
in the general purpose of extracting technical keywords from lecture videos. 

## Contributors
This project is jointly completed by Jiaxi Li, Akhil Vyas, Ninghan Zhong, and Tianhui Cai. 

## References
To text the quality of the extracted keywords from lecture videos, we run the Microsoft Azure 
Speech-to-Text recognition system on the input lectures videos and check how recognition accuracy 
is changed with/without the extracted keywords from out program. 
