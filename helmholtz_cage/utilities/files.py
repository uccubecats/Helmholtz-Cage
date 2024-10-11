"""
A module for commonly reused functions.

Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import csv
import os


def read_from_csv(file_path, file_name):
    """
    Read and return the contents of a csv file.
    
    TODO: Test
    """
    
    # Set starting directory
    start_dir = os.getcwd()
    
    try:
        
        # Go to the given path
        os.chdir(file_path)
        
        # Retrieve the contents of the csv file
        content = []
        with open(file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                content.append(row)
        
        return content
        
    finally:
        
        # Go back to the starting directory
        os.chdir(start_dir)

def write_to_csv(file_path, file_name, content, mode):
    """
    Write formated content to csv file.
    
    TODO: Test
    """
        
    # Set starting directory
    start_dir = os.getcwd()
    
    try:
        
        # Go to the given path
        os.chdir(file_path)
        
        # Write content to file
        with open(file_name, mode, newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in content:
                csv_writer.writerow(row)
        
    finally:
        
        # Go back to the starting directory
        os.chdir(start_dir)   
        
