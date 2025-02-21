import requests
import re
import os
import pandas as pd

def remove_html_tags(text):
    #Remove html tags from a string
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def CSV_extract(url, pdf_download_folder, pdf_download_prefix):
    """
    CSV_extract extracts a .csv file from a webpage, filters it by language and keywords parameters, and automatically downloads .pdf files from it to a specific folder.
    :param url: the url of the .csv
    :param pdf_download_folder: the folder in which the downloaded .pdfs are stored.
    :param pdf_download_prefix: the first part of the download url that all .pdf files share 
    :return: a string of the header of the .csv file, and all newly downloaded .pdfs. This returns all the records that have been added to the .csv after the last run. 
    """
    #extract .csv from url
    r = requests.get(url, allow_redirects=True)
    
    #cleans .csv and adds a line break
    cleanText = r.content.decode('utf-8')
    cleanText = cleanText.replace("\r", "").replace("\n", "").replace("\r", "").replace("\t", "")
    cleanText = cleanText.replace("<br />", "\n")


    with open("sidestone.csv", "w", encoding="utf-8") as f:
        f.write(remove_html_tags(cleanText.replace("@", "\t"))) #remove html tags from .csv file, and writes cleaned string to a temporary .csv file


    #- Converts .csv to a Pandas dataframe
    df = pd.read_csv("sidestone.csv", sep="\t")

    # Filter parameters for the language and keywords columns:
    lang_options = ["English", "Dutch", "German"]
    key_options = ["archaeology", "archeologie", "archäologie", "archaeo", "archeo"]

    NewDF = df.dropna(axis = 0, subset="keywords") #drop all records with no keywords
    print(NewDF)

    #drop all records not written in languages in lang_options: 
    for record in NewDF["language"]:
        if not any(option in record for option in lang_options):
            NewDF.drop(NewDF.loc[NewDF["language"]==record].index, inplace=True)
    
    #drop all records without keywords that are in key_options:
    for record in NewDF["keywords"]:
        if not any(option in record.lower() for option in key_options):
            NewDF.drop(NewDF.loc[NewDF["keywords"]==record].index, inplace=True)
    

    #save filtered dataframe as a .csv to a temporary file:
    NewDF.to_csv("sidestone_filtered.csv", index=False)


    with open("sidestone_filtered.csv", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        not_yet_downloaded = [lines[0]] #header
        
        for p in lines[1:]:
            file_url = p[p.find(pdf_download_prefix):] #for each record, find the download url
            file_name = file_url[32:]

            if file_name in os.listdir(pdf_download_folder):
                #print message for already downloaded file
                print(str(file_name) + " already in " + str(pdf_download_folder))
            else:
                #download new record and save it as pdf:
                r = requests.get(file_url, allow_redirects=True)
                with open(str(pdf_download_folder) + "/" + str(file_name), 'wb') as b:
                    b.write(r.content)
                not_yet_downloaded.append(p) #create list of all newly downloaded files

    #remove temporary .csv files:
    os.remove("sidestone_filtered.csv")
    os.remove("sidestone.csv")

    return "\n".join(str(record) for record in not_yet_downloaded) #returns list of newly downloaded files as a string
