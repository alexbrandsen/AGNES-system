import requests
import xml.etree.ElementTree as et
from datetime import date, timedelta

#web_url = 'https://archis.cultureelerfgoed.nl/zoekenenvinden//24KM-HNTZ-UUZT-D7AB#/zaak/search/(zaak:(fields:('*':'2453800100')))'

basedir = 'J:\\Workgroups\\ARCH\\EDNA\\projecten_wansleeben\\projecten\\Archis_rapporten_2023\\'
#basedir = 'C:\\tijd\\Archis3'
metadir = basedir + '\\metadata2'
docsdir = basedir + '\\docs2'
outputfile = metadir + '\\zaakdocumenten_metadata.csv'
objectsfile = metadir + '\\zaakdocumenten_fileobjects.csv'
errorfile = metadir + '\\zaakdocumenten_errorlog.csv'
outf = open(outputfile, 'w', encoding='utf-8')
objf = open (objectsfile, 'w', encoding='utf-8') 

csv_columns = ('document_id','zaakidentificatie','zaak_id','identificatie','archis2_rapportmeldingsnr','auteur','titel','reeks','volgnr','jaar','link','externe_link', 'status_zaak')

url = 'https://archis.cultureelerfgoed.nl/zoekenenvinden//zaak/download'
headers = {'Accept': 'application/xml',
           'Content-Type': 'application/json;charset=utf-8',
           'User-Agent': 'python-requests/2.18.1',
           'From': 'm.wansleeben@arch.leidenuniv.nl (EXALT)'}
# personal access code | time stamp (irrelevant)
cookies = {'toegangscode':'24KM-HNTZ-UUZT-D7AB|2023-09-29T13:50:42.968+02:00'}

# search terms in the search box endup in: fields (OR is possible)
# subsequent search terms (AND) endup in: facets
json0 = {'fields':{'zaakidentificatie':'2453800100'},'format':'xml','notiming':True,'page':1,'size':1000,'view':'zaak'}
json1 = {'fields':{'plaats':'leiderdorp'},'format':'xml','size':1000,'page':1}
json2 = {'fields':{'zaakidentificatie':'2453800100 or 2001869100'},'format':'xml','page':1,'size':1000,'view':'zaak'}
json3 = {'facets':{'vondstlocaties.chos.materiaal':['materialen~metaal~brons']},'fields':{'gemeente':'Leiderdorp'},'format':'xml','page':1,'size':1000,'view':'zaak'}

# json = {'download':true,'facets':{'vondstlocaties.chos.queryFields':{'fields':['vondstlocaties.chos.materiaal_label','vondstlocaties.chos.materiaal_code',\
# 'vondstlocaties.chos.materiaal_search'],'query':'brons'},'vondstlocaties.chos.gemeente':['Leiderdorp']},'fields':{},'format':'xml','notiming':true,'page':1,'size':1000,'view':'zaak'}

# de meldingsdatum is aanmelding, (af)melding is eerste bevindingen of afmelding
# zit in facet status_zaak: er moet dus (waarschijnlijk) voor elke dag een query zijn...
# json = {'facets':{'status_zaak':['Onderzoek afgemeld op 27-09-2023']},'fields':{},'format':'xml','page':1,'size':1000,'view':'zaak'}

