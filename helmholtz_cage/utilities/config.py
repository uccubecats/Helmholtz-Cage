#!/usr/bin/env python

"""
  Functions for retrieving and storing system configuration information.
  
  Copyright 2022 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import json
import os


def retrieve_configuration_info(main_path):
    """
    
    """
    
    # Get path-file name
    config_path = os.path.join(main_path, "config.json")
    
    # Retrieve config file contents
    with open(config_path) as json_file:
        content = json.load(json_file)
    
    #TODO: add some sanity checks?
    
    return content
