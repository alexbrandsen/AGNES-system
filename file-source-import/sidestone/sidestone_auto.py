#!/usr/bin/env python3

"""
Script to import documents from Onroerend Erfgoed to AGNES
"""

# import nltk / download punkt
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

# import libraries
import urllib.request
import requests
import json
from pyproj import Transformer
import os
import time
import sys
from datetime import datetime
#from lxml import etree
from xml.etree import ElementTree as ET
import logging

# import common functions
sys.path.insert(1, '../')
import common

# set name of module, to fetch info from config
module_name = "dans"



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
last_indexed_date = config['data_source'][module_name]['last_indexed_date']
logging.info(f'last_indexed_date: {last_indexed_date}')

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


#API settings
index_datetimestring = str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
providerName = 'Data_Station_Archaeology'
api_url = endpoint_url + 'search'
meta_url = endpoint_url + 'datasets/export'
content_url = endpoint_url + 'access/datafile/'
headers = {'Origin': 'http://agnessearch.nl',
           'Access-Control-Request-Method': 'GET',
           'httpAccept': 'application/json',
           'User-Agent': 'python-requests/2.18.1',
           'From': 'a.brandsen@arch.leidenuniv.nl (EXALT)'  
          }
page_length = 100  # size of the metadata chunks
datesort = "dateSort:["+str(last_indexed_date)+" TO "+index_datetimestring+"Z]"


params = {
            'X-Dataverse-Key': '0450fc54-e0e7-4692-b82c-e196eed69b12',  # personal API key valid till 01.05.2024
            'start': 0,                                                 # start of iteration
            'per_page': page_length,                                    # results in pages of n datasets (max. 1000)
            'type': 'dataset',
            'fq': 'publicationStatus:Published',                        # no Draft datasets
            'fq': datesort,  # everything from selected date onwards
            #'q': 'benedenberg',                                          # query (*) within archaeology.datastation.nl
            #'q': 'authorName:(schinkel AND fokkens)',                    # AND 
            #'q': 'authorName:(schinkel+OR+fokkens+OR+fontijn)',          # OR
            #'q': 'dsPublicationDate:2023',
            'q': 'dsPublicationDate:(2022 OR 2023 OR 2024 OR 2025 OR 2026 OR 2027 OR 2028 OR 2029)',                              # year of publication
            #'q': 'dsPublicationDate:(1930 OR 1950 OR 1951 OR 1952 OR 1953 OR 1954 OR 1955 OR 1956 OR 1958 OR \
            #          1959 OR 1961 OR 1962 OR 1963 OR 1964 OR 1965 OR 1966 OR 1967 OR 1968 OR 1969 \
            #          OR 1970 OR 1971 OR 1972 OR 1973 OR 1974 OR 1975 OR 1976 OR 1977 OR 1978 OR 1979 \
            #          OR 1980 OR 1981 OR 1982 OR 1983 OR 1984 OR 1985 OR 1986 OR 1987 OR 1988 OR 1989 \
            #          OR 1990 OR 1991 OR 1992 OR 1993 OR 1994 OR 1995 OR 1996 OR 1997 OR 1998 OR 1999 \
            #          OR 2000 OR 2001 OR 2002 OR 2003 OR 2004 OR 2005)',
}


# Create a requests Session
session = requests.Session()
# Set the header options, zoals 'application/json'
session.headers.update(headers)


i = 0
# Make a request and store the response
try:
    response = session.get(api_url, params=params)
    response.raise_for_status()                 # Raise error in case of failure 
except requests.exceptions.HTTPError as httpErr: 
    logging.info("HTTP Error:",httpErr) 
except requests.exceptions.ConnectionError as connErr: 
    logging.info("Error Connecting:",connErr) 
except requests.exceptions.Timeout as timeOutErr: 
    logging.info("Timeout Error:",timeOutErr) 
except requests.exceptions.RequestException as reqErr: 
    logging.info("Something Else:",reqErr)



if response.status_code == requests.codes.ok:
    
    if response:

        data = response.json()
            
        response_length = data['data']['total_count']
        logging.info('Datasets found: '+ str(response_length))
            
        dsets = data['data']['items']

        # Fetch all the other pages of results
        page = 1
        while (page*page_length+1) <= response_length:
            params['start'] = (page*page_length)
            #logging.info(page, params['start'])

            # GET the next page of dataset metadata
            next_response = session.get(api_url, params=params)
            if next_response.status_code == requests.codes.ok:
             if next_response:
                 next_data = next_response.json()
                 next_dsets = next_data['data']['items']
        
                 # add the data from the next page to the data we collected
                 dsets = dsets + next_dsets
            page = page + 1
            #time.sleep(1)                 # being kind to the API server

    else:
        logging.info('Empty result')
else:
    logging.info('Web connection Error')



