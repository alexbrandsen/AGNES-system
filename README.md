# AGNES-system

AGNES stands for Archaeological Grey-literature Named Entity Search, and is an indexing and search system designed to make Dutch archaeological excavation reports more accessible. The online version can be found at [https://agnessearch.nl](https://agnessearch.nl).

## Contents

This repository contains the [documentation](documentation) and all the code needed to recreate this system. The structure is as follows:

- [requirements.txt](requirements.txt) contains all the Python requirements
- [config.yml](config.yml) contains the configuration for the system (see documentation for more info)
- [file-source-import](file-source-import) contains the code needed to harvest documents from an API endpoint, apply NER with BERT, and output JSON/HTML ready to be sent to the webserver
- [webserver-files](webserver-files) contains the code that is needed on the webserver
- [results-post-processing](results-post-processing) contains Excel worksheets to further process and filter the output of the CSV export function
- [misc-tools](misc-tools) contains some scripts to convert between file formats, get website analytics, and extract coordinates (not currently used in AGNES)
- [NER](NER) contains old - currently not used - CRF models and code to do NER (replaced with BERT now)


