import re

# import element tree; to parse xml
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#import subprocess; to call pdf-extract
import subprocess

# import os; to loop through files
import os

# import multithreading
from multiprocessing.dummy import Pool as ThreadPool

# language detection
from langdetect import detect as detectLanguage

# url encoding
import urllib

# fuzzy matching
from fuzzywuzzy import fuzz

import html

import sys
import traceback

import json

# for curl
import requests, json

from collections import defaultdict

# frog, for POS tagging
#import frog
#frog = frog.Frog(frog.FrogOptions(parser=False,lemma=False,ner=False,morph=False))

# get CRF model and feature creation function
#import crfpredict

from PyPDF2 import PdfReader

import nltk
nltk.data.path.append('/data1/brandsena/nltk_data/')

import pickle

# BERT model import

from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
from collections import defaultdict


import torch



sys.path.insert(1, '/home/brandsena/timeperiod-to-daterange/')
import timeperiod2daterange

# set higher recursion for pypdf2
sys.setrecursionlimit(10000)

# logging settings
import logging
logger = logging.getLogger('xml2json')
hdlr = logging.FileHandler('xml2json.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)


# server location (no trailing slash) / port
#esServerLocation = 'http://132.229.16.43'
#esServerPort = '9200'

# set elasticsearch index name
#esIndex = 'agnesv03_withfacets'


jsonFolder = '/data1/brandsena/document-sources/DANS_rapporten_2020/json/'

# get DANS easy number to DOI dict
with open('DANS-easynumber2doi.pkl', 'rb') as f:
    easy2doi = pickle.load(f)

def get_known_DANS_document_numbers(dans_location):
    files = os.listdir(dans_location)
    d_numbers = []
    for file in files:
        d_numbers.append(file.split('_')[0])
    return d_numbers

dans_numbers = get_known_DANS_document_numbers ('/data1/brandsena/jsontest/')
print(f"Processed known DANS numbers, found {len(dans_numbers)} D numbers")

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def invalid_xml_remove(c, replacement=' '):
    """Takes string, replaces invalid chars and returns the updated string"""
    # http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
    illegalunichrs = [(0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
                       (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
                       (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
                       (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                       (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
                       (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                       (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
                       (0x10FFFE, 0x10FFFF)]

    illegal_ranges = ["%s-%s" % (chr(low), chr(high))
                      for (low, high) in illegalunichrs
                      if low < sys.maxunicode]

    illegal_xml_re = re.compile(u'[%s]' % u''.join(illegal_ranges))
    if illegal_xml_re.search(c) is not None:
        # Replace with replacement
        return replacement
    else:
        return c


def multiThreadRecursiveFolderFunction(dir='pdf/', numberOfThreads = 1, functionName = 'pdf2xml'):
    """find files in folder, apply function to all files, multithreaded"""
    logger.info('starting multithreading (with '+str(numberOfThreads)+' threads) on each file in folder: '+dir)
    print('starting multithreading (with '+str(numberOfThreads)+' threads) on each file in folder: '+dir)

    # put each file in folder into a list
    fileNameArray = []
    for directory, subdirectories, files in os.walk(dir):
        for file in files:
            if file != '.dropbox.attr': # dropbox hidden file, skip
                file_location = os.path.join(directory, file)
                fileNameArray.append(file_location)

                if functionName == 'pdf2xml':
                    #create xml sub directory if needed
                    xmlDirectory = directory.replace(dir, 'xml/')
                    if not os.path.exists(xmlDirectory):
                        os.makedirs(xmlDirectory)

    # multi threading
    pool = ThreadPool(numberOfThreads)
    if functionName == 'pdf2xml':
        pool.map(pdf2xml1file, fileNameArray)
    elif functionName == 'index':
        pool.map(index, fileNameArray)


def run_ner_on_pdf(fileLocation, outputFolder, modelDir, language = 'dutch'):

    # set up BERT predictor 
    cudaGpuNumber = torch.cuda.current_device()
    #print('cuda gpu number is '+str(cudaGpuNumber))
    model = AutoModelForTokenClassification.from_pretrained(modelDir)
    tokenizer = AutoTokenizer.from_pretrained(modelDir)
    predictor = pipeline(
                          'ner', 
                          model=model, 
                          tokenizer=tokenizer,
                          device = cudaGpuNumber, # 0 for gpu, -1 for cpu
                          grouped_entities = False
                        )
    
    # create a pdf reader object
    try:
        reader = PdfReader(fileLocation)
    except Exception as error:
        print('PDF reading error')
        print(error)
        return False # something wrong with pdf, skip file
        
    
    # loop through pages 
    for i in range(0, len(reader.pages) ):
    
        pageNumber = i + 1

        #logger.info('working on page '+str(pageNumber)+' of file '+fileLocation)
        #print('working on page '+str(pageNumber)+' of file '+fileLocation)
        
        page = reader.pages[i]
        
        pageEntities = defaultdict(list)
        pageTimespans = []	
        maxYear = False
        minYear = False
        maxYearExcludingRecent = False	
        
        
        pageText = page.extract_text()
                
        # create sentences
        #print('make sentences')
        sent_text = nltk.sent_tokenize(pageText, language = language) # this gives us a list of sentences
        
        # loop through sentences
        for sentence in sent_text:
            #print(sentence)
            
            # get entities 
            #print('get entities')
            entities = predictor(sentence)
            #print('entities retrieved')
            
            concatenatedEntity = ''
            currentLabel = False
            prevEntity = {'index':0}
            
            for entity in entities:
                #print(entity)
                
                if entity['word'] != '[UNK]' and entity['word'] != '[CLS]':
                    # beginning of entity
                    if entity['word'][:2] != '##' and (entity['entity'][:1] == 'B' or prevEntity['index']+1 < entity['index']):
                        # save previous entity
                        if currentLabel:
                            pageEntities[currentLabel].append(concatenatedEntity)
                            if currentLabel == 'PER':
                                timespan = timeperiod2daterange.detection2daterange(concatenatedEntity)
                                if timespan:
                                    pageTimespans.append({'startdate':timespan[0],'enddate':timespan[1]})
                                    if not minYear or timespan[0] < minYear:
                                        minYear = timespan[0]
                                    if not maxYear or timespan[1] > maxYear:
                                        maxYear = timespan[1]
                                    if timespan[1] < 1950 and (not maxYearExcludingRecent or timespan[1] > maxYearExcludingRecent):
                                        maxYearExcludingRecent = timespan[1]
                                        
                        
                        # store entity in memory          
                        concatenatedEntity = entity['word']
                        currentLabel = entity['entity'][2:]
                    
                    # continuation of word in entity
                    elif entity['word'][:2] == '##':
                        concatenatedEntity += entity['word'][2:]
                        
                    # new word in same entity
                    else:
                        concatenatedEntity += ' '+entity['word']
                        
                    prevEntity = entity
                
        # save as json
        #print('save json')
        pageJsonOutput = '{"page_number":"' + str(pageNumber) + '","content":"'+pageText+'"'
        if pageEntities:
            pageJsonOutput += ', "ner_entities":'+json.dumps(pageEntities)
        if pageTimespans:
            pageJsonOutput += ', "timespans":'+json.dumps(pageTimespans)
        if minYear and (maxYear or maxYearExcludingRecent):
            pageJsonOutput += ', "minYear":'+str(minYear)
            if maxYear:
                pageJsonOutput += ', "maxYear":'+str(maxYear)
            if maxYearExcludingRecent:
                pageJsonOutput += ', "maxYearExcludingRecent":'+str(maxYearExcludingRecent)
            
        pageJsonOutput += '}'
        
        with open(outputFolder+'/page'+str(pageNumber)+'.json', "w") as text_file:
            text_file.write(pageJsonOutput) 
        

        #print (pageJsonOutput)
        #print (r.text)

def index(fileLocation):

    try:

        logger.info('Working on: ' + fileLocation)
        print('Working on: ' + fileLocation)

        file = fileLocation.split('/')[-1]
        directory = '/'.join(fileLocation.split('/')[0:-1])
        #print(file)
        #print(directory) 
        
        outputFolder = jsonFolder+file.replace('.pdf','')
        if os.path.exists(outputFolder):
            print('Output folder for '+file+' already exists, skipping')
            return False #skip this file if it already exists
        else:
            # create folder, do try just in case other process has already made the folder
            try:
                os.mkdir(outputFolder)
                print('created folder '+outputFolder)
            except:
                print('cannot create folder '+outputFolder)
                return False
        
        documentJsonOutput = ''

        documentJsonOutput += '{'
        documentJsonOutput += '"file_name":"' + file.replace('.xml','.pdf') + '",'
        documentJsonOutput += '"subfolder":"' + directory.replace('xml/','pdf/') + '",'
        documentJsonOutput += '"file_location":"' + fileLocation.replace('.xml','.pdf').replace('xml/','pdf/') + '",'


        # check dag/week rapport etc, so we can filter these out in ES
        rapportList = ['dagrapport' , 'dag_rapport' , 'weekrapport' , 'week_rapport' , 'weekverslag' , 'week_verslag' , 'logboek']
        pvaList = ['draaiboek' , 'plan_van_aanpak' , 'pva']
        pveList = ['programma_van_eisen' , 'pve']
        omnList = ['onderzoeksmeldingsnummer' , 'onderzoeksmeldings_nummer' , 'onderzoeks_meldings_nummer']
        if any(word in file.lower() for word in rapportList):
            documentJsonOutput += '"file_type":"dag_week_rapport",'
        elif any(word in file.lower() for word in pvaList):
            documentJsonOutput += '"file_type":"plan_van_aanpak",'
        elif any(word in file.lower() for word in pveList):
            documentJsonOutput += '"file_type":"programma_van_eisen",'
        elif any(word in file.lower() for word in omnList):
            documentJsonOutput += '"file_type":"onderzoeksmeldingsnummer",'
        else:
            documentJsonOutput += '"file_type":"report",'

        fileSource = 'dans' # hardcoded for now, needs to change later 2DO
        if fileSource == 'dans':
            # get DANS info

            datasetID = file.split('_')[0][1:]
            # older reports have format D_0000_NAME.pdf, need to check
            if len(datasetID) == 1:
                datasetID = file.split('_')[1]

            
            # optional: check if we already have json for this D number
            check_existing = True
            if check_existing:
                #print(f"checking D number: {datasetID}")
                if datasetID in dans_numbers:
                    print(f"{datasetID} already indexed previously, skipping!")
                    return false;

            doi = easy2doi[datasetID]        
            url = 'https://archaeology.datastations.nl/api/datasets/export?exporter=OAI_ORE&persistentId=doi%3A'+doi
            #print(url)
            
            try:
                response = urllib.request.urlopen(url)
                metadata = json.loads(response.read())
                metadata = metadata['ore:describes']
            except Exception as error:
                print('dans json error for '+datasetID+', doi: '+doi)
                print(error)
                return False # something wrong with dans metadata, skip file
            

            #print(data)          

            # title
            title = metadata['title']
            documentJsonOutput += '"title":' + json.dumps(title) + ','

            # alternative title
            if 'alternativeTitle' in metadata.keys():
                altTitle = metadata['alternativeTitle']
                documentJsonOutput += '"altTitle":' + json.dumps(altTitle) + ','

            # author(s)
            if 'author' in metadata.keys():
                documentJsonOutput += '"creators":['
                authors = metadata['author']
                for author in authors:
                    if(type(author) is dict):
                        documentJsonOutput += '"' + author['citation:authorName'] + '",'
                    else:
                        documentJsonOutput += '"' + authors[author] + '",'

                # take off last comma
                documentJsonOutput = documentJsonOutput[:-1] + '],'

            # description
            if 'citation:dsDescription' in metadata.keys():
                description = ''
                descriptions = metadata['citation:dsDescription']
                for desc in descriptions:
                    if type(desc) is str:
                        description += remove_html_tags(descriptions[desc]) + '\n'
                    else:
                        description += remove_html_tags(desc['citation:dsDescriptionValue']) + '\n'
                documentJsonOutput += '"description":' + json.dumps(description) + ','

            # publisher / rightsholder
            if 'dansRights:dansRightsHolder' in metadata.keys():
                if type(metadata['dansRights:dansRightsHolder']) is list:
                    rightsHolder = ', '.join(metadata['dansRights:dansRightsHolder'])
                else:
                    rightsHolder = metadata['dansRights:dansRightsHolder']
                documentJsonOutput += '"publisher":"' + rightsHolder + '",'

            # published date
            if 'citation:distributionDate' in metadata.keys():
                documentJsonOutput += '"createdAt":"' + metadata['citation:distributionDate'] + '",'
            elif 'dateOfDeposit' in metadata.keys():
                documentJsonOutput += '"createdAt":"' + metadata['dateOfDeposit'] + '",'

            # identifiers
            documentJsonOutput += '"identifiers":{'
            documentJsonOutput += '"doi":"' + metadata['@id'] + '",'
            # add more?
            documentJsonOutput = documentJsonOutput[:-1] + '},'

            # language
            if 'language' in metadata.keys():
                if type(metadata['language']) is list: # multiple languages
                    documentJsonOutput += '"language":"' + ', '.join(metadata['language']) + '",'
                else: # 1 language
                    documentJsonOutput += '"language":"' + metadata['language'] + '",'
                    

            # locations
            if 'dansTemporalSpatial:dansSpatialCoverageText' in metadata.keys():
                documentJsonOutput += '"locations":['
                locations = metadata['dansTemporalSpatial:dansSpatialCoverageText']
                if type(locations) is list:
                    for location in locations:
                        documentJsonOutput += '"' + location + '",' 
                else:
                    documentJsonOutput += '"' + locations + '",' 
                documentJsonOutput = documentJsonOutput[:-1] + '],' 

            # temporals
            if 'dansTemporalSpatial:dansTemporalCoverage' in metadata.keys():
                documentJsonOutput += '"temporals":['
                temporals = metadata['dansTemporalSpatial:dansTemporalCoverage']
                if type(temporals) is list:
                    for temporal in temporals:
                        documentJsonOutput += '"' + temporal + '",'   
                else:
                    documentJsonOutput += '"' + temporals + '",' 
                documentJsonOutput = documentJsonOutput[:-1] + '],' 

            # subjects / keywords
            if 'citation:keyword' in metadata.keys():
                #print(metadata['citation:keyword'])
                documentJsonOutput += '"subjects":['
                subjects = metadata['citation:keyword']
                if type(subjects) is list:
                    for subject in subjects:
                        if(type(subject) is dict):
                            documentJsonOutput += '"' + subject['citation:keywordValue'] + '",'    
                        else:
                            documentJsonOutput += '"' + subjects[subject] + '",'  
                else:
                    if(type(metadata['citation:keyword']) is dict):
                        documentJsonOutput += '"' + metadata['citation:keyword']['citation:keywordValue'] + '",'    
                    else:
                        documentJsonOutput += '"' + metadata['citation:keyword'] + '",'  
                documentJsonOutput = documentJsonOutput[:-1] + '],' 


            # coordinates 

            coordX = False
            coordY = False

            if 'dansTemporalSpatial:dansSpatialBox' in metadata.keys():
                # bounding box
                #print(metadata['dansTemporalSpatial:dansSpatialBox'])
                if type(metadata['dansTemporalSpatial:dansSpatialBox']) is list: # multiple boxes, calculate average
                    totalX = 0
                    totalY = 0
                    for box in metadata['dansTemporalSpatial:dansSpatialBox']:
                        totalX += (float(box['dansTemporalSpatial:dansSpatialBoxEast']) + float(box['dansTemporalSpatial:dansSpatialBoxWest'])) / 2 
                        totalY += (float(box['dansTemporalSpatial:dansSpatialBoxSouth']) + float(box['dansTemporalSpatial:dansSpatialBoxNorth'])) / 2
                    coordX = totalX / len(metadata['dansTemporalSpatial:dansSpatialBox'])
                    coordY = totalY / len(metadata['dansTemporalSpatial:dansSpatialBox'])
                else: # 1 box, take east/west & north/south coords, divide by 2 to get centre
                    coordX = (float(metadata['dansTemporalSpatial:dansSpatialBox']['dansTemporalSpatial:dansSpatialBoxEast']) + float(metadata['dansTemporalSpatial:dansSpatialBox']['dansTemporalSpatial:dansSpatialBoxWest'])) / 2 
                    coordY = (float(metadata['dansTemporalSpatial:dansSpatialBox']['dansTemporalSpatial:dansSpatialBoxSouth']) + float(metadata['dansTemporalSpatial:dansSpatialBox']['dansTemporalSpatial:dansSpatialBoxNorth'])) / 2 

            elif 'dansTemporalSpatial:dansSpatialPoint' in metadata.keys():
                # point
                #print(metadata['dansTemporalSpatial:dansSpatialPoint'])
                if type(metadata['dansTemporalSpatial:dansSpatialPoint']) is list: # multiple points, calculate average
                    totalX = 0
                    totalY = 0
                    for point in metadata['dansTemporalSpatial:dansSpatialPoint']:
                        #print(point)
                        totalX += float(point['dansTemporalSpatial:dansSpatialPointX'])
                        totalY += float(point['dansTemporalSpatial:dansSpatialPointY'])
                    coordX = totalX / len(metadata['dansTemporalSpatial:dansSpatialPoint'])
                    coordY = totalY / len(metadata['dansTemporalSpatial:dansSpatialPoint'])
                else: # 1 point, save as is
                    coordX = float(metadata['dansTemporalSpatial:dansSpatialPoint']['dansTemporalSpatial:dansSpatialPointX'])
                    coordY = float(metadata['dansTemporalSpatial:dansSpatialPoint']['dansTemporalSpatial:dansSpatialPointY'])
            
            elif 'dansTemporalSpatial:dansSpatialCoverageText' in metadata.keys():
                #print('doing GEOCODING')
                # no coordinates, try geocoding the location(s)
                try:
                    locations = metadata['dansTemporalSpatial:dansSpatialCoverageText']
                    query = ''
                    if type(locations) is list:
                        for location in locations:
                            query += location + ', ' 
                    else:
                        documentJsonOutput = locations 
                    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=geojson&limit=1"
                    #print(url)
                    response = urllib.request.urlopen(url)
                    data = json.loads(response.read())
                    if len(data['features']): # if results
                        lat = data['features']['geometry']['coordinates'][0]
                        lon = data['features']['geometry']['coordinates'][1]
                        documentJsonOutput += '"location":{'
                        documentJsonOutput += '"lat":' + str(lat) + ','
                        documentJsonOutput += '"lon":' + str(lon)
                        documentJsonOutput += '},'
                except Exception as error:
                    print('geocoding error')
                    print(error)
            
            if coordX and coordY:
                documentJsonOutput += '"coordX":"' + str(coordX) + '",'
                documentJsonOutput += '"coordY":"' + str(coordY) + '",'
                #convert to lat lon
                try:
                    lat, lon = rd2wgs(coordX,coordY)
                    documentJsonOutput += '"location":{'
                    documentJsonOutput += '"lat":' + str(lat) + ','
                    documentJsonOutput += '"lon":' + str(lon)
                    documentJsonOutput += '},'
                except:
                    print('error converting coordinates from rd to wgs for DANS id '+datasetID)


        elif fileSource == 'rce':
            # TODO get RCE info
            print ('rce document')

        # take off last comma
        documentJsonOutput = documentJsonOutput[:-1] + '}'

        # convert to utf-8
        #documentJsonOutput = documentJsonOutput.encode('utf-8')

        with open(outputFolder+'/document.json', "w") as text_file:
            try:
                text_file.write(documentJsonOutput) 
            except:
                documentJsonOutput = documentJsonOutput.encode('utf-8')
                text_file.write(documentJsonOutput) 


        #print documentJsonOutput
        #break

        try:
            run_ner_on_pdf(fileLocation, outputFolder, 'dutch')
        except Exception as error:
            print('PDF error')
            print(error)
            return False # something wrong with pdf, skip file
        

        print ('Finished indexing file '+file)
        
    except Exception as error:
        print('indexing error for '+datasetID+', doi: '+doi)
        print(error)
        return False # something wrong, skip file

def pdf2xml1file(file):
    """convert single file from pdf to xml/html, function used purely for multi-threading"""
    errormsg = False
    # pdf-extract first
    # if xml does not already exist
    if not os.path.isfile('xml/' + file.replace('.pdf', '.xml').replace('pdf/', '')):

        #print "Converting " + file + " to xml"

        try:
            cmnd = 'pdf-extract extract --references --headers --footers --no-lines --regions --set char_slop:0.4 ' + file.replace(' ', '\ ') + ' > ' + file.replace('pdf/','xml/').replace('.pdf', '.xml').replace(' ','\ ')
            #print cmnd
            output = subprocess.check_output(
                cmnd, stderr=subprocess.STDOUT, shell=True,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            if "undefined method `*' for nil:NilClass" in exc.output:
                #problem with reference extraction, try without reference extraction
                try:
                    cmnd = 'pdf-extract extract --headers --footers --no-lines --regions --set char_slop:0.4 ' + file.replace(
                        ' ', '\ ') + ' > ' + file.replace('pdf/', 'xml/').replace('.pdf', '.xml').replace(' ', '\ ')
                    output = subprocess.check_output(
                        cmnd, stderr=subprocess.STDOUT, shell=True,
                        universal_newlines=True)
                except subprocess.CalledProcessError as exc:
                    #still an error present
                    errormsg = "pdf-extract error for file " + file + " " + exc.output
                else:
                    print ("Converted " + file + " to xml! (no references)")
            else:
                errormsg = "pdf-extract error for file " + file + " " + exc.output

            if errormsg:
                # error in pdf-extract, discard output file and write to log
                print (errormsg)
                logger.error(errormsg)
                os.remove(file.replace('pdf/','xml/').replace('.pdf', '.xml'))
        else:
            print ("Converted " + file + " to xml!")
    else:
        print (file.replace('pdf/','xml/').replace('.pdf', '.xml') + " already exists, skipping")

    #then do html conversion
    # TODO maybe use md5 of file for folder name to stop clashes?
    htmlDir = 'html/' + file.replace('.pdf', '').replace('pdf/', '')
    if not os.path.isdir(htmlDir):
        # first create folder for html to go in

        _mkdir(htmlDir)

        try:
            cmnd = 'pdftohtml -c -nodrm ' + file.replace(' ', '\ ') + ' ' + htmlDir + '/index.html'
            output = subprocess.check_output(
                cmnd, stderr=subprocess.STDOUT, shell=True,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            errormsg = "pdftohtml error for file " + file + " " + exc.output
            print (errormsg)
            logger.error(errormsg)
            os.rmdir(htmlDir)
        else:
            print ("Converted " + file + " to html!")

    else:
        print (file + " html folder already exists, skipping")



def _mkdir(_dir):
    if os.path.isdir(_dir): pass
    elif os.path.isfile(_dir):
        raise OSError("%s exists as a regular file." % _dir)
    else:
        parent, directory = os.path.split(_dir)
        if parent and not os.path.isdir(parent): _mkdir(parent)
        if directory: os.mkdir(_dir)



def cleanFileNames(dir):
    """loop through each file in dir recursively and replace spaces with underscores"""
    for directory, subdirectories, files in os.walk(dir):
        for file in files:
            file_location = os.path.join(directory, file)

            clean_file_location = file_location.replace(' ', '_')
            for ch in [';',':','"',"'",',','&','(',')','!','@','#','$','%','^','*']:
                if ch in clean_file_location:
                    clean_file_location = clean_file_location.replace(ch, '')

            if file_location != clean_file_location:
                print (file_location, ' renamed to ', clean_file_location)
                os.rename(file_location,clean_file_location)
    print ("All filenames cleaned")

def rd2wgs (x,y):
    """Calculate WGS84 coordinates"""
    x = int(x)
    y = int(y)

    dX = (x - 155000) * pow(10, - 5)
    dY = (y - 463000) * pow(10, - 5)

    SomN = (3235.65389 * dY) + (- 32.58297 * pow(dX, 2)) + (- 0.2475 * pow(dY, 2)) + (- 0.84978 * pow(dX, 2) * dY) + (- 0.0655 * pow(dY, 3)) + (- 0.01709 * pow(dX, 2) *pow(dY, 2)) + (- 0.00738 * dX) + (0.0053 * pow(dX, 4)) + (- 0.00039 * pow(dX, 2) *pow(dY, 3)) + (0.00033 * pow(dX, 4) * dY) + (- 0.00012 * dX * dY)

    SomE = (5260.52916 * dX) + (105.94684 * dX * dY) + (2.45656 * dX * pow(dY, 2)) + (- 0.81885 * pow(dX, 3)) + (0.05594 * dX * pow(dY, 3)) + (- 0.05607 * pow(dX, 3) * dY) + (0.01199 * dY) + (- 0.00256 * pow(dX, 3) *pow(dY, 2)) + (0.00128 * dX * pow(dY, 4)) + (0.00022 * pow(dY,2)) + (- 0.00022 * pow(dX, 2)) + (0.00026 * pow(dX, 5))

    lat = 52.15517 + (SomN / 3600);
    lon = 5.387206 + (SomE / 3600);

    return lat,lon
