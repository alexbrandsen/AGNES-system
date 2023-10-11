import requests
import json

#file settings
metadataOnly = False
basedir = 'J:\\Workgroups\\ARCH\\EDNA\\projecten_wansleeben\\projecten\\Vlaanderen\\verslag'
metadir = basedir + '\\metadata'
docsdir = basedir + '\\docs'
outputfile = metadir + '\\document_metadata_2022.csv'
objectsfile = metadir + '\\document_fileobjects_2022.csv'
errorfile = metadir + '\\document_errorlog_2022.csv'
outf = open(outputfile, 'w', encoding='utf-8')
objf = open(objectsfile, 'w', encoding='utf-8')
errf = open(errorfile, 'w', encoding='utf-8')

#REST settings
providerName = 'VIOE_rapporten' 
vioe_url = 'https://loket.onroerenderfgoed.be/archeologie/rapporten/eindverslagen/'
headers = {'Accept': 'application/json', 
           'User-Agent': 'python-requests/2.18.1',
           'From': 'm.wansleeben@arch.leidenuniv.nl (EXALT)'  
          }
# https://loket.onroerenderfgoed.be/archeologie/rapporten/eindverslagen?publiek=False&sort=id&per_pagina=50&pagina=2
params = {'publiek': False,
          'per_pagina': 50,
          'sort': 'id',
          'pagina': 12 }   # deelresultaten van 50 stuks

# Create a requests Session
session = requests.Session()
# Set the header options, zoals 'application/json'
session.headers.update(headers)

#csv export setting
#csv_columns = ('provider','id','datestamp', 'status', 'title','creator','contributor','subject','description','publisher','date','date_created', \
#               'type','size','format','identifier','resource','language','coverage','relation','source','rights')
csv_columns = ('provider','id','uri','naam','uitvoerder','veldwerk_datum','created','updated','projecttype','rapporttype','provincies','gemeenten','XYlocatie','projectcodes','relaties')

csv_header = ''
for csv_column in csv_columns:
  csv_header = csv_header + csv_column
  if csv_columns.index(csv_column) < len(csv_columns)-1:
    csv_header = csv_header + ';'
#outf.write (csv_header + '\n')   # bij csv import in nieuwe tabel

# Make a request and store the response
try:
    response = session.get(vioe_url, params=params)
    response.raise_for_status()                 # Raise error in case of failure 
except requests.exceptions.HTTPError as httpErr: 
    print ("HTTP Error:",httpErr) 
except requests.exceptions.ConnectionError as connErr: 
    print ("Error Connecting:",connErr) 
except requests.exceptions.Timeout as timeOutErr: 
    print ("Timeout Error:",timeOutErr) 
except requests.exceptions.RequestException as reqErr: 
    print ("Something Else:",reqErr)

i = 0
if response.status_code == requests.codes.ok:
 if response:
    content_range = response.headers['Content-Range'][6:]
    # The part after the slash is the total number of results
    #number_of_results = content_range.split('/')[1]
    # Split the part before the slash on `-`, before is the first result in this page
    #start_result = content_range.split('/')[0].split('-')[0].strip()
    # Split the part before the slash on `-`, after is the last result in this page
    #end_result = content_range.split('/')[0].split('-')[1].strip()
    print(content_range)
    data = response.json()

    # Fetch all the other pages of results (hier ongebruikt, via de params pagina voor pagina van 50)
##    while 'next' in response.links:
##      #print(response.links['next']['url'])
##      # GET the url pointing to the next page
##      response = session.get(response.links['next']['url'])
##      content_range = response.headers['Content-Range'][6:]
    
