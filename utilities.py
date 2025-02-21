#!/usr/bin/env python
# coding: utf-8

# import libraries
import urllib.request
import json
import os

def download_document(file_url, source, file_id, file_name = False):
    # 2DO get pdf location folder from settings file
    pdf_folder = "pdf/"
    
    # if file name not specified, use last part of url as filename
    if not file_name:
        file_name = file_url.split('/')[-1]
        
    output_location = f"{pdf_folder}{source}/{file_id}_{file_name}"
    
    urllib.request.urlretrieve(file_url, output_location) 
    
    return output_location

def _mkdir(_dir):
    if os.path.isdir(_dir): pass
    elif os.path.isfile(_dir):
        raise OSError("%s exists as a regular file." % _dir)
    else:
        parent, directory = os.path.split(_dir)
        if parent and not os.path.isdir(parent): _mkdir(parent)
        if directory: os.mkdir(_dir)

            
def save_json(data, location):

    # make parent folder(s) if needed
    _mkdir('/'.join(location.split('/')[0:-1]))
    
    # save json
    jsonOutput = json.dumps(data)
    with open(location, "w") as json_file:
        try:
            json_file.write(jsonOutput) 
        except:
            jsonOutput = jsonOutput.encode('utf-8')
            json_file.write(jsonOutput) 