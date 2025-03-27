# Documentation

This document gives an overview of the AGNES system, and how to replicate the software for your own purposes. 

## Requirements and Installation

We first start by listing the requirements and how to install all the software. Be aware that 2 machines are needed: a webserver to hold the ElasticSearch index and serve the frontend, and a processing machine for doing the NER and pre-processing. See the below image for an overview of the intended workflow:

![AGNES architecture](agnes-architecture.png "AGNES architecture")


### Webserver
	
#### Requirements
Depends to some extent on the size of the index, so the number of documents you are indexing. The requirements below will need to be scaled up depending on your corpus.

Minimal:
- 2 (v)CPU cores
- 2GB (v)RAM
- 200GB storage (mainly for HTML previews, see section below)
	
AGNES current specs, for 180.000 documents:
- 6 vCPU cores
- 8GB vRAM
- 2TB storage

#### Installation
- Install OS (developed on CentOS, should work on any Linux flavour. Windows is untested: here be dragons)
- Install Apache and set up a domain and host
- Install PHP
- Install Python3
- Install ElasticSearch
- Create an index in ElasticSearch
- Open file /webserver-files/create-mapping.txt, edit the index name to match your chosen index name, then copy and run the command on your webserver
- Copy files from /webserver-files/html/ to your html folder
- Edit the file index.php; update the logo, text, design, etc, to match your own project
- Copy /webserver-files/upload-json-to-elasticsearch.py to a (non public / non www) folder somewhere on your webserver
		
		
### Processing Machine
This is the machine where the documents are harvested from the archives, and the NER is performed with BERT. This machine then produces HTML and JSON files, which are sent to the webserver for indexing.
	
#### Requirements
Requirements are flexible, and not fully tested. At a minimum, you will need:
- Your preferred flavour of Linux
- 32GB or RAM
- A decent processor, doesn't have to be latest/fastest
- About 1 TB diskspace, largely dependent on the number of documents you are indexing
- A GPU that can handle the ArcheoBERTje-NER model, probably most will work, but this is not tested

AGNES processing machine current specs:
- Ubuntu 22.04.5 LTS Desktop
- 64GB RAM
- Intel i9-14900K
- NVIDIDA GeForce RTX 4090
	
#### Installation



Config via YAML
	
Cron setup:
- Copy Conda section from ~/.bashrc to a new file called ~/.bashrc_conda
- Add the following 2 lines to cron using 'crontab -e':
	- SHELL=/bin/bash
	- BASH_ENV=~/.bashrc_conda
- Now add a cron line for each source you want to import, below example runs on midnight on Sunday, every week:
	- 0 0 * * 0 cd /path/to/source/; conda activate your_env; python3 /path/to/source/import.py; conda deactivate
		