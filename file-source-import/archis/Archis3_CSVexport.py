import os, requests, csv
from bs4 import BeautifulSoup

archisCSVfile = 'J:\\Workgroups\\ARCH\\EDNA\\projecten_wansleeben\\projecten\\Archis_rapporten_2023\\metadata2\\zaakdocumenten_fileobjects.csv'
docsdir = 'J:\\Workgroups\\ARCH\\EDNA\\projecten_wansleeben\\projecten\\Archis_rapporten_2023\\docs2'
pos = archisCSVfile.rfind('\\')
outputfile = archisCSVfile[0:pos] + '\\zaakbestanden_wk40_2023.csv'
errorfile = archisCSVfile[0:pos] + '\\file_errorlog_wk40_2023.csv'
outf = open(outputfile, 'w', encoding='utf-8')
errf = open(errorfile, 'w', encoding='utf-8')

# Certificate verification failed on: Max retries exceeded
requests.urllib3.disable_warnings()

with open(archisCSVfile, newline='') as csvfile:
   csvreader = csv.reader(csvfile, delimiter=';', quotechar='\"')
   for row in csvreader:
     # csv: zaakidentificatie, url
     print (row[0], row[1])
     zaakId = row[0]
     url = row[1]
     # zonder certificate verification
     webpage = requests.get(url, verify=False)

     if webpage.status_code == requests.codes.ok:
       data = webpage.text
       soup = BeautifulSoup(data, 'html.parser')

       for link in soup.find_all('a'):
         filenameStr = link.get('href')
         filenameStr = filenameStr.replace('"', '\"')
         
         if url[-1] == '/':
            docUrl = url + filenameStr
         else:
            docUrl = url + '/' + filenameStr
         outf.write('\"' + zaakId + '\";\"' + filenameStr + '\"\n')

         # bepaal extensie
         extpos =  filenameStr.rfind('.')
         ext = filenameStr[extpos:]
             
         # skip afmeldingsbevestiging Archis3
         if not filenameStr.lower() == "veldwerk_" + zaakId.strip() + '.pdf':
          # skip all niet pdf-files
          if ext == '.pdf':
           
           doc = requests.get(docUrl, verify=False, stream=True)
           if doc.status_code == requests.codes.ok:

             #if url.find('/Archis2/') >= 0: 
             #  outfilenameStr = docsdir + '\\Z' + zaakId[0:7] + '_' + filenameStr
             #else:

             outfilenameStr = docsdir + '\\Z' + zaakId[0:7] + '_' + filenameStr
             if len(outfilenameStr) > 254:
               # outfilenameStr = outfilenameStr[0:239] + '.pdf'
               outfilenameStr = outfilenameStr[0:239] + ext
               
             with open(outfilenameStr, 'wb') as fd:
               for chunk in doc.iter_content(512*1024):
                 fd.write(chunk)
           else:
             print ('Error: ' + docUrl)
             errf.write("document " + zaakId + " " + docUrl + '\n')

     else:
       print ('Error: ' + url)
       errf.write("zaakurl  " + zaakId + " " + url + '\n')

outf.close()
errf.close()
