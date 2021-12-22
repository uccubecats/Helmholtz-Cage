#!/usr/bin/env python

"""
Help page GUI code for the UC Helmholtz Cage

Copyright 2018-2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.

Note: WIP
"""


import tkinter as tk


class HelpPage(tk.Frame):
    """
    TODO
    """
    
    def __init__(self, parent, controller):
        
        
        tk.Frame.__init__(self, parent)
        
        ## Controller allows HelpPage to access things from CageApp class
        self.controller = controller
        
        # Main container to hold all subframes
        container = tk.Frame(self, bg="black")
        container.grid(sticky="nsew")
