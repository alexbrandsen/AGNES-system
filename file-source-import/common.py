#!/usr/bin/env python

"""Common functions for reading / writing files, etc, used by document import modules"""

import urllib.request
import requests
import json
import os
import shutil
from transformers import pipeline
from collections import defaultdict
import torch
import pandas as pd
import json
import paramiko
import sys
import time
import yaml
import re
from PyPDF2 import PdfReader
import pickle
import subprocess
import nltk
import datetime
from func_timeout import func_timeout, FunctionTimedOut


sys.path.insert(1, '/home/alex/surfdrive/timeperiod2daterange/')
import timeperiod2daterange

# set higher recursion for pypdf2
sys.setrecursionlimit(10000)

# get config
def get_config(config_location = '../../config.yml'):
    with open(config_location) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config
config_location = "../../config.yml"
config = get_config(config_location)


# load BERT models      2DO add other languages!
cudaGpuNumber = torch.cuda.current_device()
print('cuda gpu number is '+str(cudaGpuNumber))


# Dutch    2DO fix selecting the model from folder
modelDir = config['bert_models']['dutch']
predictor = pipeline("token-classification", model="alexbrandsen/ArcheoBERTje-NER", grouped_entities = False, device=0)
"""
model = AutoModelForTokenClassification.from_pretrained(modelDir)
tokenizer = AutoTokenizer.from_pretrained(modelDir)
predictor = pipeline(
                      'ner', 
                      model=model, 
                      tokenizer=tokenizer,
                      device = cudaGpuNumber, # 0 for gpu, -1 for cpu
                      grouped_entities = False
                    )
"""





def savejson(data, location):
    """Save json data to json file"""
    
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
    
    return True
    
    
def downloaddocument(file_url, file_id, pdf_folder, file_name = False):
    """Downloads a file and saves it locally"""
    
    # if file name not specified, use last part of url as filename
    if not file_name:
        file_name = file_url.split('/')[-1]
        
    output_location = f"{pdf_folder}{file_id}_{file_name}"
    
    # check if already downloaded
    if os.path.isfile(output_location):
        print(f"file {output_location} has already been downloaded")
    else:
        urllib.request.urlretrieve(file_url, output_location) 
    
    return output_location

def _mkdir(_dir):
    """Updated mkdir function which also makes a dir if it doesn't exist, instead of throwing an error"""
    
    if os.path.isdir(_dir): pass
    elif os.path.isfile(_dir):
        raise OSError("%s exists as a regular file." % _dir)
    else:
        parent, directory = os.path.split(_dir)
        if parent and not os.path.isdir(parent): _mkdir(parent)
        if directory: os.mkdir(_dir)
        return True


def pdf_timeout_handler(signum, frame):
    """Used to handle pdf processing timeout in run_ner_on_pdf()"""
    #print("PDF processing timed out")
    raise Exception("PDF processing timed out")
    
def run_ner_on_pdf(fileLocation, outputFolder, bert_model, language = 'dutch'):
    """Run NER with BERT model on each page of a PDF file, save JSON for each page"""
    
    _mkdir(outputFolder)
    
    #print('try to read pdf')
    
    try:
        # create a pdf reader object
        try:
            reader = PdfReader(fileLocation, strict=True)
        except Exception as error:
            print('PDF reading error')
            print(error)
            return False # something wrong with pdf, skip file
            
        
        # loop through pages 
        for i in range(0, len(reader.pages) ):
        
            pageNumber = i + 1

            #print('working on page '+str(pageNumber)+' of file '+fileLocation)
            
            page = reader.pages[i]
            
            #print('pages read') 
            
            pageEntities = defaultdict(list)
            pageTimespans = []    
            maxYear = False
            minYear = False
            maxYearExcludingRecent = False    
            
            
            # try page.extract_text with a 60 sec timeout, as it sometimes gets stuck indefinitely on a page
            try:
                pageText = func_timeout(60, page.extract_text, args=())
            
            except FunctionTimedOut:
                print ('pdf text extract timed out, skipping')
                continue
            
            except Exception as e:
                print(e)
                continue

       

#            try:
#                pageText = page.extract_text()
#            except Exception as error:
#                print('PDF reading error')
#                print(error)
#                return False # something wrong with pdf, skip file

            
            #print('text extracted') 
            
            pageText = pageText.replace('\n',' ') # replace line endings with spaces
                    
            # create sentences
            #print('make sentences')
            sent_text = nltk.sent_tokenize(pageText, language = language) # this gives us a list of sentences
            
            #print('sentence loop start')
            
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
            pageJsonOutput = {
                "page_number":pageNumber,
                "content":pageText
            }
            if pageEntities:
                pageJsonOutput["ner_entities"] = pageEntities
            if pageTimespans:
                pageJsonOutput["timespans"] = pageTimespans
            if minYear and (maxYear or maxYearExcludingRecent):
                pageJsonOutput["minYear"] = minYear
                if maxYear:
                    pageJsonOutput["maxYear"] = maxYear
                if maxYearExcludingRecent:
                    pageJsonOutput["maxYearExcludingRecent"] = maxYearExcludingRecent
                
            
            savejson(pageJsonOutput, outputFolder+'/page'+str(pageNumber)+'.json')
            
            #print (pageJsonOutput)
            #print (r.text)
    except Exception as error:
        print('PDF reading error')
        print(error)
        return False
        