##      # add the data from the next page to the data we collected
##      print(content_range)
##      data.extend(response.json())

    print (len(data))
    for project in data:
        # genereer document dictionary
        doc={}
        
        #print(json.dumps(project, indent=4, sort_keys=False))
        doc['provider'] = providerName   
        doc['id'] = project['id']
        doc['uri'] = project['uri']
        doc['naam'] = project['onderwerp']
        doc['uitvoerder'] = project['archeoloog']
        doc['veldwerk_datum'] = project['einddatum_veldwerk'][:10]
        project_id = format(project['id'], '04d')
                              
        # Make a request for project data and store the response
        project_response = session.get(project['uri'], headers=headers)

        if project_response.status_code == requests.codes.ok:
          project_data = project_response.json()
          #print(json.dumps(project_data, indent=4, sort_keys=False))
          doc['created'] = project_data['systemfields']['created_at'][:19]
          doc['updated'] = project_data['systemfields']['updated_at'][:19]
          doc['projecttype'] = project_data['referentietype']['naam']
          doc['rapporttype'] = project_data['rapporttype']
          doc['provincies'] = project_data['archeologierapport']['locatie']['provincies']
          doc['gemeenten'] = project_data['archeologierapport']['locatie']['gemeenten']

          # first coordinates
          point = project_data['archeologierapport']['locatie']['contour']['coordinates'][0][0][0]
          doc['XYlocatie'] = '(' + str(point[0]) + ',' + str(point[1]) + ')'

          doc['projectcodes'] = list()
          projectcodes = []
          for code in project_data['archeologierapport']['projectcodes']:
              if code['uri']:
                  projectcodes.append(code['uri'].split('/')[-1])
          doc['projectcodes'] = list(set(projectcodes))   # remove duplicates

          doc['relaties'] = list()
          relaties = []
          for relatie in project_data['archeologierapport']['nota_uris']:
              if relatie['uri']:
                  relaties.append(relatie['uri'])
          doc['relaties'] = list(set(relaties))   # remove duplicates

          #documenten
          bijlage_lijst = project_data['bijlagen']
          for bijlage in bijlage_lijst:
            #print(json.dumps(bijlage, indent=4, sort_keys=False))
            if bijlage['bijlagetype']['naam'] == 'Verslag van resultaten':  
              #print(bijlage['id'], bijlage['bijlagetype']['naam'], bijlage['url'])
              docurl = bijlage['url'] 
              bijlage_id = format(bijlage['id'], '04d')
              file_naam = bijlage['bestandsnaam']
              
              #authors (samenvoegen)
              auteurs = ""
              for auteur in bijlage['auteurs']:
                if auteur['auteur']:
                  if len(auteurs) > 0:
                    auteurs = auteurs + '|'
                  auteurs = auteurs + auteur['auteur']

              file_headers = {'User-Agent': 'python-requests/2.18.1',
                            'From': 'm.wansleeben@arch.leidenuniv.nl (EXALT)'}                

              if not metadataOnly:
                r = requests.get(docurl, headers=file_headers, stream=True)
                if r.status_code == requests.codes.ok:
                  # document object metadata
                  objf.write (str(doc['id']) + ';' + str(bijlage['id']) + ';"' + file_naam + '";"' + \
                              bijlage['mime'] + '";"' + auteurs + '"' + '\n')
                  # check if pdf or zip file (bijlagen) is returned by request
                  if r.headers['Content-Type'].lower() == 'application/pdf' or \
                     r.headers['Content-Type'].lower() == 'application/zip' or r.headers['Content-Type'].lower() == 'application/x-zip-compressed':
                    outfilenameStr = docsdir + '\\VIOEverslag_' + project_id + '_' + bijlage_id + '_' + file_naam
                    if len(outfilenameStr) > 254:
                      outfilenameStr = outfilenameStr[0:249] + outfilenameStr[-4:]
                    print (outfilenameStr)
                    
                    #download file
                    with open(outfilenameStr, 'wb') as fd:
                      for chunk in r.iter_content(512*1024):
                        fd.write(chunk)
                  else:
                    print ('No pdf or ZIP: '+ docurl)
                    errf.write(str(doc['id']) + ';' + str(bijlage['id']) + ';"' + file_name + '";"";""; "No pdf or ZIP"' + '\n')

                else:
                  print ('Error: '+ docurl)
                  errf.write(str(doc['id']) + ';' + str(bijlage['id']) + ';"' + file_name + '";"";""; "No access"' + '\n')       

        # genereer metadata record
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
                csv_record = csv_record + value.replace("\"","'")
                if values.index(value) < len(values)-1:
                  #print ('|', end='')
                  csv_record = csv_record + '|'
            #print ('"', end='')
            csv_record = csv_record + '"'
          if isinstance(values,str):
            csv_record = csv_record + '"' + values.replace("\"","'") + '"'
          if isinstance(values, (int, float)):
            csv_record = csv_record + str(values)
            
          if csv_columns.index(csv_column) < len(csv_columns)-1:
             #print (';', end='')
             csv_record = csv_record + ';'
        outf.write (csv_record + '\n')   

        i = i + 1

else:
    print ('Web connection Error')

print ('Projects saved: ' + str(i))
#close files
errf.close()
objf.close()
outf.close()     
