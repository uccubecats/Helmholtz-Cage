"""


Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.
"""


import csv
import os


def read_csv(file_path, file_name):
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
        with open(file_name) as csv_file:
            csv_content = csv.reader(csv_file)
        
        return csv_content
        
    finally:
        
        # Go back to the starting directory
        os.chdir(start_dir)

def write_csv(file_path, file_name, content):
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
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in csv_file:
                csv_writer.writerow(row)
        
    finally:
        
        # Go back to the starting directory
        os.chdir(start_dir)
