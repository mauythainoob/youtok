# YouTok
YouTok is a program which intends to completly automate the process of stealing content from Tiktok, creating compilations, and uploading it them to diffent social media platforms (this isn't supported ATM).

The intent is to minimize the human interaction when creating compilations. That's all.

## Contribution 
There is a lot more that needs to be done... Contributions are more than welcome. Here's some areas that need improving: 

1. The apis contents is a fork from a random repo... this needs tests and cleaning up. 
2. The compilation process isn't the best. This could be improved and tests be improved as well. 
3. 

## How it works
There are diffetent phases: Discovery, Download, and Compilation. Each phase is indepentant and acts upon a common query to co-ordinate between the phrases. Each phase will store it's result in Pocketbase (even the compilation phase).

#### Discovery
This phase is when we *discover* tiktok's. 

#### Download
This phase is when we download a Tiktok video. 
#### Compilation
This phase is when we create a compilation. 

**NOTE:** All videos, downloaded and created compilations, are stored locally.

## Requirements
- Python 3.8.5+ 
- FFmpeg (Must be callable on the OS's path)
- Pocketbase. 

## Setup 
1. Import the 'pb_schema.json' into Pocketbase. 
2. Create a virtual enviroments and install dependencies from requirements.txt.
3. Create a Path object against the VIDEO_DIRECTORY variable which points to the dir where all videos will be saved.
4. Run the setup_config.py script.
5. Update the example.env file... 
5. Run python -m unittest to see if things are working as expected.
