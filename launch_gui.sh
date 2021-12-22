#!/bin/bash -e
#Copyright 2018-2019 UC CubeCats
#All rights reserved. See LICENSE file at:
#https://github.com/uccubecats/Helmholtz-Cage/LICENSE
#Additional copyright may be held by others, as reflected in the commit history.

RELATIVE_PATH="`dirname \"$0\"`"
ABSOLUTE_PATH="`( cd \"$RELATIVE_PATH\" && pwd )`"
cd $ABSOLUTE_PATH/helmholtz_cage
echo "Launching Helmholtz Cage control GUI..."
python3 app.py

