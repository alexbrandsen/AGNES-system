# Documentation

## Requirements and Installation

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

#### Install
- Install OS (Ubuntu/CentOS preferred)
- Install Apache and set up a domain and host
- Install PHP
- Install Python3
- Install ElasticSearch
- Create an index in ElasticSearch
- Open file /webserver-files/create-mapping.txt, edit the index name to match your chosen index name, then copy and run the command on your webserver
- Copy files from /webserver-files/html/ to your html folder
- Edit the file index.php; update the logo, text, design, etc, to match your own project
- Copy /webserver-files/upload-json-to-elasticsearch.py to a (non public / non www) folder somewhere on your webserver
		
		
Processing Machine
	
	Requirements:
	
	Cron setup
		Copy Conda section from ~/.bashrc to a new file called ~/.bashrc_conda
		Add the following 2 lines to cron using 'crontab -e':
			SHELL=/bin/bash
			BASH_ENV=~/.bashrc_conda
		Now add a cron line for each source you want to import, below example runs on midnight on Sunday, every week:
			0 0 * * 0 cd /path/to/source/; conda activate your_env; python3 /path/to/source/import.py; conda deactivate
		