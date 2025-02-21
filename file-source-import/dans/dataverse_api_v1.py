import requests
import json
import time
from datetime import datetime
#from lxml import etree
from xml.etree import ElementTree as ET

#file settings
metadataOnly = False
basedir = 'J:\\Workgroups\\ARCH\\EDNA\\projecten_wansleeben\\projecten\\DANS_Dataverse'
metadir = basedir + '\\metadata'
session = '12'
docsdir = basedir + '\\docs\\' + session

#API settings
providerName = 'Data_Station_Archaeology'
base_url = 'https://archaeology.datastations.nl/api/'  
api_url = base_url + 'search'
meta_url = base_url + 'datasets/export'
content_url = 'https://archaeology.datastations.nl/api/access/datafile/'
headers = {'Origin': 'http://agnessearch.nl',
           'Access-Control-Request-Method': 'GET',
           'httpAccept': 'application/json',
           'User-Agent': 'python-requests/2.18.1',
           'From': 'm.wansleeben@arch.leidenuniv.nl (EXALT)'  
          }
page_length = 25  # size of the metadata chunks

params = {'X-Dataverse-Key': '0450fc54-e0e7-4692-b82c-e196eed69b12',  # personal API key valid till 01.05.2024
          'start': 0,                                                 # start of iteration
          'per_page': page_length,                                    # results in pages of n datasets (max. 1000)
          'type': 'dataset',
          'fq': 'publicationStatus:Published',                        # no Draft datasets
          'fq': 'dateSort:[2023-10-01T00:00:00Z TO 2023-12-31T23:59:59Z]',  # alles vanaf 01.10.23
          #'q': 'benedenberg'}                                          # query (*) within archaeology.datastation.nl
          #'q': 'authorName:(schinkel AND fokkens)'}                    # AND 
          #'q': 'authorName:(schinkel+OR+fokkens+OR+fontijn)'}          # OR
          'q': 'dsPublicationDate:2023'}
          #'q': 'dsPublicationDate:(2013 OR 2014 OR 2015)'}                              # year of publication
          #'q': 'dsPublicationDate:(1930 OR 1950 OR 1951 OR 1952 OR 1953 OR 1954 OR 1955 OR 1956 OR 1958 OR \
          #          1959 OR 1961 OR 1962 OR 1963 OR 1964 OR 1965 OR 1966 OR 1967 OR 1968 OR 1969 \
          #          OR 1970 OR 1971 OR 1972 OR 1973 OR 1974 OR 1975 OR 1976 OR 1977 OR 1978 OR 1979 \
          #          OR 1980 OR 1981 OR 1982 OR 1983 OR 1984 OR 1985 OR 1986 OR 1987 OR 1988 OR 1989 \
          #          OR 1990 OR 1991 OR 1992 OR 1993 OR 1994 OR 1995 OR 1996 OR 1997 OR 1998 OR 1999 \
          #          OR 2000 OR 2001 OR 2002 OR 2003 OR 2004 OR 2005)'}

outputfile = metadir + '\\datasetmetadata' + session + '.csv'
objectsfile = metadir + '\\filemetadata' + session + '.csv'
errorfile = metadir + '\\document_errorlog_' + session + '.csv'
outf = open(outputfile, 'w', encoding='utf-8')
objf = open(objectsfile, 'w', encoding='utf-8')
errf = open(errorfile, 'w', encoding='utf-8')

# Create a requests Session
session = requests.Session()
# Set the header options, zoals 'application/json'
session.headers.update(headers)

#csv export setting
csv_columns = ('provider','doi','type','id','version','title','alt_title','published','created','updated','creator','contributor','language','rights', \
               'description','keywords','archis','report_id','complex','period','location','location_name','relation')
obj_columns = ('provider','doi','file_id','directory','filename','restricted','embargo','content_type', \
               'filesize','storage_id','file_date')

# dataset metadata header
csv_header = ''
for csv_column in csv_columns:
  csv_header = csv_header + csv_column
  if csv_columns.index(csv_column) < len(csv_columns)-1:
    csv_header = csv_header + ';'
