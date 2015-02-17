#!/usr/bin/env bash

# setup ROOT (CMSSW or check for local)

# download python modules
export vpython=external/vpython

cd external/virtualenv

echo "Creating virtual python environment in $vpython"
if [ ! -d "$vpython" ]; then
  python virtualenv.py --distribute $vpython
else
  echo "...virtual environment already setup."
fi

echo "Activating virtual python environment"
cd $vpython
source bin/activate

echo "Installing yolk"
pip install -U yolk
echo "Installing ipython"
pip install -U ipython
echo "Install progressbar"
pip install -U progressbar
#echo "Installing argparse"
#pip install -U argparse