def pdf2html(file_location,htmlDir):
    """convert single file from pdf to html"""

    # do html conversion
    # TODO maybe use md5 of file for folder name to stop clashes?

    if not os.path.isdir(htmlDir):
        # first create folder for html to go in
        _mkdir(htmlDir)

        try:
            cmnd = 'pdftohtml -c -nodrm ' + file_location.replace(' ', '\ ') + ' ' + htmlDir + '/index.html'
            output = subprocess.check_output(
                cmnd, stderr=subprocess.STDOUT, shell=True,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            errormsg = "pdftohtml error for file " + file_location + " " + exc.output
            print (errormsg)
            os.rmdir(htmlDir)
        else:
            print ("Converted " + file_location + " to html!")

    else:
        print (file_location + " html folder already exists, skipping")


def cleanFileName(filename):
    """remove unwanted chars, spaces to underscores"""
    

    clean_filename = filename.replace(' ', '_')
    for ch in [';',':','"',"'",',','&','(',')','!','@','#','$','%','^','*','⅓','½']:
        if ch in clean_filename:
            clean_filename = clean_filename.replace(ch, '')

    return clean_filename        
       
class MySFTPClient(paramiko.SFTPClient):
    """class for uploading whole json/html folders to webserver via SFTP  """
    
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are 
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


def upload2webserver(json_source, html_source, source_name, json_target, html_target):
    """Upload json and html folders to webserver via SFTP"""
    
    # connect to webserver via SFTP with a SSH key
    host = config['webserver']['ip']
    user = config['webserver']['ssh_user']
    port = config['webserver']['ssh_port']
    
    transport = paramiko.Transport((host, port))
    pkey = paramiko.RSAKey.from_private_key_file("/home/alex/.ssh/id_rsa")
    transport.connect(username=user, pkey=pkey)
    sftp = MySFTPClient.from_transport(transport)

    # upload json and move to json-UPLOADED folder
    for folder in os.listdir(json_source):
        #print(folder)

        source_path = f"{json_source}{folder}"
        target_path = f"{json_target}{source_name}/{folder}"
        
        sftp.mkdir(target_path, ignore_existing=True)
        sftp.put_dir(source_path, target_path)

        shutil.move(source_path, source_path.replace('/json/','/json-UPLOADED/'))

    # upload html and move to html-UPLOADED folder
    for folder in os.listdir(html_source):
        #print(folder)

        source_path = f"{html_source}{folder}"
        target_path = f"{html_target}{source_name}/{folder}"
        
        sftp.mkdir(target_path, ignore_existing=True)
        sftp.put_dir(source_path, target_path)

        shutil.move(source_path, source_path.replace('/html/','/html-UPLOADED/'))
        
    # close connection
    sftp.close()
       


        
def rd2wgs (x,y):
    """Calculate WGS84 coordinates from Dutch RD coordinates"""
    x = int(x)
    y = int(y)

    dX = (x - 155000) * pow(10, - 5)
    dY = (y - 463000) * pow(10, - 5)

    SomN = (3235.65389 * dY) + (- 32.58297 * pow(dX, 2)) + (- 0.2475 * pow(dY, 2)) + (- 0.84978 * pow(dX, 2) * dY) + (- 0.0655 * pow(dY, 3)) + (- 0.01709 * pow(dX, 2) *pow(dY, 2)) + (- 0.00738 * dX) + (0.0053 * pow(dX, 4)) + (- 0.00039 * pow(dX, 2) *pow(dY, 3)) + (0.00033 * pow(dX, 4) * dY) + (- 0.00012 * dX * dY)

    SomE = (5260.52916 * dX) + (105.94684 * dX * dY) + (2.45656 * dX * pow(dY, 2)) + (- 0.81885 * pow(dX, 3)) + (0.05594 * dX * pow(dY, 3)) + (- 0.05607 * pow(dX, 3) * dY) + (0.01199 * dY) + (- 0.00256 * pow(dX, 3) *pow(dY, 2)) + (0.00128 * dX * pow(dY, 4)) + (0.00022 * pow(dY,2)) + (- 0.00022 * pow(dX, 2)) + (0.00026 * pow(dX, 5))

    lat = 52.15517 + (SomN / 3600);
    lon = 5.387206 + (SomE / 3600);

    return lat,lon
 

def update_config(data_source, doc_id, value):
    """Update config file"""
    # load config from file
    with open(config_location) as f:
        config = yaml.safe_load(f)
    
    # update config with new value
    config['data_source'][data_source][doc_id] = value

    # save config to file
    with open(config_location, 'w') as f:
        yaml.safe_dump(config, f) 
        

def start_index(source):
    """Remotely start the index on the webserver, for a specific source"""
    
    # connect to webserver via SSH with a SSH key
    host = '136.144.205.98'
    user = 'alexbrandsen'
    port = 22
    
    sshcon = paramiko.SSHClient()  # will create the object
    sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # no known_hosts error
    pkey = paramiko.RSAKey.from_private_key_file("/home/alex/.ssh/id_rsa")
    sshcon.connect(host, username=user, pkey=pkey) # no passwd needed

    # get datetime, to put in logfile name
    now = datetime.datetime.now()
    datetime_string = now.strftime("%Y-%m-%d_%Hh%M")
    
    # run command with nohup and dev/null to not wait for completion, and log to a file
    #(as per https://stackoverflow.com/questions/29142/getting-ssh-to-execute-a-command-in-the-background-on-target-machine)
    command = f"nohup python3 /home/alexbrandsen/upload-json-to-elasticsearch.py {source} >json_import_logs/{source}_{datetime_string}.log 2>&1 </dev/null &"
    stdin, stdout, stderr = sshcon.exec_command(command)

    # close connection
    sshcon.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
              