outf.write (csv_header + '\n')   # bij csv import in nieuwe tabel
# file objects header
obj_header = ''
for obj_column in obj_columns:
  obj_header = obj_header + obj_column
  if obj_columns.index(obj_column) < len(obj_columns)-1:
    obj_header = obj_header + ';'
objf.write (obj_header + '\n')   # bij csv import in nieuwe tabel

i = 0
# Make a request and store the response
try:
    response = session.get(api_url, params=params)
    response.raise_for_status()                 # Raise error in case of failure 
except requests.exceptions.HTTPError as httpErr: 
    print ("HTTP Error:",httpErr) 
except requests.exceptions.ConnectionError as connErr: 
    print ("Error Connecting:",connErr) 
except requests.exceptions.Timeout as timeOutErr: 
    print ("Timeout Error:",timeOutErr) 
except requests.exceptions.RequestException as reqErr: 
    print ("Something Else:",reqErr)

if response.status_code == requests.codes.ok:
  if response:

    data = response.json()
    response_length = data['data']['total_count']
    print('Datasets found: '+ str(response_length))
    dsets = data['data']['items']
    # print (len(dsets))
    print('.', end='')

    # Fetch all the other pages of results
    page = 1
    while (page*page_length+1) <= response_length:
      params['start']= (page*page_length)
      #print (page, params['start'])

      # GET the next page of dataset metadata
      next_response = session.get(api_url, params=params)
      if next_response.status_code == requests.codes.ok:
       if next_response:
         next_data = next_response.json()
         next_dsets = next_data['data']['items']
    
         # add the data from the next page to the data we collected
         dsets = dsets + next_dsets
      page = page + 1
      print ('.', end ='')
      time.sleep(1)         # being kind to the API server

    print ('')  
    #processing the metadata of the datasets
    if dsets:
      print ('Processing: ' + str(len(dsets)))
      for dset in dsets:
        #print(json.dumps(dset, indent=4, sort_keys=False))        
        # genereer document dictionary
        doc={}
        #print (dset['name'])
        print(dset['global_id'])
        doc['provider'] = providerName
        doc['doi'] = dset['global_id']
        doc['type'] = dset['type']
        #doc['title'] = dset['name']
        doc['description'] = dset['description']
        doc['published'] = dset['published_at'].replace('T',' ').replace('Z','')        

        if 'keywords' in dset.keys():
          keyword_list = ''
          keywords = dset['keywords']
          for keyword in keywords:
            if len(keyword_list) > 0: keyword_list = keyword_list + '; '
            keyword_list = keyword_list + keyword
          doc['keywords'] = keyword_list

        # get extended metadata
        if dset['global_id']:
          dataset_doi = dset['global_id']
          meta_params = { 'X-Dataverse-Key': '0450fc54-e0e7-4692-b82c-e196eed69b12',
                          'exporter': 'dataverse_json',                     # metadata format
                          'httpAccept': 'application/json',
                          'persistentId': dataset_doi}
          meta_response = requests.get(meta_url, params=meta_params)        # request dataset metadata
          
          if meta_response.status_code == requests.codes.ok:
           if meta_response:
             metadata = meta_response.json()

             version = metadata['datasetVersion']               # is the only and last Version
             doc['id'] = version['datasetId']
             doc['version'] = version['versionNumber']
             doc['created'] = version['createTime'].replace('T',' ').replace('Z','')
             doc['updated'] = version['lastUpdateTime'].replace('T',' ').replace('Z','')
             metadata_blocks = version['metadataBlocks']

             # citation metadata block
             if 'citation' in metadata_blocks.keys():
               citation_metadata = metadata_blocks['citation']
               citation_fields = citation_metadata['fields']
               for field in citation_fields:
                # title   
                if field['typeName']=='title':
                 if field['typeClass'] == 'primitive':  
                   doc['title'] = field['value']
                # alternative title   
                if field['typeName']=='alternativeTitle':
                 if field['typeClass'] == 'primitive':  
                   doc['alt_title'] = field['value']
                # author(s)   
                if field['typeName']=='author':
                 if not field['multiple']:                # single (primitive) value
                   doc['creator'] = field['value']
                 else:                                    # multiple (compound) values
                   value_list = ''
                   items = field['value']
                   for item in items:
                     if len(value_list) > 0: value_list = value_list + '|'
                     value_list = value_list + item['authorName']['value']
                   doc['creator'] = value_list
                # contributor(s)
                if field['typeName']=='contributor':
                 if not field['multiple']:  
                   doc['contributor'] = field['value']
                 else:
                   value_list = ''
                   items = field['value']
                   for item in items:
                     if len(value_list) > 0: value_list = value_list + '|'
                     if 'contributorName' in item.keys():
                       value_list = value_list + item['contributorName']['value']
                   doc['contributor'] = value_list
                # language  
                if field['typeName']=='language':
                 if not field['multiple']:  
                   doc['language'] = field['value']
                 else:
                   value_list = ''
                   items = field['value']
                   for item in items:
                     if len(value_list) > 0: value_list = value_list + '|'
                     value_list = value_list + item
                   doc['language'] = value_list
                   
                # long description (the short(er) description from the query result is used)
                if field['typeName']=='dsDescription':
                 if not field['multiple']:  
                   #doc['long_description'] = field['value']      this is not added to the dictionary
                   pass  
                 else:
                   value_list = ''
                   items = field['value']
                   for item in items:
                     if len(value_list) > 0: value_list = value_list + ' '
                     value_text = item['dsDescriptionValue']['value']
                     value_text = value_text.replace('<p>','').replace('</p>','').replace('\'','\"')
                     value_list = value_list + value_text
                   #doc['long_description'] = value_list          this is not added to the dictionary

                # publication - publicationIDType/publicationIDNumber
                # ISBN/ISSN van gerelateerde publicatie

             # rights metadata block
             if 'dansRights' in metadata_blocks.keys():
               rights_metadata = metadata_blocks['dansRights']
               rights_fields = rights_metadata['fields']
               for field in rights_fields:
                 # rightsHolder
                 if field['typeName'] == 'dansRightsHolder':
                   if not field['multiple']:  
                     doc['rights'] = field['value']
                   else:
                     value_list = ''
                     items = field['value']
                     for item in items:
                       if len(value_list) > 0: value_list = value_list + '|'
                       value_list = value_list + item
                     doc['rights'] = value_list
              
             # relation metadata block
             if 'dansRelationMetadata' in metadata_blocks.keys():
               relations_metadata = metadata_blocks['dansRelationMetadata']
               relations_fields = relations_metadata['fields']
               for field in relations_fields:
                 # dansCollection
                 # dansRelation - is part of
                 if field['typeName'] == 'dansRelation':
                   if not field['multiple']:
                     pass
                   else:
                     value_list = ''                   
                     relations = field['value']
                     for relation in relations:
                       if relation['dansRelationType']['value'] == 'is part of':
                         if len(value_list) > 0: value_list = value_list + '|'
                         value_list = value_list + relation['dansRelationText']['value'] 
                     if len(value_list)>0: doc['relation'] = value_list

             # archaeology metadata block
             if 'dansArchaeologyMetadata'in metadata_blocks.keys():
               archaeology_metadata = metadata_blocks['dansArchaeologyMetadata']
               archaeology_fields = archaeology_metadata['fields']
               for field in archaeology_fields:
                 # archisNumber(s), starting wih zaakidentificatie
                 if field['typeName'] == 'dansArchisZaakId':
                   if not field['multiple']:
                     value_list = field['value'] + '(zaakidentificatie)'
                   else:
                     items = field['value']
                     value_list = ''
                     for item in items:
                       if len(value_list) > 0: value_list = value_list + '|'
                       value_list = value_list + item + '(zaakidentificatie)'
                   if  'archis' in doc.keys():
                     if not value_list == '':
                       doc['archis'] = doc['archis'] + '|' + value_list
                   else:
                     doc['archis'] = value_list
                 # other Archis numbers    
                 if field['typeName'] == 'dansArchisNumber':
                   if not field['multiple']:
                     value_list = field['value']
                   else:
                     items = field['value']
                     value_list = ''
                     for item in items:
                       if 'dansArchisNumberId' in item.keys(): 
                         if len(value_list) > 0: value_list = value_list + '|'
                         value_list = value_list + item['dansArchisNumberId']['value']
                         if 'dansArchisNumberType' in item.keys():
                           value_list = value_list + '(' + item['dansArchisNumberType']['value'] + ')'
                   if  'archis' in doc.keys():
                     if not value_list == '':
                       doc['archis'] = doc['archis'] + '|' + value_list
                   else:
                     doc['archis'] = value_list

                 # ABR period(s)   uses the ABR ontology at https://data.cultureelerfgoed.nl
                 if field['typeName'] == 'dansAbrPeriod':
                   # period as URL
                   if not field['multiple']:  
                     doc['period'] = field['value']  #ToDO aanpassen
                   else:
                     value_list = ''
                     items = field['value']  
                     for item in items:
                     
                       # formulate ontology request
                       abr_url = item + '.xml'
                       abr_response = requests.get(abr_url)

                       if abr_response.status_code == requests.codes.ok:
                         #print (abr_response.content)
                         xml_response = ET.fromstring(abr_response.content)

                         tree = ET.ElementTree(xml_response)
                         root=tree.getroot()
                         namespaces = {'ns':'http://www.w3.org/2004/03/trix/trix-1/'}
                         for label in root.findall('ns:graph/ns:triple[ns:uri="http://www.w3.org/2004/02/skos/core#prefLabel"]', namespaces):
                           prefLabel = label.find('ns:plainLiteral', namespaces).text
                           if len(value_list)> 0: value_list = value_list + '|'
                           value_list = value_list + prefLabel
                         # hiddenLabel is ABR code
                       else:
                         if len(value_list)> 0: value_list = value_list + '|'
                         value_list = value_list + item                  
                       doc['period'] = value_list

                 # ABR complex type(s)   uses the ABR ontology at https://data.cultureelerfgoed.nl
                 if field['typeName'] == 'dansAbrComplex':
                   # complex as URL
                   if not field['multiple']:  
                     doc['complex'] = field['value'] # ToDO aanpassen
                   else:
                     value_list = ''
                     items = field['value']
                     for item in items:

                       # formulate ontology request
                       abr_url = item + '.xml'
                       abr_response = requests.get(abr_url)

                       if abr_response.status_code == requests.codes.ok:
                         #print (abr_response.content)
                         xml_response = ET.fromstring(abr_response.content)

                         tree = ET.ElementTree(xml_response)
                         root=tree.getroot()
                         namespaces = {'ns':'http://www.w3.org/2004/03/trix/trix-1/'}
                         for label in root.findall('ns:graph/ns:triple[ns:uri="http://www.w3.org/2004/02/skos/core#prefLabel"]', namespaces):
                           prefLabel = label.find('ns:plainLiteral', namespaces).text
                           if len(value_list)> 0: value_list = value_list + '|'
                           value_list = value_list + prefLabel
                         # hiddenLabel is ABR code
                       else:
                         if len(value_list)> 0: value_list = value_list + '|'
                         value_list = value_list + item 
                       doc['complex'] = value_list

                 # ABR rapport number(s)
                 if field['typeName'] == 'dansAbrRapportNummer':
                   if not field['multiple']:  
                     doc['report_id'] = field['value']
                   else:
                     value_list = ''
                     items = field['value']
                     for item in items:
                       if len(value_list) > 0: value_list = value_list + '|'
                       value_list = value_list + item
                     doc['report_id'] = value_list
                   
             # temporal spatial metadata block
             if 'dansTemporalSpatial' in metadata_blocks.keys():
               spatial_metadata = metadata_blocks['dansTemporalSpatial']
               spatial_fields = spatial_metadata['fields']
               for field in spatial_fields:
                 # ABR period(s) as TEXT (overwrite any URL based period)
                 if field['typeName'] == 'dansTemporalCoverage':
                   if not field['multiple']:  
                     doc['period'] = field['value']
                   else:
                     value_list = ''
                     items = field['value']
                     for item in items:
                       if len(value_list) > 0: value_list = value_list + '|'
                       value_list = value_list + item
                     doc['period'] = value_list           
                 # dansSpatialPoint
                 if field['typeName'] == 'dansSpatialPoint':
                   if not field['multiple']:  
                     doc['location'] = field['value']
                   else:
                     value_list = ''
                     items = field['value']
                     for item in items:
                       if len(value_list) > 0: value_list = value_list + '|'
                       if 'dansSpatialPointX' in item.keys() and 'dansSpatialPointY' in item.keys():
                         value_list = value_list + item['dansSpatialPointX']['value'] + '/' + item['dansSpatialPointY']['value']
                         if 'dansSpatialPointScheme' in item.keys():
                           value_list = value_list + ' (' + item['dansSpatialPointScheme']['value'] + ')'
                     doc['location'] = value_list                
                 # Place name(s)
                 if field['typeName'] == 'dansSpatialCoverageText':
                   if not field['multiple']:  
                     doc['location_name'] = field['value']
                   else:
                     value_list = ''
                     items = field['value']
                     for item in items:
                       if len(value_list) > 0: value_list = value_list + '|'
                       value_list = value_list + item
                     doc['location_name'] = value_list 

             # datavault metadata block
             if 'dansDataVaultMetadata' in metadata_blocks.keys():
               datavault_metadata = metadata_blocks['dansDataVaultMetadata']
               datavault_fields = datavault_metadata['fields']
               for field in datavault_fields:
                 pass

             #print (len(citation_fields), len(rights_fields), len(relations_fields), len(archaeology_fields), len(datavault_fields))
             #print (doc)

             # generate dataset metadata record
             csv_record = ''
             for csv_column in csv_columns:
               values = doc.get(csv_column, '')
               #print ('"' + values + '"', end='')
               # meervoudige waarden
               if isinstance(values, list):
                 #print ('"', end='')
                 csv_record = csv_record + '"'
                 for value in values:
                   if value:       # kan None zijn  
                     #print (value, end='')
                     # vervang eventuele " door '
                     csv_record = csv_record + value.replace('\"','\'')
                     if values.index(value) < len(values)-1:
                       #print ('|', end='')
                       csv_record = csv_record + '|'
                 #print ('"', end='')
                 csv_record = csv_record + '"'
               if isinstance(values,str):
                 csv_record = csv_record + '"' + values.replace('\"','\'') + '"'
               if isinstance(values, (int, float)):
                 csv_record = csv_record + str(values)
                
               if csv_columns.index(csv_column) < len(csv_columns)-1:
                  #print (';', end='')
                  csv_record = csv_record + ';'
             outf.write (csv_record + '\n')   
             i = i + 1

             # process dataset files
             bestanden = version['files']
             # print ('Data files: '+ str(len(bestanden)) + ' with ',end='')
             nPdfs = 0
             for bestand in bestanden:
               dataFile = bestand['dataFile']
               if dataFile['contentType'] == 'application/pdf':
                 # genereer file metadata dictionary
                 filemeta = {}
                 filemeta['provider'] = providerName
                 filemeta['doi'] = dset['global_id']
                 filemeta['file_id'] = dataFile['id']
                 filemeta['filename'] = dataFile['filename']
                 subdir = ''
                 if 'directoryLabel' in bestand.keys():
                   subdir  =  bestand['directoryLabel'] + '/'
                 filemeta['directory'] = subdir
                 filemeta['restricted'] = bestand['restricted']
                 if 'embargo' in dataFile.keys():
                   filemeta['embargo'] = dataFile['embargo']['dateAvailable']
                 filemeta['content_type'] = dataFile['contentType']
                 filemeta['filesize'] = dataFile['filesize']
                 filemeta['storage_id'] = dataFile['storageIdentifier'].replace('file://','')
                 filemeta['file_date'] = dataFile['creationDate']
                 nPdfs = nPdfs + 1

                 #print (filemeta)
                 #print (dataFile['id'], bestand['restricted'], subdir + dataFile['filename'], dataFile['contentType'], dataFile['filesize'], dataFile['storageIdentifier'])  

                 # generate file object metadata record
                 csv_record = ''
                 for obj_column in obj_columns:
                   values = filemeta.get(obj_column, '')
                   #print ('"' + values + '"', end='')
                   # meervoudige waarden
                   if isinstance(values, list):
                     #print ('"', end='')
                     csv_record = csv_record + '"'
                     for value in values:
                       if value:       # kan None zijn  
                         #print (value, end='')
                         # vervang eventuele " door '
                         csv_record = csv_record + value.replace("\"","\'")
                         if values.index(value) < len(values)-1:
                           #print ('|', end='')
                           csv_record = csv_record + '|'
                     #print ('"', end='')
                     csv_record = csv_record + '"'
                   if isinstance(values,str):
                     csv_record = csv_record + '"' + values + '"'
                   if isinstance(values, (int, float)):
                     csv_record = csv_record + str(values)
                    
                   if obj_columns.index(obj_column) < len(obj_columns)-1:
                      #print (';', end='')
                      csv_record = csv_record + ';'
                 objf.write (csv_record + '\n')   


                 # object file download (Open Access)
                 if dataFile['id'] and not metadataOnly and not bestand['restricted']:
                   present = datetime.now()                   
                   embargo = datetime.now()
                   if 'embargo' in filemeta.keys():
                     embargo = datetime.strptime(filemeta['embargo'], "%Y-%m-%d")
                   download_url = content_url + str(dataFile['id'] )  
                   if not embargo.date() > present.date(): 
                     file_headers = {'User-Agent': 'python-requests/2.18.1',
                                     'From': 'm.wansleeben@arch.leidenuniv.nl (EXALT)' }                
                     file_params = {'X-Dataverse-Key': '0450fc54-e0e7-4692-b82c-e196eed69b12',
                                    'httpAccept' : 'application/pdf'                       }               

                     r = requests.get(download_url, headers=file_headers, params=file_params, stream=True)
                     if r.status_code == requests.codes.ok:
                       # check if pdf is returned by request
                       r_contenttype = r.headers['Content-Type']
                       if 'application/pdf' in r_contenttype.lower():
                         r_filename = 'D' + str(version['datasetId']) + '_' + dataFile['filename']
                        
                         StrOutfilename = docsdir + '\\' + r_filename
                         if len(StrOutfilename) > 254:
                           StrOutfilename = StrOutfilename[0:249] + StrOutfilename[-4:]
                         #print (StrOutfilename)
                      
                         #download file
                         with open(StrOutfilename, 'wb') as fd:
                           for chunk in r.iter_content(512*1024):
                            fd.write(chunk)
                           
                       else:
                         print ('No pdf: '+ download_url)
                     else:
                        print ('Response error: ' + str(r.status_code) + ' for ' + download_url)
                        #f.i. status code 403 Forbidden
                        errf.write('"' + dset['global_id'] + '";' + str(dataFile['id']) + ';"' + str(r.status_code) + '"\n')   
                   else:
                     # date embargo on file is still active
                     print ('Response error: temporal embargo for ' + download_url)
                     errf.write('"' + dset['global_id'] + '";' + str(dataFile['id']) + ';"temporal file embargo"\n')
                     
             #print (str(nPdfs) + ' pdf(s).' )

          else:
            print (dataset['global_id'] + ' no dataset metadata found')
            errf.write('"' + dset['global_id'] + '"; null; "no dataset metadata"\n')   
    else:
      print ('Processing: 0')
  else:
    print ('Empty result')
else:
    print ('Web connection Error')

print ('Saved: ' + str(i))
#close files
errf.close()
objf.close()
outf.close()     
