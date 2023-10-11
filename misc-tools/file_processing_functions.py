from nltk.classify.textcat import TextCat
import xml.etree.ElementTree as ET
import os
import slate3k
from pathlib import Path
from zipfile import ZipFile

folder = os.listdir(os.path.dirname(__file__)) #huidige folder

#function 1: functie die een PDF aanneemt, en de plain text er uit haalt en returned
def PDFtoTXT(pdfFile):
    name = str(pdfFile).replace(".pdf", "")
    #print("Now converting " + str(name) + "...")
    with open(pdfFile, "rb") as pdf:
        doc = slate3k.PDF(pdf) #creates a list containing all pages as strings
    pdf.close()

    doc_split = []
    for page in doc:
        doc_split.append(page)
    doc = "\r\r".join(doc_split) #by splitting and rejoining the list, all "\n" and "\r" tags are filtered out 
    doc = doc.replace("\r\r", "\r" + "".center(100,"=") + "\r") #seperates pages with "===============================..."

    return doc
    """
    with open(str(name) + "(pdf).txt", "w", encoding="utf-8") as f:
        f.write(doc) #writing pdf text to a .txt file
    f.close()
    """
    #print("Written " + str(name) + "(pdf).txt!\n")

#function 2: functie die een XML aanneemt, en de plain text er uit haalt en returned
def XMLtoTXT(XmlFile):
    name = str(XmlFile).replace(".xml", "")
    #print("Now converting " + str(name) + "...")

    tree = ET.parse(XmlFile)
    root = tree.getroot() #creates an XML tree of the file

    text = ""
    for elem in root.iter():
        if elem.text != None:
            text = text + str(elem.text) + "\n"
    return text

    """
    with open(str(name) + "(xml).txt", "w", encoding="utf-8") as txt:
        for elem in root.iter():
            if elem.text != None:
                txt.write(elem.text + "\n") #writes all items in the tree that contain text
    txt.close()
    """

#function 3: functie die plain text aanneemt, en de language code returned
def DetectLanguage(TxtFile):
    with open(TxtFile, "r", encoding="utf-8") as f:
        text = str(f.readlines()) #using a simple NLTK TextCat module to guess the language
    f.close()
    return TextCat().guess_language(text)
    #print(str(TxtFile) + " is written in:   " + str(TextCat().guess_language(text)))

#function 4: functie die een .doc(x) aanneemt en de plain text returned
def DOCtoXML(DocFile):
    if DocFile.endswith(".docx"): # Removing the .doc(x) extension
        name = str(DocFile).replace(".docx", "(docx).zip")
    else:
        name = str(DocFile).replace(".doc", "(doc).zip")
    D = Path(str(DocFile))
    D.rename(name) #changes .doc file to .zip file
    name2 = str(name).replace(".zip", "")
    with ZipFile(name, "r") as zip:
        ExFile = zip.extract("word/document.xml")   #extract a temporary .xml file with the document text
        XMLFile = str(name2) + ".xml"
        os.rename(ExFile, XMLFile)
        XMLtoTXT(XMLFile)
        os.remove(XMLFile) #deletes the temporary .xml file    
    
#Calling the functions:
for file in folder:
    if file.endswith(".pdf"):
        PDFtoTXT(file)
    if file.endswith(".xml"):
        XMLtoTXT(file)

for textfile in folder:
    if textfile.endswith(".txt"):
        DetectLanguage(textfile)


#prints
#return in plaats van print of write
