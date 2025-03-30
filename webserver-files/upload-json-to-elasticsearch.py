#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Script used to upload document/page JSON to an elasticsearch index"""

import os
import json
import requests
import sys
import shutil
from email.mime.text import MIMEText
import smtplib

# SETTINGS
jsonMainFolder = '/home/alexbrandsen/json_to_be_imported/'
esIndex = 'agnesv2-nested'

# set json folder for this source
jsonFolder = f"{jsonMainFolder}{source}"

# get source from command line
source = sys.argv[1]

print(f"Starting index for JSON from source: {source}")

#check source
allowed_sources = ['dans','archis','onroerend_erfgoed','onroerend_erfgoed_notas','kb']
if source not in allowed_sources:
    print(f"Source '{source}' not in allowed source list, exiting")
    exit()


emptyFiles = 0
failedFiles = 0
failedPages = 0
total = 0

for directory, subdirectories, files in os.walk(jsonFolder):
    if directory is not jsonFolder:
        print('indexing '+directory)
        
        try:
        
            docID = directory.split('/').pop().replace('.','') # no dots allowed in ES doc IDs
            #print('docID: '+docID)
            
            if os.path.exists(directory+'/document.json'):
                
                with open(directory+'/document.json') as f:
                    doc = f.read() 
                
                docDict = json.loads(doc)
                docDict = {'document':docDict}
                docDict['document']['pages'] = []
                      
                for file in files:
                    if file != 'document.json':
                        #print(file)
                        
                        
                        with open(directory+'/'+file) as f:
                            page = f.read()
                        
                        # below only needed for json with problems
                        """
                        # replace linendings with spaces, otherwise json invalid    
                        page = page.replace('\n',' ')
                        
                        # fix unescaped quotes in 'content' field
                        page_parts = page.split('"content":"')
                        if 'ner_entities' in page_parts[1]:
                            content_entities = page_parts[1].split('", "ner_entities"')
                            content = content_entities[0]
                            entities = content_entities[1]
                            #content = content.replace('"','\"').replace('\\','\\\\')
                            content = json.dumps(content) # escape invalid chars
                            page = f'{page_parts[0]}"content":{content}, "ner_entities"{entities}'
                        else:
                            content = page_parts[1][:-2]
                            #content = content.replace('"','\"').replace('\\','\\\\')
                            content = json.dumps(content) # escape invalid chars
                            page = f'{page_parts[0]}"content":{content}{page_parts[1][-1:]}'
                        """    
                        #print(content)
                        #print(page)
                        

                        # remove non utf-8 chars
                        #page.encode('utf-8',errors='ignore').decode('utf-8')

                        try:
                            pageDict = json.loads(page, strict=False)
                            docDict['document']['pages'].append(pageDict)
                        except Exception as e:
                            failedPages += 1
                        
                        #print(pageDict)
                        #print(page) 
                        #url = 'http://localhost:9200/'+esIndex+'/page/'+docID+'-page'+pageDict['page_number']+'?pretty&parent='+docID
                        #r = requests.post(url, data=page, headers=headers)
                        #rDict = json.loads(r.text)
                        #print(rDict)
                        

                
                #print(docDict)
                
                doc = json.dumps(docDict)
                url = 'http://localhost:9200/'+esIndex+'/_doc/'+docID+'?pretty'
                headers = {'content-type': 'application/json'}
                r = requests.post(url, data=doc, headers=headers)
                #rDict = json.loads(r.text)
                #print(rDict)
                
                # move json to 'done' folder
                shutil.move(directory, directory.replace('json_to_be_imported','json_has_been_imported'))
                
                total += 1
                
                #exit() 
                         
            else:
                print(directory+'/document.json does not exist, assuming empty file, skipping')
                emptyFiles += 1
               
        except Exception as e:
            print('error for: '+directory+', '+file)
            print(e)
            #print(page)
            failedFiles += 1

 
print(f"done! \n Total skipped (empty) files: {emptyFiles}\n Total failed files: {failedFiles}\n Total failed pages: {failedPages}")

