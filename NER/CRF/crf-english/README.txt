READ ME
This folder contains the following folders:
.ipynb_checkpoints - backups of the code
component pieces  - in here it has sections of code that might be useful on their own. 
			- jsonl2pos-and-bio - convert jsonl files to POS and bio
			- Text split for multiple documents - this splits the code into a set percentage if there are multiple files and outputs them combined. 
			- TSV converter - to convert TSV to CSV
			- English-dont change anything - just for running tests - this is the origional code. Made to ensure that I always have a backup of it. Few issues such as printing the label, but its not too bad

english-jsonl - This is the folder to put the JSONL in
no-tables 	- This folder contains all of the files that dont have tables. This is subdivided into:
		- no_tables.jsonl - this is the file outputted when removing the tables - this is then split into the following chunks
		Test splitting		1		2		3		4		5		6		7		8		9	
			  		Train	Test	Train	Test	Train	Test	Train	Test	Train	Test	Train	Test	Train	Test	Train	Test	Train	Test
			10	10	yes		yes		yes		yes		yes		yes		yes		yes		yes	
			20	10		yes	yes		yes		yes		yes		yes		yes		yes		yes	
			30	10				yes	yes		yes		yes		yes		yes		yes		yes	
			40	10						yes	yes		yes		yes		yes		yes		yes	
			50	10								yes	yes		yes		yes		yes		yes	
			60	10										yes	yes		yes		yes		yes	
			70	10												yes	yes		yes		yes	
			80	10														yes	yes		yes	
			90	10																yes	yes	
			100	10																		yes
		
		- bio - this folder contains all the bio folders when splitting the data
			- split0 - this is defined in the JSONL_to_split_txt_files_without_tables_with_POS file
			- splits 1-9 -  this contains all the bio files split into increasing segments. This is defined in the table above.
		- JSONL - see notes on bio folder, yet this is the split jsonl files
		- txt   - see notes on bio folder, yet this is the split txt files

ontologies - these are where associated ontologies are stored. Currently there is Context, Evidence, Materials, Periods, Taxon and species vernacular names. these files are called accordingly
txt - example txt files



And the following files:
English-for all files in folder - this trains the NER for all the splits defined above
English-for all files in folder-with 2x2 - expansion of above file but with 2 words before, after and sorrounding 
JSONL_to_split_txt_files_without_tables_with_POS - this code splits the origionally downloaded from docano annotations into text files with the above splits, as well as give it all POS tags. 
README - this file
tagtable-English-2022 - list of the tags for the POS. 
Train NER - this is the code to use for one test and one train document. 



How to get the scripts working:
1)Download JSONL from docano put in 
2)Run the JSONL_to_split_txt_files_without_tables_with_POS to create split text files
3)Run Train NER - just to see if the script will give you a proper result as expected
4)Run English-for all files in folder - see if all the split files work and to make a graph of the results
5)Run English-for all files in folder-with 2x2 - see if this increases the F1 in each
6)Look in ontologies, are there elements needed to improve overall score



Developed to work with English texts. It could work in other languages, contexts and such like.
 