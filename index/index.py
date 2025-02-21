#!/usr/bin/env python3

"""
Indexing script for the AGNES system
"""

import argparse
from collections.abc import Sequence
import os
import re
import requests
import json
import sys
from langdetect import detect as detectLanguage
from collections import defaultdict
import torch

import pprint
pp = pprint.PrettyPrinter(indent=4)


def main(argv: Sequence[str] | None = None):

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("pdfDir", help="Full path to the folder containing the PDFs to be indexed")
    parser.add_argument("fileSource", help="Source of files", type=str, choices=['dans', 'rce', 'oe', 'sidestone'])
    parser.add_argument("--cleanFileNames", help="Clean filenames by removing spaces / bad characters", action="store_true")
    parser.add_argument("--doHtmlConversion", help="Flag to do PDF to HTML conversion. Also specify htmlDir if flagged.", action="store_true")
    parser.add_argument("htmlDir", help="Full path to the folder where the HTML versions of the PDFs should be stored")
    args = parser.parse_args()
    
    
    # clean filenames
    if args.cleanFileNames:
        print ('---------- clean filenames --------------\n')
        cleanFileNames(args.pdfDir)

    # do pdf2html
    if args.doHtmlConversion:
        print ('---------- start pdf2html --------------\n')
        pdf2html(args.pdfDir,args.htmlDir)

    # do indexing
    print ('\n---------- start creating index ------------\n')
    index(args.pdfDir)

    print ('Done!')

    return True


def cleanFileNames(dir):
    """loop through each file in dir recursively and remove spaces / bad chars"""
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

def _mkdir(_dir):
    """makes dir and parent dir(s) if needed"""
    if os.path.isdir(_dir): pass
    elif os.path.isfile(_dir):
        raise OSError("%s exists as a regular file." % _dir)
    else:
        parent, directory = os.path.split(_dir)
        if parent and not os.path.isdir(parent): _mkdir(parent)
        if directory: os.mkdir(_dir)
        
def pdf2html(file,outputFolder):
    """convert single file from pdf to html"""
    errormsg = False
    
    # TODO maybe use md5 of file for folder name to stop clashes?
    htmlDir = f"{outputFolder}/{file.replace('.pdf', '').replace('pdf/', '')}"
    if not os.path.isdir(htmlDir):
    
        # first create folder for html to go in
        _mkdir(htmlDir)

        try:
            # run pdftohtml tool, without DRM check, save in htmlDir output folder
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

if __name__ == "__main__":
    raise SystemExit(main())















