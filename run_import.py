#!/usr/bin/env python
# coding: utf-8

# import libraries
import yaml
import utilities

# get config
config = yaml.safe_load(open("config.yml"))

print(config['data_source'])

