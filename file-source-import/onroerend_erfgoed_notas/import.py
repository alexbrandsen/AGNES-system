#!/usr/bin/env python
# coding: utf-8


# import libraries
import urllib.request
import requests
import json
from pyproj import Transformer
import os
import time
import yaml

# get config
config = yaml.safe_load(open("config.yml"))

# set up transformer from Lambert72 to lat/lon
transformer = Transformer.from_crs("EPSG:31370", "EPSG:4326")


# get last id from file
last_indexed_id = config['data_source']['oe_vlaanderen']['last_indexed_id']

# endpoint url
url = config['data_source']['oe_vlaanderen']['endpoint_url']

# set headers
headers = {'Accept': 'application/json', 
           'User-Agent': 'python-requests/2.18.1',
           'From': 'm.wansleeben@arch.leidenuniv.nl (EXALT)'  
          }

# set parameters
# https://loket.onroerenderfgoed.be/archeologie/rapporten/eindverslagen?sort=id&per_pagina=50&pagina=1
params = {'per_pagina': 50, # number of results per page
          'sort': 'id',
          #'pagina': 1 # page 
         }   


def get_new_files():
    # Create a requests Session
    session = requests.Session()

    # Set the header options
    session.headers.update(headers)

    # Make a request and store the response
    try:
        response = session.get(url, params=params)
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
        
    #print(len(data))


    # go through projects
    for project in data:
        #print(json.dumps(project, indent=4))

        # if not fetched yet
        if project['id'] > last_indexed_id:
        
            # get more details on project using uri
            response = requests.get(
                project['uri'],
                headers = {'Accept': 'application/json'}
            )
            project_detail = response.json()

            print(json.dumps(project, sort_keys=True, indent=4))

            # loop through relevant documents, make document.json for each
            for doc in project_detail['bijlagen']:

                #print(json.dumps(doc, sort_keys=True, indent=4))

                if doc['bijlagetype']['id'] == 2: # is verslag / rapport
                    #print(doc['bestandsnaam'])

                    file_name = doc['bestandsnaam'].replace(' ','_')

                    output_document = {}
                    output_document['source'] = 'onroerend_erfgoed'
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
                    output_document['identifiers'] = {'uri':project['uri']}
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

                    #print(json.dumps(output_document, indent=4))

                    # save document.json 2DO get json location from settings
                    json_output_folder = f"json/onroerend_erfgoed/{project['id']}_{file_name.replace('.pdf','')}"
                    save_json(output_document, f"{json_output_folder}/document.json")

                    # download pdf
                    file_url = doc['url']
                    pdf_location = download_document(file_url, 'onroerend_erfgoed', project['id'], file_name)

                    # process pdf, store page.json files with entities 2DO get modeldir from settings file
                    run_ner_on_pdf(
                        pdf_location, 
                        json_output_folder, 
                        '/data1/brandsena/lucdh-dataset/archeobertje-production-model-fold2/', 
                        'dutch'
                    )