#processing the metadata of the datasets
if dsets:

    # sort dsets by published date
    date_sorted_dsets = sorted(dsets, key=lambda d: d['published_at'])
    
    logging.info('Processing: ' + str(len(date_sorted_dsets)) + ' datasets')
    for dset in date_sorted_dsets:

        # skip to specific dataset TEMP
        #if dset['global_id'] != 'doi:10.17026/AR/5VSVUK':
        #    continue
        
        #logging.info(json.dumps(dset, indent=4, sort_keys=False))  
        logging.info('--------------------------------------------')
        logging.info('Processing dataset: '+dset['global_id'])
        
        # get extended metadata
        if dset['global_id']:
            dataset_doi = dset['global_id']
            meta_params = { 'X-Dataverse-Key': '0450fc54-e0e7-4692-b82c-e196eed69b12',
                            'exporter': 'dataverse_json',                             # metadata format
                            'httpAccept': 'application/json',
                            'persistentId': dataset_doi}
            meta_response = requests.get(meta_url, params=meta_params)                # request dataset metadata
            
            if meta_response.status_code == requests.codes.ok:
                if meta_response:
                    metadata = meta_response.json()

                    #logging.info(json.dumps(metadata, indent=4, sort_keys=False)) 
                    #exit()

                    metadataBlocks = metadata['datasetVersion']['metadataBlocks']
                    
                    files = metadata['datasetVersion']['files']
                    for file in files:
                        #logging.info(file)
                        dataFile = file['dataFile']
                        if dataFile['contentType'] == 'application/pdf':

                            logging.info('Processing file: '+dataFile['filename'])

                            # generate document dictionary
                            output_document = {}
                            output_document['source'] = module_name
                            output_document['file_name'] = common.cleanFileName(dataFile['filename'])
                            output_document['description'] = dset['description']
                            output_document['title'] = dset['name']
                            output_document['creators'] = dset['authors']
                            output_document['publisher'] = dset['publisher']
                            output_document['createdAt'] = dset['published_at'][:10]
                            
                            identifiers = {
                                'DOI':dset['global_id'],
                                'url':dset['url'],
                                'dans_dataset_version_id': dset['versionId']
                            }
                            if 'dansArchaeologyMetadata' in metadataBlocks:
                                for thing in metadataBlocks['dansArchaeologyMetadata']['fields']:
                                    if thing['typeName'] == 'dansArchisZaakId':
                                        identifiers['dansArchisZaakId'] = thing['value']
                            if 'dansDataVaultMetadata' in metadataBlocks:
                                for thing in metadataBlocks['dansDataVaultMetadata']['fields']:
                                    identifiers[thing['typeName']] = thing['value']
                            output_document['identifiers'] = identifiers

                            if 'citation' in metadataBlocks:
                                for thing in metadataBlocks['citation']['fields']:
                                    if thing['typeName'] == 'language':
                                        output_document['language'] = thing['value']
                            
                            # check dag/week rapport etc, so we can filter these out in ES
                            rapportList = ['dagrapport' , 'dag_rapport' , 'weekrapport' , 'week_rapport' , 'weekverslag' , 'week_verslag' , 'logboek']
                            pvaList = ['draaiboek' , 'plan_van_aanpak' , 'pva']
                            pveList = ['programma_van_eisen' , 'pve']
                            omnList = ['onderzoeksmeldingsnummer' , 'onderzoeksmeldings_nummer' , 'onderzoeks_meldings_nummer']
                            if any(word in dataFile['filename'].lower() for word in rapportList):
                                output_document['file_type'] = 'dag_week_rapport'
                            elif any(word in dataFile['filename'].lower() for word in pvaList):
                                output_document['file_type'] = 'plan_van_aanpak'
                            elif any(word in dataFile['filename'].lower() for word in pveList):
                                output_document['file_type'] = 'programma_van_eisen'
                            elif any(word in dataFile['filename'].lower() for word in omnList):
                                output_document['file_type'] = 'onderzoeksmeldingsnummer'
                            else:
                                output_document['file_type'] = 'report'
                            
                            
                            # coordinates 
                            coordX = False
                            coordY = False

                            if 'dansTemporalSpatial' in metadataBlocks:
                                for thing in metadataBlocks['dansTemporalSpatial']['fields']:
                                    if thing['typeName'] == 'dansSpatialBox':
                                        # bounding box
                                        #logging.info(thing)
                                        totalX = 0
                                        totalY = 0
                                        for box in thing['value']:
                                            #logging.info(box)
                                            # some datasets are missing 1 of the 4 corners... so check if they all exist
                                            if 'dansSpatialBoxEast' in box and 'dansSpatialBoxWest' in box and 'dansSpatialBoxSouth' in box and 'dansSpatialBoxNorth' in box:
                                                totalX += (float(box['dansSpatialBoxEast']['value']) + float(box['dansSpatialBoxWest']['value'])) / 2 
                                                totalY += (float(box['dansSpatialBoxSouth']['value']) + float(box['dansSpatialBoxNorth']['value'])) / 2
                                        coordX = totalX / len(thing['value'])
                                        coordY = totalY / len(thing['value'])
                                        
                                    elif thing['typeName'] == 'dansSpatialPoint':
                                        # point
                                        #logging.info(thing['value'])
                                        totalX = 0
                                        totalY = 0
                                        for point in thing['value']:
                                            #logging.info(point)
                                            if 'dansSpatialPointX' in point and 'dansSpatialPointY' in point:
                                                totalX += float(point['dansSpatialPointX']['value'])
                                                totalY += float(point['dansSpatialPointY']['value'])
                                        coordX = totalX / len(thing['value'])
                                        coordY = totalY / len(thing['value'])
                                       
                            
                            if not coordX and not coordY:
                                # no coordinates, try geocoding the location(s)
                                if 'dansTemporalSpatial' in metadataBlocks:
                                    for thing in metadataBlocks['dansTemporalSpatial']['fields']:    
                                        if thing['typeName'] == 'dansSpatialCoverageText':
                                            #logging.info('doing GEOCODING')
                                            try:
                                                locations = thing['value']
                                                query = ''
                                                if type(locations) is list:
                                                    for location in locations:
                                                        query += location + ', ' 
                                                url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=geojson&limit=1"
                                                #logging.info(url)
                                                response = urllib.request.urlopen(url)
                                                data = json.loads(response.read())
                                                if len(data['features']): # if results
                                                    lat = data['features'][0]['geometry']['coordinates'][0]
                                                    lon = data['features'][0]['geometry']['coordinates'][1]
                                                    output_document['location'] = {'lat':lat,'lon':lon}
                                            except Exception as error:
                                                logging.info('geocoding error')
                                                logging.info(error)                                

                            if coordX and coordY:
                                output_document['coordX'] = coordX
                                output_document['coordY'] = coordY
                                #convert to lat lon
                                try:
                                    lat, lon = common.rd2wgs(coordX,coordY)
                                    output_document['location'] = {'lat':lat,'lon':lon}
                                except:
                                    logging.info('error converting coordinates from rd to wgs for DOI '+dset['global_id'])

                            
                            # object file download (Open Access)
                            if dataFile['id'] and not file['restricted']:

                                # check for embargo
                                present = datetime.now()                                     
                                embargo = datetime.now()
                                
                                if 'embargo' in file.keys():
                                    embargo = datetime.strptime(filemeta['embargo'], "%Y-%m-%d")
                                
                                if not embargo.date() > present.date(): 

                                    # set document identifier
                                    doc_id = f"{dset['versionId']}_{common.cleanFileName(dataFile['filename'].replace('.pdf',''))}"
                                    
                                    logging.info(f"doc_id:{doc_id}")

                                    # TEMP if already downloaded, skip
                                    #output_location = f"{pdf_folder}{dset['versionId']}_{common.cleanFileName(dataFile['filename'])}"
                                    #if os.path.isfile(output_location):
                                    #    logging.info('already downloaded, SKIPPING')
                                    #    continue

                                    # sometimes get download error, so try and continue if error
                                    try:
                                        # download pdf
                                        file_url = content_url + str(dataFile['id'] ) 
                                        pdf_location = common.downloaddocument(
                                            file_url, 
                                            dset['versionId'], 
                                            pdf_folder, 
                                            common.cleanFileName(dataFile['filename'])
                                        )
                                        logging.info(f"downloaded pdf")
                                    except Exception as e:
                                        logging.info(f"could not download pdf, error:")
                                        logging.info(e)
                                        continue

                                    # save document.json 
                                    json_output_folder = f"{json_folder}/{doc_id}"
                                    common.savejson(output_document, f"{json_output_folder}/document.json")
                    
                                    logging.info(f"saved doc json")
                    
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
                                    common.update_config(module_name, 'last_indexed_date', dset['published_at'])
                                    
                                    logging.info(f"updated config with latest date: {dset['published_at']}")
                                          

                                else:
                                    logging.info('embargoed: '+ dset['name'])
                            else:
                                logging.info('restricted: ' + dset['name'])
                        #else:
                             #logging.info('not pdf: ' + dataFile['filename'])
                                 

            else:
                logging.info(dset['global_id'] + ' no dataset metadata found')
                
    # upload json and html to webserver
    common.upload2webserver(json_folder, html_folder, module_name, config['webserver']['json_folder'], config['webserver']['html_folder'])

    logging.info(f"uploaded json/html to webserver")

    # remotely start indexing script on webserver
    common.start_index(module_name)

    logging.info(f"indexing on webserver started")

else:
    logging.info('No new documents')
    

logging.info(f"done!")




