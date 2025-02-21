#!/usr/bin/env python3

"""
Script to import documents from Onroerend Erfgoed to AGNES
"""

# import nltk / download punkt
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

# import other libraries
import urllib.request
import requests
import json
from pyproj import Transformer
import os
import time
import sys
import nltk
import logging
from datetime import datetime


# import common functions
sys.path.insert(1, '../')
import common

# set up transformer from Lambert72 to lat/lon
transformer = Transformer.from_crs("EPSG:31370", "EPSG:4326")

# set name of module, to fetch info from config
module_name = "onroerend_erfgoed"

# get info from config file
config = common.get_config()

# set up logging
log_location = config['data_source'][module_name]['harvest_log_location']
now = datetime.now()
date = now.strftime("%Y-%m-%d")
logfile = f"{log_location}harvest-log-{module_name}-{date}.log"
logging.basicConfig(level=logging.DEBUG, filename=logfile, filemode="a+",
                format="%(asctime)-15s %(levelname)-8s %(message)s")

# log config info        
last_indexed_id = config['data_source'][module_name]['last_indexed_id']
logging.info(f'last indexed id: {last_indexed_id}')

endpoint_url = config['data_source'][module_name]['endpoint_url']
logging.info(f'endpoint_url: {endpoint_url}')

pdf_folder = config['data_source'][module_name]['pdf_folder']
logging.info(f'pdf_folder: {pdf_folder}')

json_folder = config['data_source'][module_name]['json_folder']
logging.info(f'json_folder: {json_folder}')

html_folder = config['data_source'][module_name]['html_folder']
logging.info(f'html_folder: {html_folder}')

language = config['data_source'][module_name]['language']
logging.info(f'language: {language}')

bert_model = config['bert_models'][language]
logging.info(f'bert_model: {bert_model}')




# set headers
headers = {'Accept': 'application/json', 
           'User-Agent': 'python-requests/2.18.1',
           'From': 'a.brandsen@arch.leidenuniv.nl (EXALT)'  
          }

# set parameters
# https://loket.onroerenderfgoed.be/archeologie/rapporten/eindverslagen?sort=id&per_pagina=50&pagina=1
params = {'per_pagina': 100, # number of results per page
          'sort': 'id',
          #'pagina': 1 # page 
         }   


# Create a requests Session
session = requests.Session()

# Set the header options
session.headers.update(headers)

# Make a request and store the response
try:
    response = session.get(endpoint_url, params=params)
    response.raise_for_status()                 # Raise error in case of failure 
except requests.exceptions.HTTPError as httpErr: 
    print ("HTTP Error:",httpErr) 
except requests.exceptions.ConnectionError as connErr: 
    print ("Error Connecting:",connErr) 
except requests.exceptions.Timeout as timeOutErr: 
    print ("Timeout Error:",timeOutErr) 
except requests.exceptions.RequestException as reqErr: 
    print ("Something Else:",reqErr)
    
# get json data from request
data = response.json()

# Fetch all the other pages of results
while 'next' in response.links:
    # GET the url pointing to the next page
    response = session.get(response.links['next']['url'])
    # add the data from the next page to the data we're collecting
    data.extend(response.json())
    # Sleep for half a second, so we don't overload the server
    time.sleep(0.5)
  
#logging.info(len(data))


# go through projects
for project in data:
    
    #logging.info(json.dumps(project, indent=4))

    # if not fetched yet
    if project['id'] > last_indexed_id:

        logging.info(f"Processing id:{project['id']}")
    
        # get more details on project using uri
        response = requests.get(
            project['uri'],
            headers = {'Accept': 'application/json'}
        )
        project_detail = response.json()

        #logging.info(json.dumps(project_detail, sort_keys=True, indent=4))

        # loop through relevant documents, make document.json for each
        for doc in project_detail['bijlagen']:

            #logging.info(json.dumps(doc, sort_keys=True, indent=4))
            
            if doc['bijlagetype']['id'] == 2 and doc['bestandsnaam'][-3:].lower() == 'pdf': # is report and is pdf file
                #logging.info(project)

                file_name = doc['bestandsnaam'].replace(' ','_').replace('(','').replace(')','')

                output_document = {}
                output_document['source'] = module_name
                output_document['file_name'] = file_name
                output_document['file_type'] = 'report'
                if(doc['omschrijving']):
                    title = f"{project['onderwerp']} - {doc['omschrijving']}"
                else:
                    title = f"{project['onderwerp']}"
                output_document['title'] = title
                creators = []
                for auteur in doc['auteurs']:
                    creators.append(auteur['auteur'])
                output_document['creators'] = creators
                output_document['description'] = '' # no descriptions in this data source
                output_document['publisher'] = project['archeoloog']
                output_document['createdAt'] = project['datum_indienen'][:10]
                output_document['identifiers'] = {'uri':project['uri'],'oe_id':project['id']}
                output_document['language'] = 'Dutch'

                #coordinates
                totalX = 0
                totalY = 0
                coordinates = project_detail['archeologierapport']['locatie']['contour']['coordinates'][0][0]
                for coord in coordinates:
                    totalX += coord[0]
                    totalY += coord[1]
                coordX = totalX / len(coordinates)
                coordY = totalY / len(coordinates)
                lat, lon = transformer.transform(coordX,coordY)
                output_document['coordX'] = coordX
                output_document['coordY'] = coordY
                output_document['location'] = {'lat':lat,'lon':lon}

                #logging.info(json.dumps(output_document, indent=4))

                # set document identifier
                doc_id = f"{project['id']}_{file_name.replace('.pdf','')}"

                logging.info(f"doc_id:{doc_id}")

                # save document.json 
                json_output_folder = f"{json_folder}/{doc_id}"
                common.savejson(output_document, f"{json_output_folder}/document.json")

                logging.info(f"saved doc json")

                # download pdf
                file_url = doc['url']
                pdf_location = common.downloaddocument(file_url, project['id'], pdf_folder, file_name)

                logging.info(f"downloaded pdf")

                # process pdf, store page.json files with entities 
                common.run_ner_on_pdf(
                    pdf_location, 
                    json_output_folder, 
                    bert_model, 
                    language
                )

                logging.info(f"ran NER, saved page json")

                # process pdf, save html files
                html_output_folder = f"{html_folder}/{doc_id}"
                common.pdf2html(pdf_location, html_output_folder)

                logging.info(f"generated and saved html")

                # save last id we indexed in the settings file 
                # (do this in the loop instead of after, in case we get errors/hanging that ends the script before we get to the end)
                common.update_config(module_name, 'last_indexed_id', project['id'])
                
                logging.info(f"updated config with latest id: {project['id']}")

                
# upload json and html to webserver
common.upload2webserver(json_folder, html_folder, module_name, config['webserver']['json_folder'], config['webserver']['html_folder'])

logging.info(f"uploaded json/html to webserver")

# remotely start indexing script on webserver
common.start_index(module_name)

logging.info(f"indexing on webserver started")

logging.info(f"done!")

