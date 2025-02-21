#!/usr/bin/env python3

"""
Script to TEST chron
"""

# * * * * * conda activate agnes-bert-file-import; python3 /home/alex/surfdrive/AGNES-system/file-source-import/onroerend_erfgoed/onroerend_erfgoed_TEST.py


import logging
import sys
from datetime import datetime

# import common functions
sys.path.insert(1, '../')
import common

# set name of module, to fetch info from config
module_name = "onroerend_erfgoed"

# get info from config file
config = common.get_config()
        
log_location = config['data_source'][module_name]['harvest_log_location']

now = datetime.now()
date = now.strftime("%Y-%m-%d")

logfile = f"{log_location}harvest-log-onroerend-erfgoed-{date}.log"
logging.basicConfig(level=logging.DEBUG, filename=logfile, filemode="a+",
                format="%(asctime)-15s %(levelname)-8s %(message)s")
logging.info("test")


print('Ran successfully')