start_date = date(2023, 10, 2)
end_date = date(2023, 10, 8)
delta = timedelta(days=1)
while start_date <= end_date:
    query_date = start_date.strftime("%d-%m-%Y")
    json = {'facets':{'status_zaak':['Onderzoek afgemeld op '+ query_date]},'fields':{},'format':'xml','page':1,'size':1000,'view':'zaak'}

    response = requests.post(url, headers=headers, json=json, cookies=cookies)
    #print (response.status_code)
    #print (response.text)

    if response.status_code == requests.codes.ok:
      contentType = response.headers['content-type']
      #print (contentType)
      # returns: application/xml;charset=windows-1252, xml header contains UTF-8

      if contentType.startswith('application/xml'):
        # reponse contains (invalid) characters like Word quotes \u201C en \u201D en (long) dashes (-)
        #print (type(response.content))
        #response.content = response.content.replace(b'\u201C',b'\'').replace(b'\u201D',b'\'')
        
        utf_response = response.text.encode(encoding='Windows-1252', errors='ignore').decode('UTF=8', errors='ignore')
        utf_response = utf_response.replace('\u201C','\'').replace('\u201D','\'')
        
        # undefined namespace error
        #utf_response = utf_response.replace(b'search:took', b'search_took')
        utf_response = utf_response.replace('search:took', 'search_took')
        xml_response = et.fromstring(utf_response)
        aantal = xml_response.find('total')
        print ('On ' + query_date + ', response hits: '+ aantal.text)
        hits = xml_response.findall('hits')
        #print len (hits)
        i = 0
        
        for hit in hits:
          zaakidentificatie = hit.find('fields/zaakidentificatie').text
          zaakstatus = hit.find('fields/status_zaak').text
          gemeente = hit.find('fields/gemeente').text
          plaats = hit.find('fields/plaats').text
          if plaats == 'null': plaats = ''
          # toponiem is leeg, wel waarde in fields/vondstlocaties/vondstlocatie/toponiem
          toponiem = hit.find('fields/toponiem').text
          if toponiem == 'null': toponiem = ''
          onderzoeksnaam = hit.find('fields/onderzoeksnaam').text
          if onderzoeksnaam == 'null': onderzoeksnaam = ''
            
          print (zaakidentificatie, gemeente, plaats, toponiem, onderzoeksnaam)
          zaakdocumenten = hit.findall('fields/zaakdocuments')

          for zaakdocument in zaakdocumenten:
            # genereer document dictionary
            doc={}

            document_id = zaakdocument.find('document_id').text
            # document_id null zijn eerste bevindingen
            if document_id != 'null':
              doc['document_id'] = int(document_id)
            else:
              doc['document_id'] = None  
            doc['zaakidentificatie'] = zaakidentificatie
            doc['zaak_id'] = int(zaakdocument.find('zaak_id').text)
            doc['identificatie'] = zaakdocument.find('identificatie').text
            archis2nr = zaakdocument.find('archis2_rapportmeldingsnr').text.strip()
            if archis2nr != 'null':
              doc['archis2_rapportnr'] = int(archis2nr)
            else:  
              doc['archis2_rapportnr'] = None
            auteur = zaakdocument.find('auteur').text.strip()
            if auteur == 'null': auteur = ''
            doc['auteur'] = auteur
            titel = zaakdocument.find('titel').text.strip()
            if titel =='null': titel = ''
            doc['titel'] = titel
            reeks = zaakdocument.find('reeks').text.strip()
            if reeks =='null': reeks = ''
            doc['reeks'] = reeks
            volgnr = zaakdocument.find('volgnr').text.strip()
            if volgnr == 'null': volgnr = ''
            doc['volgnr'] = volgnr
            jaar = zaakdocument.find('jaar').text.strip()
            if jaar == 'null': jaar = ''
            doc['jaar'] = jaar
            link = zaakdocument.find('link').text.strip()
            if 'archisarchief' in link:
                doc['link'] = link
            else:
                doc['link'] = ''
            externe_link = zaakdocument.find('externe_link').text.strip()
            if externe_link == 'null': externe_link = ''
            doc['externe_link'] = externe_link
            doc['status_zaak'] = 'Onderzoek afgemeld op ' + query_date
            
            if doc['document_id'] and doc['link']:
              # genereer metadata records
              csv_record = ''
              for csv_column in csv_columns:
                values = doc.get(csv_column, '')
                #print ('"' + values + '"', end='')
                if isinstance(values,str):
                  csv_record = csv_record + '"' + values + '"'
                if isinstance(values, (int, float)):
                  csv_record = csv_record + str(values)
                 
                if csv_columns.index(csv_column) < len(csv_columns)-1:
                  #print (';', end='')
                  csv_record = csv_record + ';'

              outf.write (csv_record + '\n')
              #print(csv_record)
              objf.write('"' + zaakidentificatie +'";"'+ link+'";'+ query_date +'\n')
              i = i + 1
          
      else:
        print ('Error: the response is not a XML file')
    else:
      print('Error: no proper response')

    print ('Aantal zaakdocumenten: ' + str(i))
    print ('')
    #next day
    start_date = start_date + delta

#close files
#errf.close()
objf.close()
outf.close()  
